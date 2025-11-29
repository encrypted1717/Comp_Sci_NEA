import pygame
from core.window_manager import WindowManager
from core.config_manager import ConfigManager

def main():
    pygame.init() #initiating pygame
    clock = pygame.time.Clock() #tool to control tick speed/fps/physics
    vector = pygame.math.Vector2  # import 2d assets from pygame
    #check if user settings are already created
    config_manager = ConfigManager()
    if config_manager.open_file("assets\\game_settings\\config_user.ini"):
        config = config_manager.get_config()
        screen_width = config.getint("Graphics", "Screen_Width")
        screen_height = config.getint("Graphics", "Screen_Height")
    else:
        screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
        config_manager.set_value({"Graphics": {"Screen_Width": screen_width, "Screen_Height": screen_height}})

    window = pygame.display.set_mode((screen_width, screen_height))

    # WindowManager handles everything to do with the windows (i.e. switching/creating/deleting windows)
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