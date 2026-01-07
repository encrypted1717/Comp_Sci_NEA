import pygame
from core.config_manager import ConfigManager
from core.button import Button

#TODO Settings should update changes to file
#TODO Introduce more settings
class SettingsMenu:
    def __init__(self, display):
        self.dt = None
        self.display = display
        #get configs for game
        self.config_manager = ConfigManager()
        self.config_manager.open_file("assets\\game_settings\\config_user.ini")
        self.config = self.config_manager.get_config()
        self.screen_width = self.config.getint("Graphics", "Screen_Width")
        self.screen_height = self.config.getint("Graphics", "Screen_Height")
        #reset background to white
        self.colour = pygame.Color('#ffffff') # White
        #resolution setting setup
        self.resolution_font = "assets\\fonts\\Number_Font_Osadam\\Gothic_pixel_font.ttf"
        self.resolution_font = pygame.font.Font(self.resolution_font, 16)
        self.resolution = str(self.screen_width) + " x " + str(self.screen_height)
        # Fonts
        self.font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 37)
        self.front_font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 56)
        # Button setup
        self.buttons = pygame.sprite.Group()
        self.__back_btn = Button((150, 120), (160, 60),"Back", self.font,"#ffffff", '#000000', 5, border_colour = "#000000", offset_y = 4, action = "back", hover_text_colour = "#000000", hover_rect_colour = "#ffffff", hover_border_colour = "#000000", fill_on_hover = True)
        self.__graphics_btn = Button((1920 / 2, 120), (235, 70), "Graphics", self.front_font,'#ffffff', '#000000', 0, offset_y = 4)
        self.__resolution_value_btn = Button((1135, 350), (300, 60), self.resolution, self.resolution_font, '#000000', '#ffffff', 5, border_colour = "#000000", offset_y = 4, action = "cycle_resolution", hover_text_colour = "#ffffff", hover_rect_colour = "#000000", hover_border_colour = "#ffffff", fill_on_hover = True)
        self.__resolution_btn = Button((785, 350), (300, 60),"Resolution", self.font,'#ffffff', '#000000', 0, offset_y = 4)
        # noinspection PyTypeChecker
        self.buttons.add(self.__back_btn, self.__graphics_btn, self.__resolution_value_btn, self.__resolution_btn)

    def event_handler(self, events):
        for event in events:
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action is None:
                    continue
                if action == "cycle_resolution":
                    self.resolution = "1280 x 720" # TODO apply proper cycling logic
                    self.__resolution_value_btn.update_text(self.resolution)
                    return None
                return action
        return None

    def draw(self, dt):
        self.dt = dt
        mouse_pos = pygame.mouse.get_pos()
        self.buttons.update(mouse_pos)
        self.buttons.draw(self.display)