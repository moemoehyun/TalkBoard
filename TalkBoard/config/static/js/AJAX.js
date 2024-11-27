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
