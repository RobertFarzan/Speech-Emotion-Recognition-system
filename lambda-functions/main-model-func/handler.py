import boto3
import tensorflow as tf
import json
import numpy as np
import os
import io
import librosa
import pickle

os.environ[ 'NUMBA_CACHE_DIR' ] = '/tmp/NUMBA_CACHE_DIR'
s3 = boto3.client('s3')

def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    wav_file = get_wavfile(bucket, key)
    model = get_ser_model()
    pred = make_prediction(model, wav_file)

    return pred


def get_ser_model():
    model_bucket = os.environ['SAVED_MODEL_BUCKET']
    json_filename = os.environ['MODEL_JSON']

    print('Downloading JSON file...')
    json_file_response = s3.get_object(Bucket=model_bucket, Key=json_filename)
    json_file = json_file_response['Body'].read().decode('utf-8')

    print('JSON file successfully downloaded...')

    model = load_tf_model(json_file)

    return model


def get_wavfile(bucket, key):

    print('Downloading WAV file...')
    response = s3.get_object(Bucket=bucket, Key=key)
    print('WAV file successfully downloaded...')

    return io.BytesIO(response['Body'].read())


def make_prediction(model, wav_file):
    mfcc = prepare_audiofile(wav_file)

    print('Model making prediction...')
    pred = model.predict(mfcc)
    result = np.argmax(pred, axis=1)
    print('SUCCESSFUL prediction: {}'.format(result[0]))

    lb = load_labels_object()
    result = lb.inverse_transform(result)[0]

    print('PARSED FINAL prediction: {}'.format(result))

    return result



def prepare_audiofile(wav_file):

    duration = float(os.environ['MAX_DURATION'])
    sampling_rate = int(os.environ['SAMPLING_RATE'])
    input_len = duration * sampling_rate

    mean, std = load_mean_std_parameters()

    print('Loading WAV file in Librosa...')
    data, sr = librosa.load(wav_file, sr = sampling_rate, duration= duration, offset=0.5)
    print('Waveform successfully loaded with Librosa...')

    if len(data) > input_len:
        max_offset = len(data) - input_len
        offset = np.random.randint(max_offset)
        data = data[offset:(input_len + offset)]
    else:
        if input_len > len(data):
            max_offset = input_len - len(data)
            offset = np.random.randint(max_offset)
        else:
            offset = 0
        data = np.pad(data, (offset, int(input_len) - len(data) - offset), 'constant')

    print('Extracting MFCC from waveform...')
    mfcc = librosa.feature.mfcc(data, sr=sampling_rate, n_mfcc=30)
    print('MFCC successfully extracted...')

    print('Standardizing MFCC...')
    mfcc_std = (mfcc - mean) / std
    print('MFCC successfully standardized...')

    mfcc_exp = np.expand_dims(mfcc_std, axis=(0, -1))

    return mfcc_exp

def load_tf_model(json_file):

    print('Reading Tensorflow model from JSON file...')
    loaded_model = tf.keras.models.model_from_json(json_file)
    print('Tensorflow model successfully loaded from JSON file...')

    #save h5 file on temporary folder to pass it to load_weights()
    tmp_file =  '/tmp/' + os.environ['MODEL_H5']
    
    print('Downloading H5 file...')
    if not os.path.isfile(tmp_file):
        s3.download_file(os.environ['SAVED_MODEL_BUCKET'], os.environ['MODEL_H5'], tmp_file)
        print('H5 file successfully downloaded...')
    else:
        print('H5 file already exists...')

    print('Loading Neural Network weights...')
    loaded_model.load_weights(tmp_file)
    print('Weights successfully loaded...')


    opt = tf.keras.optimizers.Adagrad(learning_rate=0.005, epsilon=1e-07) #Adam(learning_rate = lr_scheduler) #

    print('Compiling Tensorflow model...')
    loaded_model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    print('Tensorflow model successfully compiled...')

    return loaded_model

def load_mean_std_parameters():

    model_bucket = os.environ['SAVED_MODEL_BUCKET']
    
    print('Downloading NPY mean file...')
    mean_file = s3.get_object(Bucket=model_bucket, Key=os.environ['MODEL_MEAN'])
    print('NPY mean file successfully downloaded...')

    print('Loading mean Numpy array...')
    with io.BytesIO(mean_file['Body'].read()) as f:
        f.seek(0)  
        mean = np.load(f)
    print('Mean Numpy array successfully loaded...')

    print('Downloading NPY std file...')
    std_file = s3.get_object(Bucket=model_bucket, Key=os.environ['MODEL_STD'])
    print('NPY std file successfully downloaded...')

    print('Loading std Numpy array...')
    with io.BytesIO(std_file['Body'].read()) as f:
        f.seek(0)  
        std = np.load(f)
    print('Std Numpy array successfully loaded...')

    return (mean, std)

def load_labels_object():
    tmp_file = '/tmp/' + os.environ['MODEL_LABELS']
    
    print('Downloading LabelEncoder tempfile...')
    if not os.path.isfile(tmp_file):
        s3.download_file(os.environ['SAVED_MODEL_BUCKET'], os.environ['MODEL_LABELS'], tmp_file)
        print('LabelEncoder tempfile successfully downloaded...')
    else:
        print('LabelEncoder tempfile already exists...')

    file = open(tmp_file, 'rb')
    print('Loading LabelEncoder object with Pickle...')
    lb = pickle.load(file)
    file.close()
    print('LabelEncoder object successfully loaded...')
    
    return lb