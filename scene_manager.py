class SceneManager:
    def __init__(self, initial_scene):
        self.scene = initial_scene
        self.scene.manager = self

    def switch_to(self, new_scene):
        self.scene = new_scene
        self.scene.manager = self
        self.scene.on_enter()

    def run(self):
        self.scene.on_enter()
        if hasattr(self.scene, 'run'):
            self.scene.run()
        else:
            while self.scene.running:
                self.scene.handle_events()
                self.scene.update()
                self.scene.draw()