import os
import json
import boto3
import uuid
from google.oauth2 import id_token
from google.auth.transport import requests

CLIENT_ID = "1068374517657-oaqifgr0mrhvaj65vs3lff7r71d26f7n.apps.googleusercontent.com"

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME'] # set by cloudformation
table = dynamodb.Table(table_name)

def handler(event, context):
    print(event)
    try:
        # Parse JSON body
        body = json.loads(event["body"])
        token = body.get("idToken")
        
        if not token:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "idToken: is required in body"})
            }
        
        # Call Google service to validate JWT
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        sub = idinfo['sub']
        email = idinfo['email']
        user_uuid = str(uuid.uuid4())

        # Update the database
        table.put_item(Item={"email": email, "uuid": user_uuid})

        # TODO/FIX the cookie options
        return {
            "cookies": [
                f"session={user_uuid}; Secure=true; SameSite=Lax; Path=/",
                f"user={sub}; Secure=true; SameSite=Lax; Path=/; Max-Age=31536000"
            ],
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": 'no-cache="Set-Cookie"'
            },
            "body": json.dumps({"message": "Session created", "idToken": token, "uuid":user_uuid})
        }
    
    except ValueError as e:
        print(f"Error {e}")
        return {
            "statusCode": 401,
            "headers": { "Content-Type": "application/json" },
            "body": f"Error: {e}"
        } 
