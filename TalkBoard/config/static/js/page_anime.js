document.addEventListener("DOMContentLoaded", function () {
    const content = document.getElementById("content");
    const links = document.querySelectorAll("a"); // 適宜対象を変更

    links.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault(); // 通常の遷移を防ぐ
            const targetUrl = this.href;

            // スライドアウト
            content.classList.add("slide-out");

            // アニメーション後に遷移
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 500); // アニメーション時間と合わせる

            // ページがロードされたらスライドインを開始
            setTimeout(() => {
                content.classList.add("slide-in");
            }, 700); // 遅延を入れるとより自然
        });
    });
});



