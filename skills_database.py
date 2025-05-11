from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from note_type import NoteType

@dataclass
class SkillData:
    name: str
    animation_path: Optional[str]
    frames: int
    cooldown: int
    hitbox_sizes: Optional[Dict[str, Tuple[int, int]]]
    requirement: Dict[NoteType, int]
    damage: int
    description: str = ""
    effect_offsets: Optional[Dict[str, Tuple[int, int]]] = None
    follow_caster: bool = False
    duration: Optional[int] = None

    charge_time: Optional[int] = None  # milliseconds
    radius: Optional[int] = None  # base radius
    radius_bonus: Optional[int] = None  # additional radius by charge
    bonus_damage: Optional[int] = None


skill_database = {
    "strike_beat": SkillData(
        name="Strike Beat",
        animation_path="assets/sprites/test sprite/strike_beat2.png",
        frames=5,
        cooldown=200,
        hitbox_sizes={
            "up": (120, 70),
            "down": (120, 70),
            "left": (70, 120),
            "right": (70, 120)
        },
        effect_offsets={
                "up": (-100, -175),
                "down": (-100, -30),
                "left": (-150, -95),
                "right": (-50, -95)
            },
        requirement={NoteType.QUARTER: 1},
        damage=1,
        description="Quick slash attack using a quarter note.",
        follow_caster = True,
        duration = None
    ),
    "note_flurry": SkillData(
        name="Note Flurry",
        animation_path= None,
        frames=8,
        cooldown=150,
        hitbox_sizes={
            "up": (50, 100),
            "down": (50, 100),
            "left": (100, 50),
            "right": (100, 50)
        },
        effect_offsets={
                "up": (0, 0),
                "down": (4000, 100),
                "left": (0, 0),
                "right": (0, 0)
            },
        requirement={NoteType.EIGHTH: 1},
        damage=2,
        description="Rapid fire notes attack from range.",
        follow_caster = True,
        duration = None
    ),
    "sound_barrier": SkillData(
        name="Sound Barrier",
        animation_path=None,
        frames=1,
        cooldown=2000,
        hitbox_sizes=(0, 0),
        requirement={NoteType.HALF: 1},
        damage=0,
        description="Creates a shield that blocks all damage for a short duration.",
        follow_caster=True,
        duration=1000  # ✅ เพิ่ม duration เป็น 2 วิ
    ),
    "soundquake": SkillData(
        name="Soundquake",
        animation_path=None,  # ไม่มี sprite
        frames=1,
        cooldown=2000,  # base cooldown ก่อนคิดระดับ charge
        hitbox_sizes=None,  # ไม่ใช้ hitbox sprite
        requirement={NoteType.WHOLE: 1},
        damage=10,  # base damage ก่อนคิด level
        description="A shockwave burst around the player that grows stronger when charged.",
        follow_caster=False,
        duration=500,
        charge_time=3000,
        radius=80,
        radius_bonus=80,
        bonus_damage=20
    ),
    "heal_note": SkillData(
        name="Healing Note",
        animation_path=None,
        frames=1,
        cooldown=10000,
        hitbox_sizes=None,
        requirement={NoteType.HALF: 2},
        damage=-5,
        description="Heals the player for 5 HP using a melodic combo.",
        follow_caster=True
    ),
    "crescendo": SkillData(
        name="Crescendo",
        animation_path=None,
        frames=1,
        cooldown=10000,
        hitbox_sizes=None,
        requirement={
            NoteType.HALF: 1,
            NoteType.QUARTER: 1,
            NoteType.EIGHTH: 2
        },
        damage=0,
        description="Boosts attack power 2x for 5 seconds with a precise combo.",
        follow_caster=True,
        duration=5000
    ),
}
