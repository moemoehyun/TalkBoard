document.addEventListener('DOMContentLoaded', () => {
    const likeButtons = document.querySelectorAll('.like-button');

    likeButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // ページリロードを防止
            const boardId = button.dataset.boardId;

            fetch(`/favorite-toggle/${boardId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }

                // ボタンの状態を動的に更新
                if (data.is_favorite) {
                    button.classList.add('btn-primary');
                    button.classList.remove('btn-outline-primary');
                    button.querySelector('i').classList.add('bi-heart-fill');
                    button.querySelector('i').classList.remove('bi-heart');
                } else {
                    button.classList.add('btn-outline-primary');
                    button.classList.remove('btn-primary');
                    button.querySelector('i').classList.add('bi-heart');
                    button.querySelector('i').classList.remove('bi-heart-fill');
                }

                // いいねカウントを更新
                button.querySelector('span').textContent = data.favorite_count;
            })
            .catch(error => console.error('Error:', error));
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const repostButtons = document.querySelectorAll('.repost-button');

    repostButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const boardId = button.dataset.boardId;

            // 確認ダイアログを表示
            const confirmRepost = confirm("この投稿をリポストしますか？");
            if (!confirmRepost) {
                return; // ユーザーがキャンセルした場合は終了
            }

            fetch(`/repost-toggle/${boardId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }

                // リポストの状態を更新
                const repostCountElement = button.querySelector('.repost-count');
                if (data.is_reposted) {
                    button.classList.add('reposted');
                } else {
                    button.classList.remove('reposted');
                }

                // カウント部分を更新
                if (repostCountElement) {
                    repostCountElement.textContent = data.repost_count;
                }
            })
            .catch(error => console.error('エラー:', error));
        });
    });
});