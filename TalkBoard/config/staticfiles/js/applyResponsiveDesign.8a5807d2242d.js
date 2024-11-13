function applyResponsiveDesign() {
    console.log("現在の画面幅:", window.innerWidth);
    if (window.innerWidth <= 768) {
        // モバイルビュー
        document.body.classList.add("mobile-view");
        document.body.classList.remove("desktop-view");
    } else {
        // デスクトップビュー
        document.body.classList.add("desktop-view");
        document.body.classList.remove("mobile-view");
    }
}

applyResponsiveDesign();
window.addEventListener("resize", applyResponsiveDesign);
