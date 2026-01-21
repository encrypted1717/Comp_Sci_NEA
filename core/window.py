import pygame


class Window:
    def __init__(self, display, renderer):
        self.display = display
        self.renderer = renderer

        self.surface = self.renderer.virtual_surface

        self.display_width, self.display_height = self.renderer.design_size # In this case its 1920, 1080

        self.center_x = 960
        self.center_y = 540

        self.events = None
        self.dt = 0
        self.fonts = {
            "OldeTome" : "assets\\fonts\\OldeTome\\OldeTome.ttf",
            "GothicPixel" : "assets\\fonts\\Number_Font_Osadam\\Gothic_pixel_font.ttf"
        }
        self.buttons = pygame.sprite.Group()

    def draw(self, dt):
        self.dt = dt
        mouse_pos = self.renderer.get_virtual_mouse_pos()
        self.buttons.update(mouse_pos)
        self.buttons.draw(self.surface)  # keep loading buttons

    # Update all variables with new display
    def set_display(self, new_display):
        # Called when the window surface changes (resolution/mode/resizing)
        self.display = new_display
        self.renderer.set_window_surface(new_display)
        self.surface = self.renderer.virtual_surface