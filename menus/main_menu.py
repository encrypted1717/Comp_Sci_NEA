import pygame
from core.button import Button
from graphics.parallax_background import Background

class MainMenu(Button):
    def __init__(self, window, screen):
        super().__init__()
        self.new_window = None
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]
        self.events = None
        self.window = window
        #parallax background
        self.dt = None
        self.background = Background()
        self.dict_background = self.background.get_background()
        self.scale = None
        self.scale_height = None
        self.scale_width = None  # default scale
        self.transform_background_to_window_size()
        #buttons
        self.font = pygame.font.Font("assets\\fonts\\OldeTome\\OldeTome.ttf", 43)
        self.start_button = self.create_rect((960, 500), (255, 70), '#ffffff', '#ffffff', "Start", self.font, 5, offset_y=4) #returns dict{"text": , "text rect": , "colour": , "rect": , "border"}
        self.controls_button = self.create_rect((960, 590), (255, 70), '#ffffff', '#ffffff', "Controls", self.font, 5, offset_y=4) #position is 550, the previous y coordinate of the other button + their y dimension + a gap of 15
        self.settings_button = self.create_rect((960, 680), (255, 70), '#ffffff', '#ffffff', "Settings", self.font, 5, offset_y=4)
        self.exit_button = self.create_rect((960, 770), (255, 70), '#ffffff','#ffffff' , "Exit", self.font, 5, offset_y=4)
        self.buttons = [self.start_button, self.controls_button, self.settings_button, self.exit_button]
        #plan to make a variable called self.gap possibly which uses the gap value if a button collides with another button

    def draw_background(self):
        #TODO could implement pygame sprites for this instead using spite.kill ... would have to see which is more efficient
        for layer in self.dict_background:
            layer["x"] -= layer["speed"] * self.dt #x value is the coordinate on the screen which gets reduced by the value speed
            if layer["x"] <= -layer["img"].get_width():
                layer["x"] = 0 #reset scrolling if image off the screen/less than the x dimension of the image

            self.window.blit(layer["img"], (layer["x"], 0))  # draw first copy
            self.window.blit(layer["img"], (layer["x"] + layer["img"].get_width(), 0))  # draw second copy

    def draw_buttons(self):
        if self.buttons: #if list isn't empty then...
            for btn in self.buttons:
                pygame.draw.rect(self.window, btn["rect_colour"], btn["rect"], btn["border"])
                self.window.blit(btn["text_surf"], btn["text_rect"]) #dictionary received from button class returns the text to put in the button and the type of rectangle

    def transform_background_to_window_size(self):
        for layer in self.dict_background:
            #scales background to window size
            self.scale_width = self.screen_width / layer["img"].get_width() # get scale factor for width
            self.scale_height = self.screen_height / layer["img"].get_height()
            self.scale = max(self.scale_width, self.scale_height)
            layer["img"] = pygame.transform.scale_by(layer["img"], self.scale) #multiply by scale factor because height is irrelevant as the height of all the files are the same
            #check_image = print("name", layer["speed"], "Height", layer["img"].get_height(), "height of window", self.screen_height)
            self.scale = 1 #updating/resetting scale
            #TODO fix sun appearing on both ends of the screen by scaling the image a bit larger

    def event_handler(self, events):
        self.events = events
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #if user left clicks mouse
                for btn in self.buttons:
                    if btn["rect"].collidepoint(event.pos): #if colliding with any menu buttons... open that menu
                        if btn["text"].lower() == "start":
                            return "start"
                        elif btn["text"].lower() == "controls":
                            return "controls"
                        elif btn["text"].lower() == "settings":
                            return "settings"
                        elif btn["text"].lower() == "exit":
                            return "exit"
                #check_click = print(event.pos, event.button)
        return None

    def draw(self, dt):
        self.dt = dt
        self.draw_background() #keep loading background
        self.draw_buttons() #keep loading buttons