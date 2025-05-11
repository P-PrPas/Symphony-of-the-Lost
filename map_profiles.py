MAP_PROFILES = {
    "tutorial_hall": {
        "collision_rects": [
            (0, 0, 1920, 730),
            (0, 1060, 1920, 20)
        ],
        "starting_pos": (1000, 1000),
        "transitions": {
            "left": {
                "target_map": "mysterious_forest",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "tutorial_1",
                "player_pos": (100, None)
            }
        },
        "npcs": ["Lynn"]
    },
    "tutorial_1": {
        "has_enemies": True,
        "enemy_data": [
            {"x": 1100, "y": 850, "type": "melee", "sprite": "slime2"},
        ],
        "collision_rects": [
            (0, 0, 1920, 730),
            (0, 1060, 1920, 20)
        ],
        "starting_pos": (1000, 1000),
        "transitions": {
            "left": {
                "target_map": "tutorial_hall",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "tutorial_2",
                "player_pos": (100, None)
            }
        },
        "npcs": ["Lynn"]
    },
    "tutorial_2": {
        "has_enemies": True,
        "enemy_data": [
            {"x": 600, "y": 850, "type": "range", "sprite": "slime1"}
        ],
        "collision_rects": [
            (0, 0, 1920, 730),
            (0, 1060, 1920, 20)
        ],
        "starting_pos": (1000, 1000),
        "transitions": {
            "left": {
                "target_map": "tutorial_1",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "tutorial_3",
                "player_pos": (100, None)
            }
        },
        "npcs": ["Lynn"]
    },
    "tutorial_3": {
        "has_enemies": True,
        "enemy_data": [
            {"x": 600, "y": 700, "type": "range", "sprite": "slime1"},
            {"x": 1100, "y": 700, "type": "melee", "sprite": "slime2"},
        ],
        "collision_rects": [
            (0, 0, 1920, 730),
            (0, 1060, 1920, 20)
        ],
        "starting_pos": (1000, 1000),
        "transitions": {
            "left": {
                "target_map": "tutorial_2",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "tutorial_4",
                "player_pos": (100, None)
            }
        },
        "npcs": ["Lynn"]
    },
    "tutorial_4": {
        "has_enemies": True,
        "enemy_data": [
            {"x": 500, "y": 700, "type": "range", "sprite": "slime1"},
            {"x": 600, "y": 700, "type": "melee", "sprite": "slime2"},
            {"x": 750, "y": 700, "type": "range", "sprite": "slime1"},
            {"x": 350, "y": 700, "type": "melee", "sprite": "slime2"},
            {"x": 200, "y": 700, "type": "melee", "sprite": "slime3"},
            {"x": 400, "y": 700, "type": "melee", "sprite": "slime3"},
        ],
        "collision_rects": [
            (0, 0, 1920, 730),
            (0, 1060, 1920, 20)
        ],
        "starting_pos": (1000, 1000),
        "transitions": {
            "left": {
                "target_map": "tutorial_4",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "tutorial_5",
                "player_pos": (100, None)
            }
        },
        "npcs": ["Lynn"]
    },
    "tutorial_5": {
        "collision_rects": [
            (0, 0, 1920, 730),
            (0, 1060, 1920, 20)
        ],
        "starting_pos": (1000, 1000),
        "transitions": {
            "left": {
                "target_map": "tutorial_4",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "battleground",
                "player_pos": (100, None)
            }
        },
        "npcs": ["Lynn"]
    },
    "battleground": {
        "has_enemies": True,
        "enemy_data": [
            {"x": 1000, "y": 700, "type": "range", "sprite": "slime1"},
            {"x": 600, "y": 700, "type": "melee", "sprite": "slime2"},
            {"x": 750, "y": 700, "type": "range", "sprite": "slime1"},
            {"x": 500, "y": 700, "type": "melee", "sprite": "slime2"},
            {"x": 1100, "y": 700, "type": "melee", "sprite": "slime3"},
            {"x": 800, "y": 700, "type": "melee", "sprite": "slime3"},
        ],
        "collision_rects": [
            (0, 0, 1920, 730),
            (0, 1060, 1920, 20)
        ],
        "starting_pos": (1000, 1000),
        "transitions": {
            "left": {
                "target_map": "mysterious_forest",
                "player_pos": (1750, None)
            },
            "right": {
                "target_map": "ruin",
                "player_pos": (100, None)
            }
        },
        "npcs": ["Lynn"]
    },
}