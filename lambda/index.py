import json
import os
import boto3
import re
from botocore.exceptions import ClientError
import urllib.request
from urllib.error import HTTPError, URLError

# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"

bedrock_client = None

MODEL_API_URL = os.environ.get("MODEL_API_URL", "https://668e-34-126-102-232.ngrok-free.app/generate")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        print("User message:", message)

        prompt = ""
        for msg in conversation_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                prompt += f"ユーザー: {content}\n"
            elif role == "assistant":
                prompt += f"アシスタント: {content}\n"
        prompt += f"ユーザー: {message}\nアシスタント:"

        payload = {
            "prompt": prompt,
            "max_new_tokens": 100,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        print("Sending request to custom model API")
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(MODEL_API_URL, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")

        try:
            with urllib.request.urlopen(req) as res:
                response_data = json.loads(res.read().decode("utf-8"))
        except HTTPError as e:
            raise Exception(f"Model API error: {e.code}, {e.read().decode('utf-8')}")
        except URLError as e:
            raise Exception(f"Failed to reach server: {e.reason}")

        assistant_response = response_data["generated_text"]

        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": assistant_response})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": conversation_history
            })
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
