import pygame
from core.button import Button
from graphics.parallax_background import Background

class MainMenu:
    def __init__(self, display, screen):
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]
        self.events = None
        self.display = display
        self.dt = None
        #parallax background
        self.background = Background()
        self.dict_background = self.background.get_background()
        self.scale = None
        self.scale_height = None
        self.scale_width = None  # default scale
        self.transform_background_to_display_size()
        #font
        self.font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 43)
        #buttons
        self.buttons = pygame.sprite.Group()
        # noinspection PyTypeChecker
        self.buttons.add(
            Button((960, 500), (255, 70), "Start", self.font, "#ffffff", "#000000", 5, border_colour= "#ffffff", fill = False, offset_y = 4, action = "start", hover_text_colour = "#000000", hover_rect_colour = "#ffffff", hover_border_colour = "#000000", fill_on_hover = True),
            Button((960, 590), (255, 70), "Controls", self.font, "#ffffff", "#000000", 5, border_colour= "#ffffff", fill = False, offset_y = 4, action = "controls", hover_text_colour = "#000000", hover_rect_colour = "#ffffff", hover_border_colour = "#000000", fill_on_hover = True),
            Button((960, 680), (255, 70), "Settings", self.font, "#ffffff", "#000000", 5, border_colour= "#ffffff", fill = False, offset_y = 4, action = "settings", hover_text_colour = "#000000", hover_rect_colour = "#ffffff", hover_border_colour = "#000000", fill_on_hover = True),
            Button((960, 770), (255, 70), "Exit", self.font, "#ffffff", "#000000", 5, border_colour= "#ffffff", fill = False, offset_y = 4, action = "exit", hover_text_colour = "#000000", hover_rect_colour = "#ffffff", hover_border_colour = "#000000", fill_on_hover = True),
        )

        #plan to make a variable called self.gap possibly which uses the gap value if a button collides with another button

    def draw_background(self):
        for layer in self.dict_background:
            layer["x"] -= layer["speed"] * self.dt #x value is the coordinate on the screen which gets reduced by the value speed
            if layer["x"] <= -layer["img"].get_width():
                layer["x"] = 0 #reset scrolling if image off the screen/less than the x dimension of the image

            self.display.blit(layer["img"], (layer["x"], 0))  # draw first copy
            self.display.blit(layer["img"], (layer["x"] + layer["img"].get_width(), 0))  # draw second copy

    # TODO fix sun appearing on both ends of the screen by scaling the image a bit larger
    def transform_background_to_display_size(self):
        for layer in self.dict_background:
            #scales background to window size
            self.scale_width = self.screen_width / layer["img"].get_width() # get scale factor for width
            self.scale_height = self.screen_height / layer["img"].get_height()
            self.scale = max(self.scale_width, self.scale_height)
            layer["img"] = pygame.transform.scale_by(layer["img"], self.scale) #multiply by scale factor because height is irrelevant as the height of all the files are the same
            #check_image = print("name", layer["speed"], "Height", layer["img"].get_height(), "height of window", self.screen_height)
            self.scale = 1 #updating/resetting scale

    def event_handler(self, events):
        for event in events:
            for btn in self.buttons:
                action = btn.handle_event(event)
                if action is not None:
                    return action
        return None

    def draw(self, dt):
        self.dt = dt
        self.draw_background() #keep loading background
        self.buttons.update(pygame.mouse.get_pos())
        self.buttons.draw(self.display) #keep loading buttons