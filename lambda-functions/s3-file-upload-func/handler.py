import logging
import base64
import uuid
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

response  = {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    },
    'body': ''
}

def lambda_handler(event, context):

    file_name = uuid.uuid4().hex + '.wav'
    file_content = base64.b64decode(event['content'])
    
    print(event['content'])
    BUCKET_NAME = os.environ['BUCKET_NAME']

    try:
        s3_response = s3_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=file_content)   
        logger.info('S3 Response: {}'.format(s3_response))
        response['body'] = {'file_path': file_name}

        return response

    except Exception as e:
        raise IOError(e)
