MAP_PROFILES = {
    "castle_hall": {
        "collision_rects": [
            (0, 0, 1920, 540),
            (0, 1060, 1920, 20)
        ],
        "transitions": {
            "left": {
                "target_map": "mysterious_forest",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "ruin",
                "player_pos": (100, None)
            }
        }
    },
    "mysterious_forest": {
        "has_enemies": True,
        "enemy_data": [
            {"x": 600, "y": 700, "type": "melee", "sprite": "slime1"},
            {"x": 1100, "y": 700, "type": "range", "sprite": "slime2"},
        ],
        "barriers": True,
        "collision_rects": [
            (0, 0, 1920, 540),
            (0, 1060, 1920, 20)
        ],
        "transitions": {
            "left": {
                "target_map": "tomb",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "castle_hall",
                "player_pos": (100, None)
            }
        }
    }
}
