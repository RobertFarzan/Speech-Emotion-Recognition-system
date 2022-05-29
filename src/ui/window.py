import os
import sys
import numpy as np
import pandas as pd
import datetime
import logging

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, QSize

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import FuncFormatter
from matplotlib import cm, colors

from config.values import WNDSIZE, SLICE_SECONDS, TMPDIR, EMO_TMPFILE
from summarizer.sum import Summarizer
from ui.model import Model, SummaryWindow

logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.sumw = None
        self.fig = Figure()
        self.ax = None
        self.worker = None
        self.canvas = FigureCanvas(self.fig)
        self.button = QtWidgets.QPushButton('Start')
        self.button.clicked.connect(self.animate)
        self.button.clicked.connect(self.run_model)

        self.sum_button = QtWidgets.QPushButton('Summary')
        self.sum_button.clicked.connect(self.summarize)
        self.sum_button.setEnabled(False)
        
        # set the layouts
        innerLayout = QtWidgets.QHBoxLayout()
        innerLayout.addWidget(self.button)
        innerLayout.addWidget(self.sum_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(innerLayout)
        #layout.addWidget(self.button)
        self.setLayout(layout)

        self.show()
    
    def run_model(self):

        if self.button.text() == "Start":
            self.button.setText("Stop")
            self.sum_button.setEnabled(False)

            self.thread = QThread()
            self.worker = Model()

            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()
        
        elif self.button.text() == "Stop":
            self.button.setText("Start")
            self.sum_button.setEnabled(True)

            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def animate(self):
        plt.style.use('seaborn')
        
        if self.ax is None:
            self.ax = self.fig.add_subplot(111)  # create an axis
            self.ax2 = self.ax.twinx() # emoji ticks
            self.ax2.grid(None)
        else:
            self.ax.cla()
            self.ax2.cla()
            self.ax.axes.xaxis.set_visible(True)
            self.ax.axes.yaxis.set_visible(True)
            self.ax2.axes.yaxis.set_visible(True)
            self.ax2.grid(None)

        self.ani = FuncAnimation(self.fig, self.animate_loop, interval=SLICE_SECONDS*1000)
        self.canvas.draw()

    def animate_loop(self, i):

        if not os.path.exists(os.path.join(TMPDIR, EMO_TMPFILE)):
            self.ax.cla()
            self.ax.text(0.95, 0.01, 'Waiting COLD START...', verticalalignment='bottom', horizontalalignment='right', color='red', fontsize=15)
            return

        df = pd.read_csv(os.path.join(TMPDIR, EMO_TMPFILE))
        i = df.shape[0]

        if i > WNDSIZE: # num_rows > 10
            df = df.iloc[i - WNDSIZE: , :]

        cmap = cm.get_cmap('viridis')
        norm = colors.Normalize(vmin=0.0, vmax=6.0)

        names_colors = {'sadness': 0, 'fear': 1, 'disgust': 2, 'anger': 3, 'neutral': 4, 'surprise': 5, 'happiness': 6}
        emojis = {'$\U00002639$': 0, '$\U0001F628$': 1, '$\U0001F637$': 2, '$\U0001F620$': 3, '$\U0001F610$': 4, '$\U0001F632$': 5, '$\U0001F603$': 6}
        sort_names = [names_colors[e] for e in df['emotion']]
        sort_colors = [cmap(norm(names_colors[e])) for e in df['emotion']] # sort_colors = [names_colors[e][1] for e in df['emotion']]
        yvals = np.arange(len(names_colors))

        self.ax.cla()
        timeTicks = lambda sec, pos: str(datetime.timedelta(seconds=sec))[2:7]
        xfmt = FuncFormatter(timeTicks)
        self.ax.xaxis.set_major_formatter(xfmt)

        self.ax.barh(sort_names, SLICE_SECONDS, left=df['timestamp'], color=sort_colors, height=0.5)
        self.ax.set_yticks(yvals, list(names_colors.keys()), rotation=25)
        #self.ax2.set_yticks(yvals, list(emojis.keys()))
        self.ax2.set_yticks(np.linspace(self.ax2.get_yticks()[0], self.ax2.get_yticks()[-1], len(self.ax.get_yticks())), list(emojis.keys()))
        plt.tight_layout()

    def summarize(self):
        self.button.setEnabled(False)
        self.sumw = SummaryWindow()
        self.sumw.show()
        self.button.setEnabled(True)
        

    def close_event(self):
        logger.info("Exiting program")
        
        if self.worker is not None:
            self.worker.stop()
        
        Model.wipe_files()
        sys.exit(0)