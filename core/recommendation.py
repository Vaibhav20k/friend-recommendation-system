"""Friend and peer recommendation engine module for CampusConnect.

Responsible for:
- Finding friends-of-friends (depth 2 connections).
- Filtering out direct friends and self.
- Calculating mutual friend counts and intersection sets.
- Calculating Jaccard similarity of student interest profiles:
    J(A, B) = |Interests(A) ∩ Interests(B)| / |Interests(A) ∪ Interests(B)|
- Hybrid ranking: Mutual friends count (primary) -> Jaccard similarity (secondary) -> Name tie-breaker.
- Producing human-readable recommendation explanations.
- Filtering candidates by department/branch or year of study.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from core.graph import SocialGraph


def calculate_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Calculate the Jaccard similarity coefficient between two sets of tags.

    Formula:
        J(A, B) = |A ∩ B| / |A ∪ B|

    Special Cases:
        - If both sets are empty, returns 0.0.

    Args:
        set_a: First set of string tags.
        set_b: Second set of string tags.

    Returns:
        Float similarity score between 0.0 and 1.0, rounded to 3 decimal places.
    """
    if not set_a or not set_b:
        return 0.0
    intersection_len = len(set_a.intersection(set_b))
    union_len = len(set_a.union(set_b))
    if union_len == 0:
        return 0.0
    return round(intersection_len / union_len, 3)


def get_friend_recommendations(
    graph: SocialGraph,
    user_id: str,
    limit: Optional[int] = None,
    user_manager: Optional[Any] = None,
    same_branch_only: bool = False,
    same_year_only: bool = False,
    branch_filter: Optional[str] = None,
    year_filter: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Compute ranked friend recommendations based on mutual friends and Jaccard interest similarity.

    Explores 2-hop connections (friends-of-friends) in the social network graph,
    filters out the query student and existing direct friends, computes mutual friend
    intersections, calculates Jaccard similarity of interest tags, and ranks candidate
    students descending by:
        1. mutual_count (primary)
        2. jaccard similarity (secondary)
        3. student display name / ID (tie-breaker)

    Time Complexity Analysis:
        - Traversal Complexity: O(sum_{f in direct_friends} deg(f)) bounded by O(|E|).
        - Profile Intersection: O(|Interests_u| + |Interests_c|) per candidate.
        - Sorting: O(C log C) where C is the count of 2-hop candidates.
        - Total: O(|V| + |E| + C log C) optimal.

    Args:
        graph: The SocialGraph instance representing the social network.
        user_id: Unique string identifier of the user seeking recommendations.
        limit: Optional maximum number of recommendations to return.
        user_manager: Optional UserManager instance for student profile access.
        same_branch_only: If True and user_manager provided, only recommends students in same branch.
        same_year_only: If True and user_manager provided, only recommends students in same year.
        branch_filter: Optional specific branch to filter candidates by (e.g. "CSE").
        year_filter: Optional specific year of study to filter candidates by (e.g. 2).

    Returns:
        List[Dict[str, Any]]: A ranked list of recommendation dictionaries:
            [
                {
                    "user_id": str,
                    "name": str,
                    "mutual_count": int,
                    "mutual_friends": List[str],
                    "shared_interests": List[str],
                    "jaccard": float,
                    "branch": str,
                    "year": int,
                    "score_explanation": str
                },
                ...
            ]
        Returns an empty list [] if user does not exist, has no direct friends,
        or has no eligible 2-hop candidates.
    """
    if not isinstance(user_id, str):
        return []
    user_id = user_id.strip()
    if not graph.has_user(user_id):
        return []

    direct_friends: Set[str] = graph.get_friends(user_id)
    if not direct_friends:
        return []

    # Get query user's profile attributes if user_manager is available
    user_profile = user_manager.get_user(user_id) if user_manager is not None else None
    user_interests: Set[str] = set(user_profile.get("interests", [])) if user_profile else set()
    user_branch: Optional[str] = user_profile.get("branch") if user_profile else None
    user_year: Optional[int] = user_profile.get("year") if user_profile else None

    # Step 1: Collect 2-hop candidates and aggregate mutual friends
    candidate_mutuals: Dict[str, Set[str]] = defaultdict(set)
    for f in direct_friends:
        for candidate in graph.get_friends(f):
            if candidate == user_id or candidate in direct_friends:
                continue
            candidate_mutuals[candidate].add(f)

    if not candidate_mutuals:
        return []

    # Step 2: Build candidate records and apply filters
    recommendations: List[Dict[str, Any]] = []

    for candidate_id, mutual_set in candidate_mutuals.items():
        cand_profile = user_manager.get_user(candidate_id) if user_manager is not None else None
        cand_name = cand_profile.get("name", candidate_id) if cand_profile else candidate_id
        cand_branch = cand_profile.get("branch", "CSE") if cand_profile else "CSE"
        cand_year = cand_profile.get("year", 1) if cand_profile else 1
        cand_interests: Set[str] = set(cand_profile.get("interests", [])) if cand_profile else set()

        # Apply branch filters
        if same_branch_only and user_branch and cand_branch != user_branch:
            continue
        if branch_filter and cand_branch.upper() != branch_filter.strip().upper():
            continue

        # Apply year filters
        if same_year_only and user_year and cand_year != user_year:
            continue
        if year_filter and cand_year != year_filter:
            continue

        # Compute Jaccard similarity and shared interests
        shared_interests = sorted(user_interests.intersection(cand_interests))
        jaccard = calculate_jaccard_similarity(user_interests, cand_interests)

        # Build human-readable score explanation
        m_count = len(mutual_set)
        mutual_str = f"{m_count} mutual friend{'s' if m_count != 1 else ''}"
        if shared_interests:
            interests_str = f"shares {', '.join(shared_interests)}"
        else:
            interests_str = "no shared interests"
        explanation = f"{mutual_str} · {interests_str}"

        recommendations.append(
            {
                "user_id": candidate_id,
                "name": cand_name,
                "mutual_count": m_count,
                "mutual_friends": sorted(mutual_set),
                "shared_interests": shared_interests,
                "jaccard": jaccard,
                "branch": cand_branch,
                "year": cand_year,
                "score_explanation": explanation,
            }
        )

    if not recommendations:
        return []

    # Rank candidates:
    # 1. mutual_count descending (-item["mutual_count"])
    # 2. jaccard similarity descending (-item["jaccard"])
    # 3. display name alphabetically (item["name"].lower())
    # 4. user_id tie-breaker (item["user_id"])
    recommendations.sort(
        key=lambda item: (
            -item["mutual_count"],
            -item["jaccard"],
            item["name"].lower() if isinstance(item["name"], str) else "",
            item["user_id"],
        )
    )

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
