# lambda/index.py
import json
import os
import boto3
import re  # 正規表現モジュールをインポート
from botocore.exceptions import ClientError
import requesrt

# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"  # デフォルト値

# グローバル変数としてクライアントを初期化（初期値）
bedrock_client = None

# モデルID
#MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")

# FastAIPのエンドポイント
MODEL_API_URL = os.environ.get("MODEL_API_URL", "https://d987-34-126-102-232.ngrok-free.app/generate")

# Fast API用
def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # 認証ユーザー情報の取得（あれば）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディの取得
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        print("User message:", message)

        # プロンプトの生成（シンプルに履歴を連結）
        prompt = ""
        for msg in conversation_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                prompt += f"ユーザー: {content}\n"
            elif role == "assistant":
                prompt += f"アシスタント: {content}\n"
        prompt += f"ユーザー: {message}\nアシスタント:"

        # 独自モデルAPIにPOSTリクエストを送信
        payload = {
            "prompt": prompt,
            "max_new_tokens": 100,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        print("Sending request to custom model API")
        response = requests.post(MODEL_API_URL, json=payload, headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        if response.status_code != 200:
            raise Exception(f"Model API error: {response.status_code}, {response.text}")

        response_data = response.json()
        assistant_response = response_data["generated_text"]

        # 会話履歴に応答を追加
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
