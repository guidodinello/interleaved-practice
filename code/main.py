import json
import logging
import random
import time
import tkinter as tk
from datetime import date

from sound import AudioController

logging.basicConfig(
    filename=f"./log/{date.today().isoformat()}",
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
)

ASSETS_FOLDER = "assets"
SOUNDS_FOLDER = f"{ASSETS_FOLDER}/sounds"

FONT = "Helvetica"
HUNDRERD_MINUTES_MS = 6_000_000

# PARAMETERS
# - The time interval for the timer is set.
TIME_BETWEEN_ALERTS_MU = 600  # s = 10 minutes. testing=5
TIME_BETWEEN_ALERTS_STD = 70  # s = 1 minute 10 seconds. testing=1

BREAK_DURATION = 10_000  # The duration of the break in ms (10s).
BREAK_DURATION_HOURS = BREAK_DURATION / 3_600_000  # The duration of the break in hours.


class GUI:
    def __init__(self):
        self.load_translations(language="english")

        self.root = tk.Tk()
        self.root.title(self.translations["title"])

        # Set the size and position of the window
        window_width, window_height = 300, 180
        x_coordinate, y_coordinate = 1500, 100
        self.root.geometry(
            f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}"
        )

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True)

        self.btn = tk.Button(
            self.frame,
            text=self.translations["btn_start"],
            command=self.btn_handler,
            bg="lightgreen",
        )
        self.text = tk.Label(
            self.frame,
            text=self.translations["header_start"],
            font=(FONT, 16, "bold"),
            pady=10,
        )
        self.info = tk.Label(
            self.frame,
            text=self.translations["info_start"],
            font=(FONT, 12),
            pady=8,
            wraplength=250,
        )

        self.text.pack()
        self.info.pack()
        self.btn.pack()

        self.practice_stage_callback = None
        self.break_stage_callback = None
        self.practice_start_timestamp = 0

        self.white_controller = AudioController(
            f"{SOUNDS_FOLDER}/white_noise_track.wav"
        )
        self.white_controller.set_volume(0)
        self.brown_controller = AudioController(
            f"{SOUNDS_FOLDER}/brown_noise_track.wav"
        )
        self.brown_controller.set_volume(1)

    def break_stage(self):
        # play relaxing brown noise
        self.white_controller.pause()
        self.brown_controller.play()

        self.btn.pack_forget()
        self.text.config(text=self.translations["header_break"])
        self.info.config(text=self.translations["info_break"])

        # Schedule the next practice session
        self.practice_stage_callback = self.root.after(
            BREAK_DURATION,
            self.practice_stage,
        )

    def practice_stage(self):
        # play concentration noise
        self.brown_controller.pause()
        self.white_controller.play()

        self.btn.config(text=self.translations["btn_pause"], bg="lightskyblue")
        self.btn.pack()
        self.text.config(text=self.translations["header_practicing"])
        self.info.config(text=self.translations["info_practicing"])

        self.practice_start_timestamp = time.time()
        # Schedule the next break, ms
        self.break_stage_callback = self.root.after(
            self.time_to_practice, self.break_stage
        )

    def brac_alert(self):
        if self.break_stage_callback is not None:
            self.root.after_cancel(self.break_stage_callback)
        if self.practice_stage_callback is not None:
            self.root.after_cancel(self.practice_stage_callback)

        self.btn.config(text=self.translations["btn_brac"], bg="lightpink1")
        self.text.config(text=self.translations["header_brac"])
        self.info.config(text=self.translations["info_brac"])
        self.btn.pack()

    def btn_handler(self):
        if self.btn.cget("text") == self.translations["btn_start"]:
            # basic rest–activity cycle (BRAC) 90–110 minutes. We'll use 100 minutes as a middle ground.
            self.root.after(HUNDRERD_MINUTES_MS, self.brac_alert)

            time_to_practice = random.gauss(
                mu=TIME_BETWEEN_ALERTS_MU, sigma=TIME_BETWEEN_ALERTS_STD
            )
            self.time_to_practice = int(time_to_practice * 1000)  # to ms
            self.practice_stage()

        elif self.btn.cget("text") == self.translations["btn_pause"]:
            self.btn.config(text=self.translations["btn_resume"], bg="lightpink1")
            self.text.config(text=self.translations["header_paused"])
            self.info.config(text=self.translations["info_paused"])
            self.white_controller.pause()

            # Cancel the scheduled break
            if self.break_stage_callback is not None:
                self.root.after_cancel(self.break_stage_callback)

            # Calculate remaining time and store it
            self.time_to_practice = int(
                max(
                    self.time_to_practice
                    - (time.time() - self.practice_start_timestamp) * 1000,
                    0,
                )
            )

        elif self.btn.cget("text") == self.translations["btn_resume"]:
            self.btn.config(text=self.translations["btn_pause"], bg="lightskyblue")
            self.text.config(text=self.translations["header_practicing"])
            self.info.config(text=self.translations["info_practicing"])
            self.white_controller.resume()

            self.practice_stage()

        elif self.btn.cget("text") == self.translations["btn_brac"]:
            self.root.destroy()

    def run(self):
        self.root.mainloop()

    def load_translations(self, language="english"):
        with open(
            f"{ASSETS_FOLDER}/translations/{language}.json", "r", encoding="utf-8"
        ) as f:
            self.translations = json.load(f)


if __name__ == "__main__":
    try:
        gui = GUI()
        gui.run()
    except Exception as e:
        logging.error(e)
        raise e
