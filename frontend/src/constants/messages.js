// =====================================
// src/constants/messages.js
// =====================================

export const messages = {
    // 必須項目エラー
    required: '{name}は必須です',

    // 文字数制限
    maxLength: '{name}は{max}文字以内で入力してください',
    minLength: '{name}は{min}文字以上で入力してください',

    // 認証関連
    auth: {
        loginFailed:
            'ログインに失敗しました。ユーザー名またはパスワードが正しくありません。',
        invalidCredentials: 'ユーザー名またはパスワードが違います',
        sessionExpired:
            'セッションの有効期限が切れました。再度ログインしてください。',
    },

    // フィールド名
    fields: {
        username: 'ユーザー名',
        password: 'パスワード',
        email: 'メールアドレス',
        name: '名前',
        phone: '電話番号',
    },

    // パターンマッチ
    pattern: {
        email: '正しいメールアドレスの形式で入力してください',
        phone: '正しい電話番号の形式で入力してください',
        alphaNumeric: '英数字のみで入力してください',
    },
};
