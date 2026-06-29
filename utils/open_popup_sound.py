# popup_sound.py
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl


class PopupSound:
    def __init__(self, sound_path="sounds/openPopup.wav"):
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(sound_path))
        self.sound.setVolume(0.9)

    def play_openPopup(self):
        # Check sound file availability
        if self.sound.source().isEmpty():
            print("❌ No valid sound source loaded:", self.sound.source().toString())
            return
        
        self.sound.play()
