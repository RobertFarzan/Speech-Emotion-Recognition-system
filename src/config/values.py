import os
import tempfile
# Recording params
RATE   = 16000
CHUNK  = 1024
SLICE_SECONDS = 2
WNDSIZE = 8
RECORD_SECS = 2
NCHANNELS = 2

# Paths
TMPDIR = tempfile.TemporaryDirectory(prefix="ser-").name #os.path.join(os.path.abspath('src'), 'tmp')
EMO_TMPFILE = 'emotions.csv'

# AWS API Gateway
API_POST_URL = 'https://9dprlp99gl.execute-api.eu-west-1.amazonaws.com/v1/upload-wavs'
API_GET_URL = 'https://9dprlp99gl.execute-api.eu-west-1.amazonaws.com/v1/prediction'
API_KEY = 'uFsgbmen4J4Y25lmInWlp5vWbIZiOAGrafMKmPOG'
CONTENT_TYPE = 'audio/x-wav'