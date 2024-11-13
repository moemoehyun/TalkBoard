const body = document.querySelector('body');
const darkmodeBtn = document.getElementById('darkmodeBtn');

// ローカルストレージからテーマを取得して設定
let mode = localStorage.getItem('mode');

// 初期設定: ローカルストレージからテーマを読み込む
if (mode === 'dark') {
    body.classList.add('dark');  // ダークモードの場合
} else {
    body.classList.remove('dark');  // 通常モードの場合
}

// ダークモードのトグルボタンにイベントリスナーを追加
if (darkmodeBtn) {
    darkmodeBtn.addEventListener('click', () => {
        body.classList.toggle('dark');  // ダークモードを切り替える
        mode = body.classList.contains('dark') ? 'dark' : 'normal';  // 現在のモードを取得
        localStorage.setItem('mode', mode);  // モードをローカルストレージに保存
    });
} else {
    console.error("Dark mode button not found!");
}
