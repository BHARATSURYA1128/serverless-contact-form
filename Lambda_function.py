import json
import boto3
import uuid
import os

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

table_name = os.environ['DYNAMO_TABLE']
sender_email = os.environ['SENDER_EMAIL']
recipient_email = os.environ['RECIPIENT_EMAIL']

def lambda_handler(event, context):
    # ✅ Handle preflight OPTIONS request
    if event['requestContext']['http']['method'] == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "https://d3iq4nve8vtmki.cloudfront.net",
                "Access-Control-Allow-Headers": "content-type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps("Preflight OK")
        }

    try:
        data = json.loads(event['body'])
        name = data['name']
        email = data['email']
        message = data['message']

        table = dynamodb.Table(table_name)
        table.put_item(Item={
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'message': message
        })

        ses.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': f"New Contact from {name}"},
                'Body': {'Text': {'Data': f"Name: {name}\nEmail: {email}\nMessage: {message}"}}
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "https://d3iq4nve8vtmki.cloudfront.net",
                "Access-Control-Allow-Headers": "content-type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({"message": "Message sent successfully!"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "https://d3iq4nve8vtmki.cloudfront.net",
                "Access-Control-Allow-Headers": "content-type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({"error": str(e)})
        }
