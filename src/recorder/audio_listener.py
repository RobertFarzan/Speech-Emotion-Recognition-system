import threading
import pyaudio
import requests
import tempfile
import logging
import time
import wave
import os

from config.values import RATE, CHUNK, SLICE_SECONDS, TMPDIR, NCHANNELS, API_KEY, CONTENT_TYPE, API_POST_URL

logger = logging.getLogger(__name__)

class AudioListener(threading.Thread):
 
    def __init__(self, record_seconds):
        
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.p = pyaudio.PyAudio()
        self.record_seconds = record_seconds
 
    def run(self):

        stream = self.p.open(format=pyaudio.paInt16, channels=2, rate=RATE, input=True, frames_per_buffer=CHUNK)
        sthreads = []

        # tstart = time.perf_counter()
        while not self.stopped.is_set(): # and time.perf_counter()-tstart < self.record_seconds: # records during record_seconds secs
            frames = []

            for i in range(int(RATE / CHUNK * SLICE_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            audio_sender = threading.Thread(target=self._upload_wav_api, args=(frames,))
            audio_sender.start()
            sthreads.append(audio_sender)

        #actions to take before interruption handling
        for t in sthreads:
            t.join()
            
        stream.stop_stream()
        stream.close()
        self.p.terminate()

 
    def _upload_wav_api(self, audio_data):
    
        wav_file = self._generate_wav_file(audio_data)
        
        start = time.perf_counter()
        self._send_post_request(wav_file)
        end = time.perf_counter()

        logger.info(f"File {os.path.split(wav_file)[1]} uploaded to API GATEWAY in {end-start}s") #print(f"Archivo subido a API GATEWAY en {end-start}s")
        

    def _generate_wav_file(self, audio_data):
        
        #filename = uuid.uuid4().hex + '.wav' # genera nombres de fichero casi aleatorios
        #filepath = os.path.join(TMPDIR, filename)
        filepath = tempfile.NamedTemporaryFile(mode="wb", dir=TMPDIR, suffix=".wav", delete=False)

        wf = wave.open(filepath.name, 'wb')
        wf.setnchannels(NCHANNELS)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_data))
        wf.close()
        filepath.close()

        return filepath.name

    def _send_post_request(self, wav_file):
        
        headers = {
            'x-api-key': API_KEY,
            'Content-Type': CONTENT_TYPE
        }

        data = open(wav_file, 'rb').read()
        post = requests.post(API_POST_URL, headers=headers, data=data)

        return post.text


