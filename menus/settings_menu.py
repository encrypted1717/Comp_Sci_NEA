import pygame
from core.config_manager import ConfigManager
from core.button import Button


class SettingsMenu(Button):
    def __init__(self, window):
        super().__init__()
        self.events = None
        self.window = window
        #get configs for game
        self.config_manager = ConfigManager()
        self.config_manager.open_file("assets\\game_settings\\config_user.ini")
        self.config = self.config_manager.get_config()
        self.screen_width = self.config.getint("Graphics", "Screen_Width")
        self.screen_height = self.config.getint("Graphics", "Screen_Height")
        #reset background to white
        self.colour = pygame.Color('#ffffff') # White
        #make button
        self.font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 37)
        self.back_btn = self.create_rect((150, 120), (160, 60), '#ffffff', '#000000', "Back", self.font, 0, offset_y=4)
        self.front_font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 56)
        self.graphics_btn = self.create_rect((1920/2, 120), (235,70), '#ffffff', '#000000', "Graphics", self.front_font, 0, offset_y=4)
        #resolution setting setup
        self.resolution_font = "assets\\fonts\\Number_Font_Osadam\\Gothic_pixel_font.ttf"
        self.resolution_font = pygame.font.Font(self.resolution_font, 16)
        self.resolution = str(self.screen_width) + " x " + str(self.screen_height)
        self.resolution_txt = self.create_rect((785, 350), (300, 60), '#ffffff', '#000000', "Resolution", self.font, 0, offset_y=4)
        self.resolution_btn = self.create_rect((1135, 350), (300, 60), '#000000', '#000000', self.resolution, self.resolution_font, 5, offset_y=4)
        self.buttons = [self.back_btn, self.graphics_btn, self.resolution_txt, self.resolution_btn]

    def event_handler(self, events):
        self.events = events
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # if user left clicks mouse
                if self.resolution_btn["rect"].collidepoint(event.pos):
                    self.resolution_btn = self.update_text(self.resolution_btn, "1280 x 720", '#000000', self.resolution_font)
                elif self.back_btn["rect"].collidepoint(event.pos):
                    return "main_menu"
            # check_click = print(event.pos, event.button)
        return None

    def draw(self):
        for btn in self.buttons:
            pygame.draw.rect(self.window, btn["rect_colour"], btn["rect"], btn["border"])
            self.window.blit(btn["text_surf"], btn["text_rect"])