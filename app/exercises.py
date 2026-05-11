
#the learning paths and helper functions to fetch exercise content.


from app.content import ALL_EXERCISES


# The 4 learning paths shown on the dashboard.
LEARNING_PATHS = {
    "network": {
        "title": "Network Attacks",
        "description": "Learn how attackers probe and exploit networks using scanning, flooding, and brute force techniques.",
        "icon": "🌐",
        "exercises": ["port_scan", "dos_attack", "brute_force"],
    },
    "injection": {
        "title": "Injection Attacks",
        "description": "Understand how attackers inject malicious code into web applications through input fields.",
        "icon": "💉",
        "exercises": ["sql_injection", "xss_attack"],
    },
    "passwords": {
        "title": "Password Security",
        "description": "Discover why weak passwords are dangerous and how attackers crack them.",
        "icon": "🔑",
        "exercises": ["weak_passwords", "credential_stuffing", "password_hashing"],
    },
    "malware": {
        "title": "Malware",
        "description": "Learn about different types of malicious software and how they spread and get detected.",
        "icon": "🦠",
        "exercises": ["viruses", "ransomware", "trojans"],
    },
}


EXERCISES = ALL_EXERCISES


def get_exercise(exercise_id):
    """Look up a single exercise by id, or None if not found."""
    return EXERCISES.get(exercise_id)


def get_path(path_id):
    """Look up a learning path by id."""
    return LEARNING_PATHS.get(path_id)


def get_path_exercises(path_id):
    """Return all exercises that belong to a learning path."""
    path = LEARNING_PATHS.get(path_id)
    if not path:
        return []

    # build a list of id,exercise_data
    result = []
    for eid in path["exercises"]:
        if eid in EXERCISES:
            result.append({"id": eid, **EXERCISES[eid]})
    return result
