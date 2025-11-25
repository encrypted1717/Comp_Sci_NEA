import pygame
from configparser import ConfigParser
from core.button import Button


class SettingsMenu(Button):
    def __init__(self, window, screen):
        super().__init__(screen)
        self.events = None
        self.window = window
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]
        #get configs for game
        self.config = ConfigParser()
        self.config.read("assets\\game_settings\\config_user.ini")
        self.width = self.config.getint("Graphics", "Screen_Width")
        self.height = self.config.getint("Graphics", "Screen_Height")

        #reset background to white
        self.colour = pygame.Color('#ffffff')
        self.window.fill(self.colour)
        #make button
        self.font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 37)
        self.back_btn = self.create_rect((150, 120), (160, 60), '#ffffff', '#000000', "Back", self.font, 0, offset_y=4)
        self.front_font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 56)
        self.graphics_btn = self.create_rect((1920/2, 120), (235,70), '#ffffff', '#000000', "Graphics", self.front_font, 0, offset_y=4)
        #resolution setting setup
        self.resolution_font = pygame.font.Font("assets\\fonts\\Number_Font_Osadam\\Gothic_pixel_font.ttf", 16)
        self.resolution = str(self.width) + " X " + str(self.height)
        self.resolution_txt = self.create_rect((1920/2 - 175, 300), (200, 60), '#ffffff', '#000000', "Resolution", self.font, 0, offset_y=4)
        self.resolution_btn = self.create_rect((1920 / 2 + 175, 300), (200, 60), '#000000', '#000000', self.resolution, self.resolution_font, 5, offset_y=4)
        self.buttons = [self.back_btn, self.graphics_btn, self.resolution_txt, self.resolution_btn]

    def event_handler(self, events):
        self.events = events
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # if user left clicks mouse
                if self.resolution_btn["rect"].collidepoint(event.pos):

                    self.resolution_btn["text"] = "1280 x 720"
                elif self.back_btn["rect"].collidepoint(event.pos):
                    return "main_menu"
            # check_click = print(event.pos, event.button)
        return None

    def draw(self):
        for btn in self.buttons:
            pygame.draw.rect(self.window, btn["colour"], btn["rect"], btn["border"])
            self.window.blit(btn["text surf"], btn["text rect"])