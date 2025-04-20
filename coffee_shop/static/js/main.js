document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех модулей
    initCartModule();
    initMessagesModule();
    initProductFormModule();
});

/* ======================
   МОДУЛЬ КОРЗИНЫ
   ====================== */
function initCartModule() {
    // Добавление в корзину
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', handleAddToCart);
    });
    
    // Обновляем счетчик при загрузке
    updateCartCounter();
}

function handleAddToCart(e) {
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
            updateCartCounter();
            showMessage('Товар добавлен в корзину', 'success');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showMessage('Ошибка при добавлении в корзину', 'error');
    });
}

function updateCartCounter() {
    fetch('/cart/count/')
    .then(response => response.json())
    .then(data => {
        const counterElements = document.querySelectorAll('.cart-count');
        counterElements.forEach(el => {
            el.textContent = data.count;
        });
    })
    .catch(error => console.error('Error updating cart count:', error));
}

/* ======================
   МОДУЛЬ СООБЩЕНИЙ
   ====================== */
function initMessagesModule() {
    // Закрытие сообщений по клику
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('close-message')) {
            e.target.closest('.message').remove();
        }
    });
}

function showMessage(text, type = 'success') {
    const container = document.querySelector('.messages-container') || createMessageContainer();
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        info: 'info-circle'
    };

    const message = document.createElement('div');
    message.className = `message message-${type}`;
    message.innerHTML = `
        <div class="message-content">
            <i class="fas fa-${icons[type] || 'info-circle'}"></i>
            ${text}
            <button class="close-message">&times;</button>
        </div>
    `;
    
    container.appendChild(message);
    setTimeout(() => message.remove(), 5000);
}

function createMessageContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    document.body.appendChild(container);
    return container;
}

/* ======================
   МОДУЛЬ ФОРМЫ ДОБАВЛЕНИЯ ТОВАРА
   ====================== */
function initProductFormModule() {
    const productForm = document.getElementById('add_product_form');
    if (!productForm) return;

    initImageUpload();
    initCategoryManagement();
}

function initImageUpload() {
    const imageInput = document.getElementById('id_image');
    if (!imageInput) return;

    const uploadArea = document.querySelector('.upload-area');
    const fileName = document.getElementById('file-name');

    imageInput.addEventListener('change', function() {
        updateFileDisplay(this.files);
    });

    // Drag and Drop
    ['dragover', 'dragleave', 'drop'].forEach(event => {
        uploadArea.addEventListener(event, function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (event === 'dragover') {
                uploadArea.classList.add('dragover');
            } else if (event === 'dragleave') {
                uploadArea.classList.remove('dragover');
            } else if (event === 'drop') {
                uploadArea.classList.remove('dragover');
                imageInput.files = e.dataTransfer.files;
                updateFileDisplay(e.dataTransfer.files);
            }
        });
    });

    function updateFileDisplay(files) {
        fileName.textContent = files.length ? files[0].name : 'Выберите файл';
        uploadArea.classList.toggle('has-file', files.length > 0);
    }
}

function initCategoryManagement() {
    const addBtn = document.getElementById('add-category-btn');
    if (!addBtn) return;

    const modal = document.getElementById('category-modal');
    const form = document.getElementById('category-form');

    addBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    document.querySelector('.close-modal').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitCategoryForm(this);
    });
}

function submitCategoryForm(form) {
    fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addCategoryToSelect(data.id, data.name);
            form.reset();
            document.getElementById('category-modal').style.display = 'none';
            showMessage(`Категория "${data.name}" добавлена`, 'success');
        }
    })
    .catch(error => {
        console.error('Error adding category:', error);
        showMessage('Ошибка при добавлении категории', 'error');
    });
}

function addCategoryToSelect(id, name) {
    const select = document.getElementById('id_category');
    const option = new Option(name, id);
    select.add(option);
    select.value = id;
}

/* ======================
   ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
   ====================== */
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