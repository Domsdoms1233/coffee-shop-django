document.addEventListener('DOMContentLoaded', function() {
    // Добавление в корзину
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartCount();
                    showMessage('Товар добавлен в корзину', 'success');
                }
            });
        });
    });
    
    // Закрытие сообщений
    document.querySelectorAll('.close-message').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
});

function updateCartCount() {
    fetch('/cart/count/')
    .then(response => response.json())
    .then(data => {
        document.querySelector('.cart-count').textContent = data.count;
    });
}

function showMessage(text, type) {
    const container = document.querySelector('.messages-container') || createMessagesContainer();
    const message = document.createElement('div');
    message.className = `message message-${type}`;
    message.innerHTML = `
        ${text}
        <button class="close-message">&times;</button>
    `;
    container.appendChild(message);
    
    message.querySelector('.close-message').addEventListener('click', function() {
        message.remove();
    });
    
    setTimeout(() => {
        message.remove();
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    document.querySelector('main').prepend(container);
    return container;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}