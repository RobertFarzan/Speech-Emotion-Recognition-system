import json
import boto3

response  = {
    'statusCode': 204,
    'body': json.dumps("No emotion")
}

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='speech-emotion-sqs')

def lambda_handler(event, context):
    
    for message in queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=0):
        body = json.loads(message.body)
        message.delete()
        response['body'] = json.dumps(body['responsePayload'])
        response['statusCode'] = 200
        
        return response
        
    # if no message is found in the queue
    
    response['statusCode'] = 204
    response['body'] = json.dumps("No emotion")
    
    return response
