import os
import pygame


#WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows
class WindowManager:
    def __init__(self, window):
        self.events = None
        self.window = window
        self.state = "main_menu" #defaults to this
        self.win_res = pygame.display.list_modes()
        self.windows = {"main_menu" : MainMenu(self.window, self.win_res)} #windows that are preloaded
        self.new_state = None

    def get_window(self): #or create/load anything that isn't already loaded into the windows
        if self.state not in self.windows:
            if self.state == "main_menu":
                self.windows["main_menu"] = MainMenu(self.window, self.win_res)
            elif self.state == "start":
                self.windows["start"] = StartMenu(self.window, self.win_res)
            elif self.state == "controls":
                self.windows["controls"] = ControlsMenu(self.window, self.win_res)
            elif self.state == "settings":
                self.windows["settings"] = SettingsMenu(self.window, self.win_res)
            else:
                self.windows["exit"] = ExitMenu(self.window)
        return self.windows[self.state]

    def set_window(self, events):
        self.events = events
        self.new_state = self.get_window().event_handler(self.events)
        if self.new_state: #if true then there is a new state
            del self.windows[self.state]
            self.state = self.new_state

    def draw(self):
        self.get_window().draw()


class Button(pygame.sprite.Sprite):
    def __init__(self, window): #consider adding a log as image
        super().__init__()
        self.window = window
        self.btn = None

        #features of rect
        self.rect = None
        self.position = None
        self.dimensions = None
        self.colour = None
        self.offset_x = 0
        self.offset_y = 0
        self.border = False

        #text surface
        self.text = ""
        self.text_surf = None
        self.text_rect = None

    def create_rect(self, position, dimensions, colour, text, font, border = 0, offset_x = 0, offset_y = 0, image= None):
        self.text = text
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.border = border
        self.colour = colour
        self.dimensions = dimensions #tuple of width and height

        #make the text rect
        self.rect = pygame.Rect((0,0), dimensions) #create rect but leave the coordinate to default to 0,0
        self.rect.center = position
        self.text_surf = font.render(self.text, False, '#ffffff')  # true/false is for anti-aliasing on the font
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        #apply offsets if needed
        if self.offset_x != 0:
            self.text_rect.x += self.offset_x
        if self.offset_y != 0:
            self.text_rect.y += self.offset_y

        #dictionary holds all data of the button
        self.btn = {"text": self.text, "text surf" : self.text_surf, "text rect": self.text_rect, "colour" : self.colour, "rect" : self.rect, "border" : self.border}
        return self.btn


class MainMenu(Button):
    def __init__(self, window, screen):
        super().__init__(window)
        from graphics.parallax_background import background
        self.new_window = None
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]
        self.events = None
        self.window = window
        #parallax background
        self.parallax_background = background
        self.scale = None
        self.scale_height = None
        self.scale_width = None  # default scale
        self.transform_background_to_window_size()
        #buttons
        self.font = pygame.font.Font("assets/fonts/OldeTome.ttf", 43)
        self.start_button = self.create_rect((960, 500), (255, 70), '#ffffff', "start", self.font, 5, offset_y=4) #returns dict{"text": , "text rect": , "colour": , "rect": , "border"}
        self.controls_button = self.create_rect((960, 590), (255, 70), '#ffffff', "controls", self.font, 5, offset_y=4) #position is 550, the previous y coordinate of the other button + their y dimension + a gap of 15
        self.settings_button = self.create_rect((960, 680), (255, 70), '#ffffff', "settings", self.font, 5, offset_y=4)
        self.exit_button = self.create_rect((960, 770), (255, 70), '#ffffff', "exit", self.font, 5, offset_y=4)
        self.buttons = [self.start_button, self.controls_button, self.settings_button, self.exit_button]
        #plan to make a variable called self.gap possibly which uses the gap value if a button collides with another button

    def draw_background(self):
        #TODO could implement pygame sprites for this instead using spite.kill ... would have to see which is more efficient
        for layer in self.parallax_background:
            layer["x"] -= layer["speed"] #x value is the coordinate on the screen which gets reduced by the value speed
            if layer["x"] <= -layer["img"].get_width():
                layer["x"] = 0 #reset scrolling if image off the screen/less than the x dimension of the image

            self.window.blit(layer["img"], (layer["x"], 0))  # draw first copy
            self.window.blit(layer["img"], (layer["x"] + layer["img"].get_width(), 0))  # draw second copy

    def draw_buttons(self):
        if self.buttons: #if list isn't empty then...
            for btn in self.buttons:
                pygame.draw.rect(self.window, btn["colour"], btn["rect"], btn["border"])
                self.window.blit(btn["text surf"], btn["text rect"]) #dictionary received from button class returns the text to put in the button and the type of rectangle

    def transform_background_to_window_size(self):
        for layer in self.parallax_background:
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
                        if btn["text"] == "start":
                            return "start"
                        elif btn["text"] == "controls":
                            return "controls"
                        elif btn["text"] == "settings":
                            return "settings"
                        elif btn["text"] == "exit":
                            return "exit"
                #check_click = print(event.pos, event.button)
        return None

    def draw(self):
        self.draw_background() #keep loading background
        self.draw_buttons() #keep loading buttons


class Start(Button):
    def __init__(self, window, screen):
        super().__init__(window)
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]

    def event_handler(self):
        return "start"


class ControlsMenu(Button):
    def __init__(self, window, screen):
        super().__init__(window)
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]

    def event_handler(self):
        return "controls"


class SettingsMenu(Button):
    def __init__(self, window, screen):
        super().__init__(screen)
        self.window = window
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]
        #get configs for game
        self.config = ConfigParser()
        self.config.read("assets\\game_settings\\settings.ini")
        self.graphics = {}
        self.sections = self.config.options("Graphics")
        self.resolution = self.config.get("Graphics","resolution")
        self.fullscreen = self.config.getboolean("Graphics","fullscreen")
        self.fps = self.config.getint("Graphics","fps")
        #reset background to white
        self.colour = pygame.Color('#ffffff')
        self.window.fill(self.colour)
        #make button
        self.font = pygame.font.Font("assets/fonts/OldeTome.ttf", 43)
        self.back_btn = self.create_rect((150, 120), (175, 70), '#000000', "Back", self.font, 0, offset_y=4)
        self.buttons = [self.back_btn]

    def event_handler(self, events):
        self.events = events
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # if user left clicks mouse
                if self.back_btn["rect"].collidepoint(event.pos):
                    return "main_menu"
            # check_click = print(event.pos, event.button)
        return None

    def draw(self):
        for btn in self.buttons:
            pygame.draw.rect(self.window, btn["colour"], btn["rect"], btn["border"])
            self.window.blit(btn["text surf"], btn["text rect"])


class ExitMenu(Button):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.events = None
        self.font = pygame.font.Font("assets/fonts/OldeTome.ttf", 43)
        self.confirmation_btn = self.create_rect((960, 540), (550, 120), '#000000', "Are you sure you want to exit", self.font, 0, offset_y=4)
        self.back_btn = self.create_rect((150, 120), (175, 70), '#000000', "Back", self.font, 0, offset_y=4)
        self.buttons = [self.confirmation_btn, self.back_btn]

    def event_handler(self, events):
        self.events = events
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # if user left clicks mouse
                if self.confirmation_btn["rect"].collidepoint(event.pos):  # if colliding with any menu buttons... open that menu
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if self.back_btn["rect"].collidepoint(event.pos):
                    return "main_menu"
            # check_click = print(event.pos, event.button)
        return None

    def draw(self):
        for btn in self.buttons:
            pygame.draw.rect(self.window, btn["colour"], btn["rect"], btn["border"])
            self.window.blit(btn["text surf"], btn["text rect"])


def main():
    pygame.init() #initiating pygame
    clock = pygame.time.Clock() #tool to control tick speed/fps/physics
    vector = pygame.math.Vector2  # import 2d assets from pygame
    #check if user settings are already created
    screen_width, screen_height =

    window = pygame.display.set_mode((screen_width, screen_height))

    manager = WindowManager(window)

    running = True
    while running:
        events = pygame.event.get()  # store events in a variable and updates it
        clock.tick(60) #sets tick speed and returns number of milliseconds passed from last time tick was called
        fps = clock.get_fps()
        #check_fps = print(f"{clock.tick(60)} and {fps} and {dt}") #check fps per second and dt value
        dt = fps / 1000  # converting to seconds

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        manager.set_window(events)
        manager.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()