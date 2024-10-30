const body = document.querySelector('body');
const darkmodeBtn = document.getElementById('darkmodeBtn');

// ローカルストレージからテーマを取得して設定
let mode = localStorage.getItem('mode');

if (mode === 'dark') {
    body.classList.add('dark');
} else {
    body.classList.remove('dark');
}

darkmodeBtn.addEventListener('click', () => {
    body.classList.toggle('dark');
    mode = body.classList.contains('dark') ? 'dark' : 'normal';
    localStorage.setItem('mode', mode);
});
