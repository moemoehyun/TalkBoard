document.addEventListener("DOMContentLoaded", function() {
    const loadingScreen = document.querySelector('.loading-screen');
    const logo = document.querySelector('.logo');
    const mainContent = document.querySelector('.main-content');

    const isFirstVisit = localStorage.getItem('firstVisit') === null;
    
    // 初めての訪問の場合
    if (isFirstVisit) {
    // ロゴのアニメーションが終わった時に処理を実行
        logo.addEventListener('animationend', function() {
        // ローディング画面をフェードアウト
        loadingScreen.style.opacity = '0';
    
        // フェードアウトが終了したらメインコンテンツを表示
        setTimeout(function() {
            // メインコンテンツを表示
            loadingScreen.classList.add('hide'); // ローディング画面を完全に非表示にする
            mainContent.classList.add('show');
        }, 1000); // フェードアウトの時間と合わせる
        
        });
    }else {
        // 再訪問の場合はローディング画面をすぐに非表示にしてメインコンテンツを表示
        loadingScreen.classList.add('hide');
        mainContent.classList.add('show');
      }
});

  