[2] 講義内の演習の実施
UIを改良し，`MODEL_ID:us.amazon.nova-lite-v1:0`を実行したときの結果を以下に示します．<br>
また，`MODEL_ID:us.amazon.nova-micro-v1:0`も実行し動作を確認した．<br>
▼実行結果

<img src="https://github.com/Taiga10969/simplechat/blob/main/report/%E7%94%BB%E9%9D%A2%E5%8F%8E%E9%8C%B2%202025-04-25%2016.56.59.gif" alt="" width="500" />

[3] アプリケーションの修正による独自モデルの利用

使用したモデル：``



[+α] UIの改善
1. `Enter` を押すと変換の確定にも関わらずメッセージが送られてしまう問題を解決 (APP.js)
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
2. 