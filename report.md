# 📄 レポート：AIエンジニアリング実践講座2025 第2回 宿題

このレポートでは，【AIエンジニアリング実践講座2025】第2回の宿題（演習課題）の実施内容をまとめています．<br>
第2回の宿題では，AWSからFastAPIで立てたLLMにアクセスして回答を生成しています．<br>
ここでは，AWS上で変更を加えた点についてまとめた．<br>

## 🙋 基本情報

- **Omnicampus アカウント名**：`taiga10969`  
- **名前**：増田大河
--- 

### [2] 講義内の演習の実施
UIを改良し，`MODEL_ID:us.amazon.nova-lite-v1:0`を実行したときの結果を以下に示します．<br>
また，`MODEL_ID:us.amazon.nova-micro-v1:0`も実行し動作を確認した．<br>
▼実行結果

<img src="https://github.com/Taiga10969/simplechat/blob/main/report/%E7%94%BB%E9%9D%A2%E5%8F%8E%E9%8C%B2%202025-04-25%2016.56.59.gif" alt="" width="500" />

### [3] アプリケーションの修正による独自モデルの利用

使用したモデル：`elyza/ELYZA-japanese-CodeLlama-7b-instruct`<br>
7bもの大きさのモデルをGoogle Colaboratory（無料枠）でも動作させるためには，量子化してモデルをロードする工夫をしている．<br>
詳しくは，[ここ](https://github.com/Taiga10969/lecture-ai-engineering/blob/master/day1/03_FastAPI/README.md) に記載してあります．<br>

この独自モデルを利用するために，`./lambda/index.py`をFastAPIにアクセスするように変更した．変更点を最後に示す．<br>
▼実行結果

<img src="https://github.com/Taiga10969/simplechat/blob/main/report/%E7%94%BB%E9%9D%A2%E5%8F%8E%E9%8C%B2-2025-04-26-23.22.17.gif" alt="" width="500" />

▼`elyza/ELYZA-japanese-CodeLlama-7b-instruct`が生成したmatplotlibのコードの実行結果

<img src="https://github.com/Taiga10969/simplechat/blob/main/report/%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%202025-04-26%2023.27.50.png" alt="" width="500" />

### [+α] UIの改善
1. `Enter` を押すと変換の確定にも関わらずメッセージが送られてしまう問題を解決 (APP.js)
   <br>
    ```
    <form onSubmit={handleSubmit} className="input-form">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="メッセージを入力..."
        disabled={loading}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            //handleSubmit(e);
          }
        }}
      />
      <button type="submit" disabled={loading || !input.trim()}>
        🐯送信
      </button>
    </form>
    ```
2. `CSS`の改善
   CSSを適宜変更し，🐯イメージ（自分の名前Taigaから来ている笑）に変更しました！

---

### 補足資料 (`./lambda/index.py`の変更点）
```
MODEL_API_URL = os.environ.get("MODEL_API_URL", "https://c7a2-34-138-10-164.ngrok-free.app/generate")

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
```

