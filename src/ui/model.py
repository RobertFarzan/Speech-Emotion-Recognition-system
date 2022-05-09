import os
import time
import shutil
import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread

from config.values import TMPDIR, EMO_TMPFILE
from recorder.audio_listener import AudioListener
from emotions.handler import EmotionResponses

logger = logging.getLogger(__name__)

class Model(QObject):

    def __init__(self):
        super(Model, self).__init__()
        self._isRunning = True

    def setup(self):
        if not os.path.isdir(TMPDIR):
            os.mkdir(TMPDIR)
    
        csvpath = os.path.join(TMPDIR, EMO_TMPFILE)
    
        if os.path.isfile(csvpath) and EmotionResponses.timestamp == 0:
            os.remove(csvpath)

    @staticmethod
    def wipe_files():
        logger.info(f"Cleaning up {TMPDIR} directory")
        if os.path.isdir(TMPDIR): # delete tmp folder and all its contents
            shutil.rmtree(TMPDIR)

    def run(self):
        self.model()
    
    def model(self):

        self.emo_thread = None
        self.audio_thread = None

        self.setup()

        try:
            self.emo_thread = EmotionResponses()
            self.audio_thread = AudioListener(10)

            self.emo_thread.start()
            self.audio_thread.start()

            while self.emo_thread.is_alive() and self.audio_thread.is_alive():
                time.sleep(1)

            if not self.audio_thread.is_alive():
                self.emo_thread.stopped.set()
    
        except (KeyboardInterrupt, SystemExit):
            
            if self.emo_thread:
                self.emo_thread.stopped.set()
            if self.audio_thread:
                self.audio_thread.stopped.set()
                
            logger.info("Forced exiting")

        finally:
            
            if self.emo_thread and self.emo_thread.is_alive():
                self.emo_thread.stopped.set()
                self.emo_thread.join()
            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.stopped.set()
                self.audio_thread.join()

        logger.info("Recording stopped")

    def stop(self):
        self._isRunning = False

        if self.emo_thread:
            self.emo_thread.stopped.set()
        if self.audio_thread:
            self.audio_thread.stopped.set()

        if self.emo_thread and self.emo_thread.is_alive():
            self.emo_thread.join()
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()