import settings

class SettingsManager:
    @staticmethod
    def load():
        return {
            "SHOW_ENEMY_HP_BAR": settings.SHOW_ENEMY_HP_BAR,
            "SHOW_HITBOX_PLAYER": settings.SHOW_HITBOX_PLAYER,
            "SHOW_HITBOX_ENEMY": settings.SHOW_HITBOX_ENEMY,
            "MASTER_VOLUME": settings.MASTER_VOLUME,
            "MUSIC_VOLUME": settings.MUSIC_VOLUME,
            "SFX_VOLUME": settings.SFX_VOLUME
        }

    @staticmethod
    def save(new_settings: dict):
        path = "settings.py"
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for key, value in new_settings.items():
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{key}"):
                    if isinstance(value, str):
                        lines[i] = f'{key} = "{value}"\n'
                    elif isinstance(value, bool):
                        lines[i] = f"{key} = {str(value)}\n"
                    else:
                        lines[i] = f"{key} = {value}\n"
                    break

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
