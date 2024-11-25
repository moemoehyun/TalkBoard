document.addEventListener("DOMContentLoaded", function() {
    const loadingScreen = document.querySelector('.loading-screen');
    const logo = document.querySelector('.logo');
    const mainContent = document.querySelector('.main-content');
  
    // ロゴのアニメーションが終わった時に処理を実行
    logo.addEventListener('animationend', function() {
      // ローディング画面をフェードアウト
      loadingScreen.style.opacity = '0';
  
      // フェードアウトが終了したらメインコンテンツを表示
      setTimeout(function() {
        // メインコンテンツを表示
        mainContent.classList.add('show');
      }, 1000); // フェードアウトの時間と合わせる
    });
  });
  