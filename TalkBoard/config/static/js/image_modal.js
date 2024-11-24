document.addEventListener("DOMContentLoaded", function () {
    // モーダル要素を取得
    const modal = document.getElementById("imageModal");
    const modalImage = document.getElementById("modalImage");
    const closeBtn = document.querySelector(".close");

    // modal、modalImage、closeBtn が正しく取得できているか確認
    if (modal && modalImage && closeBtn) {
        // 投稿画像をクリックした時
        document.querySelectorAll(".post-image").forEach((image) => {
            image.addEventListener("click", function () {
                modal.style.display = "block"; // モーダルを表示
                modalImage.src = this.src; // クリックした画像をモーダルに表示
            });
        });

        // 閉じるボタンをクリックした時
        closeBtn.addEventListener("click", function () {
            modal.style.display = "none"; // モーダルを非表示
        });

        // モーダルの外側をクリックした時
        modal.addEventListener("click", function (e) {
            if (e.target === modal) {
                modal.style.display = "none"; // モーダルを非表示
            }
        });
    } else {
        console.error("モーダル要素が見つかりません。");
    }
});
