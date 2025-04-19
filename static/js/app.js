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

const answersContainer = document.getElementById("answers-container");

if (answersContainer) {
    answersContainer.addEventListener('click', async function(event) {
        if (event.target.matches('.btn-like')) {
            const card = event.target.closest('.card-answer');
            const answerId = card.dataset.answerId;
            const likeCounter = card.querySelector('.like-counter');
            const dislikeButton = card.querySelector('.btn-dislike');
            event.preventDefault();
            await sendVote(answerId, true, likeCounter, event.target, dislikeButton, 'answer');
        }

        if (event.target.matches('.btn-dislike')) {
            const card = event.target.closest('.card-answer');
            const answerId = card.dataset.answerId;
            const likeCounter = card.querySelector('.like-counter');
            const likeButton = card.querySelector('.btn-like');
            event.preventDefault();
            await sendVote(answerId, false, likeCounter, likeButton, event.target, 'answer');
        }

        if (event.target.matches('.correct-checkbox')) {
            const card = event.target.closest('.card-answer');
            const answerId = card.dataset.answerId;
            await rateCorrect(answerId, event.target.checked);
        }
    });
}

const questionsContainers = document.getElementsByClassName("card");

Array.from(questionsContainers).forEach(function(card) {
    card.addEventListener('click', async function(event) {
        // Ваш код обработки клика
        if (event.target.matches('.btn-like')) {
            const questionId = card.dataset.questionId;
            const likeCounter = card.querySelector('.like-counter');
            const dislikeButton = card.querySelector('.btn-dislike');
            event.preventDefault();
            await sendVote(questionId, true, likeCounter, event.target, dislikeButton, 'question');
        }
    
        if (event.target.matches('.btn-dislike')) {
            const questionId = card.dataset.questionId;
            const likeCounter = card.querySelector('.like-counter');
            const likeButton = card.querySelector('.btn-like');
            event.preventDefault();
            await sendVote(questionId, false, likeCounter, likeButton, event.target, 'question');
        }
    });
});


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
                likeButton.classList.toggle('active');
                dislikeButton.classList.remove('active');
            } else {
                dislikeButton.classList.toggle('active');
                likeButton.classList.remove('active');
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

