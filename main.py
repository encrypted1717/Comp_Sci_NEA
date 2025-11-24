import pygame
from core.window_manager import WindowManager
from utils.config_setup import Configuration

def main():
    pygame.init() #initiating pygame
    clock = pygame.time.Clock() #tool to control tick speed/fps/physics
    vector = pygame.math.Vector2  # import 2d assets from pygame
    #check if user settings are already created
    config = Configuration()
    screen_width, screen_height = config.get_screen()

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