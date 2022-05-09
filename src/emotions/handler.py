import threading
import requests
import logging
import json
import csv
import os

from config.values import EMO_TMPFILE, TMPDIR, SLICE_SECONDS, API_GET_URL, API_KEY

logger = logging.getLogger(__name__)

class EmotionResponses(threading.Thread):
    
    timestamp = 0

    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        #self.timestamp = 0 # for sequencing the responses in the time dimension
 
    def run(self):
        
        while not self.stopped.wait(SLICE_SECONDS):
            emotion_req = requests.get(API_GET_URL, headers={'x-api-key': API_KEY}).json()

            if emotion_req['statusCode'] == 200:
                msg = emotion_req['body'].strip('"')
                logger.info(f"Emotion: {msg}")
                self._save_to_csv(msg)      

    def _save_to_csv(self, emotion):

        csvpath = os.path.join(TMPDIR, EMO_TMPFILE)
        if not os.path.isfile(csvpath): # if the file doesn't exist we need to write the csv header
            with open(csvpath, 'w', newline='') as f:
                hwriter = csv.writer(f)
                hwriter.writerow(["timestamp", "emotion"]) # write header
        
        with open(csvpath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([EmotionResponses.timestamp, emotion])
            EmotionResponses.timestamp += SLICE_SECONDS