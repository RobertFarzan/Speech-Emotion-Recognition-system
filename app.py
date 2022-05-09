import os
import sys
import logging

from PyQt5 import QtWidgets

from config.values import TMPDIR, EMO_TMPFILE
from recorder.audio_listener import AudioListener
from emotions.handler import EmotionResponses
from ui.window import MainWindow

def setLogger():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )   

if __name__ == "__main__":
    
    setLogger()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Breeze')
    app.setApplicationName("Speech Emotion Recognition")
    w = MainWindow()
    app.aboutToQuit.connect(w.close_event)

    w.show()
    app.exec_()