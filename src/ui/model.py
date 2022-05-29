import os
import time
import shutil
import logging
import threading

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, QThread

from config.values import TMPDIR, EMO_TMPFILE
from recorder.audio_listener import AudioListener
from emotions.handler import EmotionResponses
from summarizer.sum import Summarizer

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm, colors

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

class SummaryWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        
        #self.save_button = QtWidgets.QPushButton('Save to PNG')
        #self.save_button.clicked.connect(self._save_to_png)
        #self.save_button.setEnabled(True)

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        emo, counts = Summarizer().read_from_csv()

        colormap = self._apply_color_map(emo)

        self.ax.bar(emo, counts, color=colormap)
        self.ax.set_xlabel('Emotion')
        self.ax.set_ylabel("% of time")
        self.ax.axes.xaxis.set_visible(True)
        self.ax.axes.yaxis.set_visible(True)
        self._add_label(emo, counts)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        #layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.show()
        self.canvas.draw()

    def _apply_color_map(self, emo):
        cmap = cm.get_cmap('viridis')
        norm = colors.Normalize(vmin=0.0, vmax=6.0)

        names_colors = {'sadness': 0, 'fear': 1, 'disgust': 2, 'anger': 3, 'neutral': 4, 'surprise': 5, 'happiness': 6}
        sort_colors = [cmap(norm(names_colors[e])) for e in emo]

        return sort_colors

    def _add_label(self, emo, counts):

        labels = [str(round(c, 2)) + '%' for c in counts]
        for i in range(len(emo)):
            self.ax.text(i, counts[i]//2, labels[i], ha = 'center', color='white')

    def _save_to_png(self):
        pass