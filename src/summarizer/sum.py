import threading
import pandas as pd
import tempfile
import logging
import os

from config.values import TMPDIR, EMO_TMPFILE

logger = logging.getLogger(__name__)

class Summarizer():
 
    def __init__(self):
        super().__init__()
 
    def read_from_csv(self):

        csvpath = os.path.join(TMPDIR, EMO_TMPFILE)
        if not os.path.isfile(csvpath):
            logger.exception(f"File {EMO_TMPFILE} not found in {TMPDIR}")
            return

        df = pd.read_csv(csvpath)

        values = df['emotion'].value_counts().keys().tolist()
        counts = df['emotion'].value_counts().tolist()
        sumcounts = sum(counts)
        avgs = [(c/sumcounts)*100 for c in counts]
        #df['emotion'].value_counts().plot(kind='barh')

        return (values, avgs)
        
