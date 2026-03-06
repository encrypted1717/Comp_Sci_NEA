import logging
import pygame
from core.button import Button


class Window:
    def __init__(self, display, renderer):
        # Logging setup
        self.log = logging.getLogger(type(self).__module__)
        self.log.info("Initialising %s module", type(self).__name__)
        # Main setup
        self.display = display
        self.renderer = renderer
        self.surface = self.renderer.virtual_surface
        self.design_width, self.design_height = self.renderer.design_size # In this case its 1920, 1080 (the design width and height?)
        self.events = None
        self.dt = 0
        # Create helper attributes
        self.center_x = self.design_width / 2
        self.center_y = self.design_height / 2

        self.fonts = {
            "OldeTome" : "assets\\fonts\\OldeTome\\OldeTome.ttf",
            "GothicPixel" : "assets\\fonts\\Number_Font_Osadam\\Gothic_pixel_font.ttf"
        }
        self.buttons = pygame.sprite.Group()

        if self.on_escape() == "back" and self.show_back_button():
            self._back_btn = Button(
                (150, 90), (160, 60), "Back",
                pygame.font.Font(self.fonts["OldeTome"], 37),
                "#ffffff", "#000000", 5,
                border_colour="#000000", offset_y=4,
                action="back",
                hover_text_colour="#000000",
                hover_rect_colour="#ffffff",
                hover_border_colour="#000000",
                fill_on_hover=True
            )
            self.buttons.add(self._back_btn)
        else:
            self._back_btn = None

    def event_handler(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                result = self.on_escape()
                if result is not None:
                    return result
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action:
                    result = self.handle_action(action)
                    if result is not None:
                        return result
        return None

    def draw(self, dt):
        self.dt = dt
        mouse_pos = self.renderer.get_virtual_mouse_pos()
        self.buttons.update(mouse_pos, dt)
        self.buttons.draw(self.surface)  # keep loading buttons

    def on_escape(self):
        return "back"  # sensible default - most windows want this

    def show_back_button(self):
        return True  # default: show the auto back button

    def handle_action(self, action):
        return action  # default: pass through unchanged

    # Update all variables with new display
    def set_display(self, new_display):
        # Called when the window surface changes (resolution/mode/resizing)
        self.display = new_display
        self.renderer.set_window_surface(new_display)
        self.surface = self.renderer.virtual_surface