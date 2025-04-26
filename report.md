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
詳しくは，[ここ](https://github.com/Taiga10969/lecture-ai-engineering/blob/master/day1/03_FastAPI/README.md) に記載してあります．


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
