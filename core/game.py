class Game(Button):
    def __init__(self, window, screen):
        super().__init__(window)
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]

    def event_handler(self):
        return "start"