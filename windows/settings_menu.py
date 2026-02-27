import pygame
from core.window import Window
from core.button import Button
from core.config_manager import ConfigManager


#TODO Introduce more settings
class SettingsMenu(Window):
    def __init__(self, display, renderer):
        super().__init__(display, renderer)

        # Setup Configs
        self.config_manager = ConfigManager("assets\\game_settings\\config_user.ini")
        self.config = self.config_manager.get_config()
        self.changed = False # Whether any settings have been changed

        # Resolution setting setup
        self.resolutions = pygame.display.list_modes()
        # TODO could try first getting it from ini file
        self.resolution = self.display.get_size() # Get real window resolution
        # Display mode setup
        self.display_modes = ("Fullscreen", "Borderless_Windowed", "Windowed")
        self.display_mode = self.config.get("Window", "Display_Mode")
        # FPS setup
        self.fps_values = ("30", "60", "120", "144", "165", "185", "240", "360", "Unlimited") # Unlimited normally is represented by a 0 or empty parameter on the clock
        self.fps = self.config.get("Window", "FPS")
        # Button setup
        self.__back_btn = Button(
            (150, 120),
            (160, 60),
            "Back",
            pygame.font.Font(self.fonts["OldeTome"], 37),
            "#ffffff",
            '#000000',
            5,
            border_colour = "#000000",
            offset_y = 4,
            action = "back",
            hover_text_colour = "#000000",
            hover_rect_colour = "#ffffff",
            hover_border_colour = "#000000",
            fill_on_hover = True
        )

        self.__graphics_label = Button(
            (self.center_x, 120),
            (235, 70),
            "Graphics",
            pygame.font.Font(self.fonts["OldeTome"], 56),
            '#ffffff',
            '#000000',
            offset_y = 4
        )

        self.__resolution_label = Button(
            (780, 350),
            (300, 60),
            "Resolution",
            pygame.font.Font(self.fonts["OldeTome"], 37),
            '#ffffff',
            '#000000',
            offset_y = 4
        )

        self.__resolution_btn = Button(
            (1180, 350),
            (380, 60),
            f"{self.resolution[0]} x {self.resolution[1]}",
            pygame.font.Font(self.fonts["GothicPixel"], 16),
            '#000000',
            '#ffffff',
            5,
            border_colour = "#000000",
            offset_y = 4,
            action = "cycle_resolution",
            hover_text_colour = "#ffffff",
            hover_rect_colour = "#000000",
            hover_border_colour = "#ffffff",
            fill_on_hover = True
        )

        self.__display_mode_label = Button(
            (780, 440),
            (300, 60),
            "Display_Mode",
            pygame.font.Font(self.fonts["OldeTome"], 37),
            '#ffffff',
            '#000000',
            offset_y=4
        )

        self.__display_mode_btn = Button(
            (1180, 440),
            (380, 60),
            self.display_mode,
            pygame.font.Font(self.fonts["GothicPixel"], 16),
            '#000000',
            '#ffffff',
            5,
            border_colour = "#000000",
            offset_y = 4,
            action = "cycle_display_modes",
            hover_text_colour = "#ffffff",
            hover_rect_colour = "#000000",
            hover_border_colour = "#ffffff",
            fill_on_hover = True
        )
        self.__fps_label = Button(
            (780, 530),
            (300, 60),
            "FPS",
            pygame.font.Font(self.fonts["OldeTome"], 37),
            '#ffffff',
            '#000000',
            offset_y=4
        )

        self.__fps_btn = Button(
            (1180, 530),
            (380, 60),
            self.fps,
            pygame.font.Font(self.fonts["GothicPixel"], 16),
            '#000000',
            '#ffffff',
            5,
            border_colour="#000000",
            offset_y=4,
            action="cycle_fps",
            hover_text_colour="#ffffff",
            hover_rect_colour="#000000",
            hover_border_colour="#ffffff",
            fill_on_hover=True
        )

        self.__apply_btn = Button(
            (1770, 960),
            (160, 60),
            "Apply",
            pygame.font.Font(self.fonts["GothicPixel"], 16),
            '#000000',
            '#ffffff',
            5,
            border_colour="#000000",
            offset_y=4,
            action="apply",
            hover_text_colour="#ffffff",
            hover_rect_colour="#000000",
            hover_border_colour="#ffffff",
            fill_on_hover=True
        )

        # noinspection PyTypeChecker
        self.buttons.add(
            self.__back_btn,
            self.__graphics_label,
            self.__resolution_label,
            self.__resolution_btn,
            self.__display_mode_label,
            self.__display_mode_btn,
            self.__fps_label,
            self.__fps_btn
        )

    def event_handler(self, events):
        # Unless a setting has changed then apply button won't appear
        if self.changed and not self.buttons.has(self.__apply_btn):
            self.buttons.add(self.__apply_btn)
        elif not self.changed and self.buttons.has(self.__apply_btn):
            self.buttons.remove(self.__apply_btn)

        for event in events:
            # kb press down
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
            for btn in self.buttons:
                action = btn.handle_event(event)

                if action == "cycle_resolution":
                    self.resolution = self.__cycle_setting(self.resolution, self.resolutions)
                    self.__resolution_btn.update_text(f"{self.resolution[0]} x {self.resolution[1]}")
                    return None

                if action == "cycle_display_modes":
                    self.display_mode = self.__cycle_setting(self.display_mode, self.display_modes)
                    self.__display_mode_btn.update_text(self.display_mode)
                    return None

                if action == "cycle_fps":
                    self.fps = self.__cycle_setting(self.fps, self.fps_values)
                    self.__fps_btn.update_text(self.fps)
                    return None

                if action == "apply":
                    self.config_manager.set_values({
                        "Graphics":
                            {
                                "Screen_Width": self.resolution[0],
                                "Screen_Height": self.resolution[1]
                            },
                        "Window":
                            {
                                "Display_Mode": self.display_mode,
                                "FPS": self.fps
                            }
                    })

                    self.buttons.remove(self.__apply_btn)
                    self.changed = False
                    return "apply_display"

                elif action:
                    return action
        return None

    def __cycle_setting(self, setting, values):
        """
        Cycles through 'values'. If 'setting' is not currently in 'values',
        it falls back to values[0] instead of throwing.
        """
        if not values: # there are no values
            # TODO log the fact no values were found?
            return setting

        try:
            current_index = values.index(setting)
        except ValueError:
            current_index = -1  # force to 0 on next line

        next_index = (current_index + 1) % len(values) # TODO Explain why this line works
        new_setting = values[next_index]

        if not self.changed:
            self.changed = True

        return new_setting

    def draw(self, dt):
        self.surface.fill((255, 255, 255)) # White background
        super().draw(dt)