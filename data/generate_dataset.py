"""Campus social network synthetic dataset generator.

Generates realistic campus social graphs of N students with:
- Student names, unique handles (usernames), branches, study years, and interest tags.
- Clustered community structure (clique-like study groups and branch clusters).
- Cross-branch bridge friendships (clubs, sports, mutual interests).
- Isolated students and small disconnected components to demonstrate unreachable BFS paths.
- Reproducible via random seed.
- Runnable as CLI or importable module.
"""

import json
import os
import random
from typing import Any, Dict, List, Set, Tuple


FIRST_NAMES = [
    "Aarav", "Aditi", "Advait", "Akash", "Ananya", "Aryan", "Bhavya", "Chetan",
    "Dev", "Diya", "Esha", "Gaurav", "Harsh", "Isha", "Kabir", "Kavya", "Madhav",
    "Meera", "Neha", "Nikhil", "Pooja", "Pranav", "Priya", "Rahul", "Rhea", "Rishi",
    "Rohan", "Saanvi", "Samir", "Sanya", "Shiv", "Shreya", "Siddharth", "Simran",
    "Tanvi", "Tarun", "Utkarsh", "Varun", "Vedant", "Yash", "Zara", "Aman", "Riya"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Reddy", "Mehta", "Singh", "Kumar",
    "Chopra", "Malhotra", "Joshi", "Bhat", "Iyer", "Nair", "Das", "Rao",
    "Mukherjee", "Chatterjee", "Kulkarni", "Deshmukh", "Aggarwal", "Kapoor"
]

BRANCHES = ["CSE", "ECE", "IT", "ME", "CE", "EE", "AIDS"]

INTEREST_TAGS = [
    "coding", "web-dev", "ai", "machine-learning", "robotics", "hackathons",
    "cricket", "football", "badminton", "chess", "gaming", "esports",
    "music", "guitar", "photography", "drama", "dance", "reading",
    "finance", "startups", "design", "graphic-design"
]


def generate_campus_dataset(
    num_students: int = 40,
    seed: int = 42,
    include_isolated: bool = True,
    include_small_component: bool = True,
) -> Dict[str, Any]:
    """Generate a realistic campus social network dataset with N students.

    Args:
        num_students: Total number of students to create (default: 40).
        seed: Random seed for deterministic reproducibility (default: 42).
        include_isolated: If True, guarantees at least 1 isolated student (0 friends).
        include_small_component: If True, guarantees a separate small component of 2-3 students.

    Returns:
        Dict with keys:
            - "users": List of student records dict
            - "friendships": List of [u, v] pairs
    """
    random.seed(seed)

    if num_students < 6:
        num_students = 6

    users: List[Dict[str, Any]] = []
    used_usernames: Set[str] = set()

    for i in range(1, num_students + 1):
        uid = str(i)
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"

        # Generate unique lowercase username
        base_un = f"{first.lower()}_{last.lower()}"
        un = base_un
        counter = 1
        while un in used_usernames:
            counter += 1
            un = f"{base_un}{counter}"
        used_usernames.add(un)

        # Branch assignment (bias toward CSE/IT/ECE for campus vibe)
        branch_weights = [0.35, 0.20, 0.15, 0.10, 0.08, 0.07, 0.05][:len(BRANCHES)]
        branch = random.choices(BRANCHES, weights=branch_weights, k=1)[0]
        year = random.choices([1, 2, 3, 4], weights=[0.3, 0.3, 0.25, 0.15], k=1)[0]

        # Select 2 to 4 interests
        num_interests = random.randint(2, 4)
        interests = sorted(random.sample(INTEREST_TAGS, num_interests))

        users.append({
            "id": uid,
            "name": full_name,
            "username": un,
            "branch": branch,
            "year": year,
            "interests": interests,
        })

    # Reservation of special nodes
    # Last node is isolated (if enabled)
    isolated_uid = str(num_students) if include_isolated else None

    # Two nodes before isolated node form a small separate component
    small_comp_uids: List[str] = []
    if include_small_component and num_students >= 6:
        if include_isolated:
            small_comp_uids = [str(num_students - 2), str(num_students - 1)]
        else:
            small_comp_uids = [str(num_students - 1), str(num_students)]

    excluded_from_main = set(small_comp_uids)
    if isolated_uid:
        excluded_from_main.add(isolated_uid)

    main_uids = [u["id"] for u in users if u["id"] not in excluded_from_main]

    friendships_set: Set[Tuple[str, str]] = set()

    def add_edge(u: str, v: str) -> None:
        if u != v:
            edge = (min(u, v), max(u, v))
            friendships_set.add(edge)

    # 1. Connect small component nodes together only
    if len(small_comp_uids) >= 2:
        for i in range(len(small_comp_uids) - 1):
            add_edge(small_comp_uids[i], small_comp_uids[i + 1])

    # 2. Main component: dense coding club / CSE core (first 8-10 nodes in main)
    core_size = min(10, max(4, len(main_uids) // 3))
    core_uids = main_uids[:core_size]
    for i in range(len(core_uids)):
        for j in range(i + 1, len(core_uids)):
            if random.random() < 0.65:  # Dense connections
                add_edge(core_uids[i], core_uids[j])

    # Ensure core is fully connected via spanning backbone
    for i in range(len(core_uids) - 1):
        add_edge(core_uids[i], core_uids[i + 1])

    # 3. Connect remaining nodes in main component
    # Prefer connecting to nodes with same branch or shared interests
    user_map = {u["id"]: u for u in users}
    connected_main = set(core_uids)

    remaining_main = [uid for uid in main_uids if uid not in connected_main]
    for uid in remaining_main:
        u_rec = user_map[uid]
        # Guarantee connection to at least one already connected node to maintain single main component
        bridge_target = random.choice(list(connected_main))
        add_edge(uid, bridge_target)
        connected_main.add(uid)

        # Add 1 to 3 additional probabilistic edges
        extra_edges = random.randint(1, 3)
        candidates = [t for t in connected_main if t != uid and (min(uid, t), max(uid, t)) not in friendships_set]
        if candidates:
            # Weight by shared branch or shared interests
            weights = []
            for c in candidates:
                c_rec = user_map[c]
                weight = 1.0
                if c_rec["branch"] == u_rec["branch"]:
                    weight += 2.0
                if c_rec["year"] == u_rec["year"]:
                    weight += 1.5
                shared = len(set(c_rec["interests"]).intersection(set(u_rec["interests"])))
                weight += shared * 2.0
                weights.append(weight)

            chosen = random.choices(candidates, weights=weights, k=min(extra_edges, len(candidates)))
            for c in chosen:
                add_edge(uid, c)

    # Sort friendships deterministically
    def edge_key(e: Tuple[str, str]) -> Tuple[int, int, str, int, int, str]:
        u, v = e[0], e[1]
        u_k = (0, int(u), u) if u.isdigit() else (1, 0, u)
        v_k = (0, int(v), v) if v.isdigit() else (1, 0, v)
        return u_k + v_k

    friendships_list = [[e[0], e[1]] for e in sorted(friendships_set, key=edge_key)]

    return {
        "users": users,
        "friendships": friendships_list,
    }


def save_dataset_to_file(data: Dict[str, Any], filepath: str) -> None:
    """Save generated dataset to formatted JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic CampusConnect dataset")
    parser.add_argument("--size", type=int, default=40, help="Number of students (e.g. 40, 50, 200, 1000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--out", type=str, default="data/users.json", help="Output file path")
    args = parser.parse_args()

    dataset = generate_campus_dataset(num_students=args.size, seed=args.seed)
    save_dataset_to_file(dataset, args.out)
    print(f"Generated {len(dataset['users'])} students and {len(dataset['friendships'])} friendships -> {args.out}")
