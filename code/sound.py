from just_playback import Playback


class AudioController:
    def __init__(self, sound_path):
        self.audio = Playback()
        self.audio.load_file(sound_path)
        self.audio.loop_at_end(True)

    def play(self):
        self.audio.play()

    def pause(self):
        self.audio.pause()

    def resume(self):
        self.audio.resume()

    def set_volume(self, volume):
        self.audio.set_volume(volume)
