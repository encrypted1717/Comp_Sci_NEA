from configparser import ConfigParser
import pygame

#WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows
class WindowManager:
    def __init__(self, window):
        self.events = None
        self.window = window
        self.color = pygame.Color("#ffffff")
        self.font = pygame.font.Font("assets/fonts/OldeTome.ttf", 60) #77 largest font size before grid lines start appearing
        self.state = "main_menu" #defaults to this
        self.win_res = pygame.display.list_modes()
        self.windows = {"main_menu" : MainMenu(self.window, self.win_res)} #windows that are preloaded and colour purple
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
                self.windows["exit"] = ExitMenu()
        return self.windows[self.state]

    def update_window(self, events):
        self.events = events
        self.new_state = self.get_window().update(self.events) #pass events to always check what happens
        if self.new_state != self.state:
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
        from modules.main_menu_background import background
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


        #button class
        self.font = pygame.font.Font("assets/fonts/OldeTome.ttf", 43)
        self.start_button = self.create_rect((960, 500), (255, 70), '#ffffff', "Start", self.font, 5, offset_y=4) #returns dict{"text": , "text rect": , "colour": , "rect": , "border"}

        self.controls_button = self.create_rect((960, 590), (255, 70), '#ffffff', "Controls", self.font, 5, offset_y=4) #position is 550, the previous y coordinate of the other button + their y dimension + a gap of 15

        self.settings_button = self.create_rect((960, 680), (255, 70), '#ffffff', "Settings", self.font, 5, offset_y=4)

        self.exit_button = self.create_rect((960, 770), (255, 70), '#ffffff', "Exit", self.font, 5, offset_y=4)

        self.buttons = [self.start_button, self.controls_button, self.settings_button, self.exit_button]

    def draw_background(self):
        for layer in self.parallax_background:
            layer["x"] -= layer["speed"] #x value is the coordinate on the screen which gets reduced by the value assigned to speed
            if layer["x"] <= -layer["img"].get_width():
                layer["x"] = 0 #reset scrolling if image off the screen

            self.window.blit(layer["img"], (layer["x"], 0))  # draw first copy
            self.window.blit(layer["img"], (layer["x"] + layer["img"].get_width(), 0))  # draw second copy

    def draw_buttons(self):
        if self.buttons: #if list isn't empty then...
            for btn in self.buttons:
                pygame.draw.rect(self.window, btn["colour"], btn["rect"], btn["border"])
                self.window.blit(btn["text surf"], btn["text rect"]) #dictionary received from button class returns the text to put in the button and the type of rectangle


    def transform_background_to_window_size(self):
        for layer in self.parallax_background: #scales background to window size
            self.scale_width = self.screen_width / layer["img"].get_width() # get scale factor for width
            self.scale_height = self.screen_height / layer["img"].get_height()
            self.scale = max(self.scale_width, self.scale_height)
            layer["img"] = pygame.transform.scale_by(layer["img"], self.scale) #multiply by scale factor because height is irrelevant as the height of all the files are the same
            print("name", layer["speed"], "Height", layer["img"].get_height(), "height of window", self.screen_height)
            self.scale = 1 #updating scale

    def event_handler(self):
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.buttons:
                    if btn["rect"].collidepoint(event.pos):
                        for menu in self.buttons:
                            if menu["text"] == "Start":
                                return "Start"
                            elif menu["text"] == "Controls":
                                return "Controls"
                            elif menu["text"] == "Settings":
                                return "Settings"
                            else:
                                return "Exit"

                print(event.pos, event.button)
        return "main_menu"

    def update(self, events):
        self.events = events
        self.new_window = self.event_handler()
        #if smth happens then return the window required
        return self.new_window #for now placeholder

    def draw(self):
        self.draw_background() #keep loading background
        self.draw_buttons() #keep loading buttons


    #should make a function that fixes sun appearing on both ends of the screen by scaling the image a bit larger than it already is

class Start(Button):
    def __init__(self, window, screen):
        super().__init__(window)
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]

    def update(self):
        return "start"


class ControlsMenu(Button):
    def __init__(self, window, screen):
        super().__init__(window)
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]

    def update(self):
        return "controls"



class SettingsMenu(Button):
    def __init__(self, window, screen):
        super().__init__(screen)
        self.window = window
        self.config = ConfigParser()
        self.screen_width, self.screen_height = screen[0][0], screen[0][1]

    def update(self):
        return "settings"

class ExitMenu:
    def __init__(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))


def main():
    pygame.init() #initiating pygame
    clock = pygame.time.Clock() #tool to control tick speed/fps/physics
    vector = pygame.math.Vector2  # import 2d assets from pygame
    default_win_res = (1920, 1080)
    window = pygame.display.set_mode(default_win_res)  # Menu(win_resolution) 1088 640
    manager = WindowManager(window)

    # loop to check if program is closed

    running = True
    while running:
        events = pygame.event.get()  # store events in a variable and updates it
        clock.tick(60) #sets tick speed and returns number of milliseconds passed from last time tick was called
        fps = clock.get_fps()
        dt = fps / 1000  # converting to seconds
        win_resolution = pygame.display.get_desktop_sizes()  # tuple of resolution set by windows #if more than one tuple then there is more than one display

        #print(f"{clock.tick(60)} and {fps} and {dt}") #check fps per second and dt value

        #default settings if not then grab from file
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        manager.update_window(events)
        manager.draw()
        pygame.display.flip()

        #print(win_resolution) hahahahah


if __name__ == "__main__":
    main()