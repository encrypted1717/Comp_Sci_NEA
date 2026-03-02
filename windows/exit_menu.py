import pygame
from core.window import Window
from core.button import Button


class ExitMenu(Window):
    def __init__(self, display, renderer):
        super().__init__(display, renderer)

        menu_font  = pygame.font.Font(self.fonts["OldeTome"], 43)
        small_font = pygame.font.Font(self.fonts["OldeTome"], 34)

        self.buttons.add(
            # Prompt label (non-interactive)
            Button(
                (self.center_x, self.center_y - 130),
                (550, 90),
                "What would you like to do?",
                small_font,
                "#ffffff", "#000000", 5,
                border_colour="#ffffff",
                offset_y=4,
            ),

            # Log out — clears session and returns to login screen
            Button(
                (self.center_x - 200, self.center_y),
                (340, 90),
                "Log Out",
                menu_font,
                "#ffffff", "#000000", 5,
                border_colour="#ffffff",
                offset_y=4,
                action="logout",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
            ),

            # Exit — quits the application entirely
            Button(
                (self.center_x + 200, self.center_y),
                (340, 90),
                "Exit Game",
                menu_font,
                "#ffffff", "#000000", 5,
                border_colour="#ffffff",
                offset_y=4,
                action="exit",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
            ),

            # Back
            Button(
                (150, 90),
                (175, 70),
                "Back",
                menu_font,
                "#ffffff", "#000000", 5,
                border_colour="#ffffff",
                offset_y=4,
                action="back",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
            ),
        )

    def event_handler(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action is None:
                    continue
                if action == "exit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    return None
                if action == "logout":
                    return "logout"
                return action
        return None

    def draw(self, dt):
        self.surface.fill((255, 255, 255))
        super().draw(dt)