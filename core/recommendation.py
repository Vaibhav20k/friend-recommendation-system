"""Friend recommendation engine module.

Responsible for:
- Finding friends-of-friends (depth 2 connections).
- Filtering out direct friends and self.
- Calculating mutual friend counts and intersection sets.
- Ranking candidates in descending order of mutual friend counts.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from core.graph import SocialGraph


def get_friend_recommendations(
    graph: SocialGraph,
    user_id: str,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Compute ranked friend recommendations based on mutual friend counts.

    Explores 2-hop connections (friends-of-friends) in the social network graph,
    filters out the query user and their existing direct friends, aggregates mutual
    friends for each candidate, and ranks candidate users descending by mutual friend
    count. Ties in mutual count are broken alphabetically by user ID.

    Algorithm:
        1. Existence Check: Verify if `user_id` exists in `graph`. If not, return [].
        2. Direct Friends: Fetch `direct_friends = graph.get_friends(user_id)`.
           If `direct_friends` is empty, return [].
        3. 2-Hop Traversal & Mutual Tracking:
           For each direct friend `f` in `direct_friends`:
               For each `candidate` in `graph.get_friends(f)`:
                   If `candidate == user_id` or `candidate in direct_friends`:
                       continue  # Exclude self and direct friends
                   Track mutual friend `f` for `candidate`.
        4. Mutual Count & Structure:
           For each candidate, calculate `mutual_count = len(mutual_friends)`.
           Store candidate ID, mutual count, and sorted list of mutual friends.
        5. Candidate Ranking:
           Sort candidates descending by `mutual_count`, with ties broken
           alphabetically by `candidate_id` in ascending order:
           key = (-mutual_count, candidate_id).
        6. Limit Application:
           If `limit` is provided and > 0, truncate to the top `limit` items.
           If `limit` is provided and <= 0, return [].
           If `limit` is None, return all ranked recommendations.

    Complexity Analysis:
        - Traversal Complexity (before sorting):
          O(sum_{f in direct_friends} deg(f)).
          Each direct friend `f` is inspected, and their degree `deg(f)` neighbors
          are traversed. Set lookups (`candidate in direct_friends`) and insertions
          run in O(1) average time via hash table lookups.
          In the worst case, this traversal is bounded by O(|E|), where |E| is the
          number of edges in the graph.
        - Sorting Complexity:
          O(C log C), where C is the number of unique 2-hop candidate users (C <= |V|).
          Sorting the mutual friends list for each candidate takes O(M_c log M_c),
          where M_c <= deg(user_id).
        - Total Time Complexity:
          O(sum_{f in direct_friends} deg(f) + C log C) average case, bounded by
          O(|V| + |E| + C log C).
        - Space Complexity:
          O(F + C * M) auxiliary space, where F is the number of direct friends and
          M is the average mutual friend count per candidate, bounded by O(|V| + |E|).

    Args:
        graph: The SocialGraph instance representing the social network.
        user_id: Unique string identifier of the user seeking recommendations.
        limit: Optional maximum number of recommendations to return.
               If provided and > 0, returns top `limit` recommendations.
               If provided and <= 0, returns an empty list.
               If None, returns all eligible recommendations.

    Returns:
        List[Dict[str, Any]]: A ranked list of recommendation dictionaries:
            [
                {
                    "user_id": candidate_id,
                    "mutual_count": int,
                    "mutual_friends": List[str]  # Sorted alphabetically
                },
                ...
            ]
        Returns an empty list [] if user does not exist, has no direct friends,
        or has no candidate friends-of-friends.
    """
    if not isinstance(user_id, str):
        return []
    user_id = user_id.strip()
    if not graph.has_user(user_id):
        return []

    direct_friends: Set[str] = graph.get_friends(user_id)
    if not direct_friends:
        return []

    candidate_mutuals: Dict[str, Set[str]] = defaultdict(set)

    for f in direct_friends:
        for candidate in graph.get_friends(f):
            if candidate == user_id or candidate in direct_friends:
                continue
            candidate_mutuals[candidate].add(f)

    if not candidate_mutuals:
        return []

    recommendations: List[Dict[str, Any]] = [
        {
            "user_id": candidate_id,
            "mutual_count": len(mutual_set),
            "mutual_friends": sorted(mutual_set),
        }
        for candidate_id, mutual_set in candidate_mutuals.items()
    ]

    # Rank candidates descending by mutual_count, breaking ties alphabetically by candidate_id
    recommendations.sort(key=lambda item: (-item["mutual_count"], item["user_id"]))

    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            return []
        return recommendations[:limit]

    return recommendations


def get_mutual_friends_details(
    graph: SocialGraph,
    user_u: str,
    user_v: str,
    user_manager: Optional[Any] = None,
) -> Dict[str, Any]:
    """Calculate detailed mutual friends information between two specific users.

    Computes the set intersection of neighbors between user_u and user_v. If a
    UserManager instance is provided, enriches each mutual friend ID with their
    human-readable display name.

    Args:
        graph: The SocialGraph instance.
        user_u: String identifier of the first user.
        user_v: String identifier of the second user.
        user_manager: Optional UserManager instance for name resolution.

    Returns:
        Dict[str, Any] containing:
            - user_u: Sanitized string ID of first user.
            - user_v: Sanitized string ID of second user.
            - are_friends: Boolean indicating direct friendship status.
            - mutual_count: Integer count of common friends.
            - mutual_friends: Sorted list of common friend user IDs.
            - mutual_friends_detailed: List of dicts with {"id": uid, "name": name}.
    """
    if not isinstance(user_u, str) or not isinstance(user_v, str):
        return {
            "user_u": str(user_u) if user_u is not None else "",
            "user_v": str(user_v) if user_v is not None else "",
            "are_friends": False,
            "mutual_count": 0,
            "mutual_friends": [],
            "mutual_friends_detailed": [],
        }

    user_u = user_u.strip()
    user_v = user_v.strip()

    if not user_u or not user_v or not graph.has_user(user_u) or not graph.has_user(user_v):
        return {
            "user_u": user_u,
            "user_v": user_v,
            "are_friends": False,
            "mutual_count": 0,
            "mutual_friends": [],
            "mutual_friends_detailed": [],
        }

    are_friends = graph.are_friends(user_u, user_v)
    friends_u = graph.get_friends(user_u)
    friends_v = graph.get_friends(user_v)
    mutual_set = friends_u.intersection(friends_v)
    mutual_friends = sorted(mutual_set)

    detailed = []
    for uid in mutual_friends:
        name = f"User {uid}"
        if user_manager is not None:
            user_record = user_manager.get_user(uid)
            if user_record and "name" in user_record:
                name = user_record["name"]
        detailed.append({"id": uid, "name": name})

    return {
        "user_u": user_u,
        "user_v": user_v,
        "are_friends": are_friends,
        "mutual_count": len(mutual_friends),
        "mutual_friends": mutual_friends,
        "mutual_friends_detailed": detailed,
    }


