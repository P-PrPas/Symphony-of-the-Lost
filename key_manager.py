class KeyPressManager:
    def __init__(self):
        self.held_keys = set()

    def is_new_press(self, key, keys_pressed):
        if keys_pressed[key]:
            if key not in self.held_keys:
                self.held_keys.add(key)
                return True
        else:
            self.held_keys.discard(key)
        return False

    def is_key_held(self, key, keys):
        return keys[key]