function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
const cards = document.getElementsByClassName('card');

for (const card of cards) {
    const likeButton = card.querySelector('.btn-like');
    const dislikeButton = card.querySelector('.btn-dislike');
    const likeCounter = card.querySelector('.like-counter');
    const questionId = card.dataset.questionId;

    likeButton.addEventListener('click', async (event) => {
        event.preventDefault(); 
        await sendVote(questionId, true, likeCounter, likeButton, dislikeButton, 'question');
    });

    dislikeButton.addEventListener('click', async (event) => {
        event.preventDefault();
        await sendVote(questionId, false, likeCounter, likeButton, dislikeButton, 'question');
    });
}

const answerCards = document.getElementsByClassName('card-answer');

for (const card of answerCards) {
    const likeButton = card.querySelector('.btn-like');
    const dislikeButton = card.querySelector('.btn-dislike');
    const likeCounter = card.querySelector('.like-counter');
    const answerId = card.dataset.answerId;
    const checkbox = card.querySelector('.correct-checkbox');

    likeButton.addEventListener('click', async (event) => {
        event.preventDefault();
        await sendVote(answerId, true, likeCounter, likeButton, dislikeButton, 'answer');
    });

    dislikeButton.addEventListener('click', async (event) => {
        event.preventDefault();
        await sendVote(answerId, false, likeCounter, likeButton, dislikeButton, 'answer');
    });

    checkbox.addEventListener('click', async (event) => {
        await rateCorrect(answerId, checkbox.checked);
    });
}

async function sendVote(id, isUpvote, likeCounter, likeButton, dislikeButton, type) {
    try {
        const response = await fetch(`/${type}_like/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_upvote: isUpvote })
        });

        if (response.ok) {
            const data = await response.json();
            likeCounter.textContent = data.likes_count;

            if (isUpvote) {
                if (likeButton.classList.contains('active')) {
                    likeButton.classList.remove('active');
                } else {
                    likeButton.classList.add('active');
                    dislikeButton.classList.remove('active');
                }
            } else {
                if (dislikeButton.classList.contains('active')) {
                    dislikeButton.classList.remove('active');
                } else {
                    dislikeButton.classList.add('active');
                    likeButton.classList.remove('active');
                }
            }
        } else {
            console.error(`Error: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function rateCorrect(id, correctness) {
    try {
        const response = await fetch(`/answer/rate_correct/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ correctness: correctness })
        });

        if (response.ok) {
            return;
        } else {
            console.error(`Error: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
