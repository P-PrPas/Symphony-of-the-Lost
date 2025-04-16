from dataclasses import dataclass
from typing import Dict, Tuple
from note_type import NoteType

@dataclass
class SkillData:
    name: str
    animation_path: str
    frames: int
    cooldown: int
    hitbox_size: Tuple[int, int]
    requirement: Dict[NoteType, int]
    damage: int
    description: str = ""

skill_database = {
    "strike_beat": SkillData(
        name="Strike Beat",
        animation_path="assets/sprites/test sprite/strike_beat.png",
        frames=8,
        cooldown=300,
        hitbox_size=(60, 40),
        requirement={NoteType.QUARTER: 1},
        damage=10,
        description="Quick slash attack using a quarter note."
    ),
    "note_flurry": SkillData(
        name="Note Flurry",
        animation_path="assets/animations/note_flurry.png",
        frames=8,
        cooldown=150,
        hitbox_size=(50, 30),
        requirement={NoteType.EIGHTH: 2, NoteType.QUARTER: 1},
        damage=7,
        description="Rapid fire notes attack from range."
    )
}
