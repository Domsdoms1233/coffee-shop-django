document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех модулей
    initCartModule();
    initMessagesModule();
    initProductFormModule();
    
    // Проверяем, находимся ли мы на странице админки
    if (document.querySelector('.admin-page')) {
        initAdminModule();
    }
});

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
   МОДУЛЬ АДМИН-ПАНЕЛИ
   ====================== */
function initAdminModule() {
    // Переключение вкладок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            document.querySelectorAll('.tab-btn, .tab-content').forEach(el => {
                el.classList.remove('active');
            });
            this.classList.add('active');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });

    // Инициализация модулей управления
    initProductManagement();
    initCategoryManagement();
    initModals();
    initImageUpload();
}

function initProductManagement() {
    const productForm = document.getElementById('product-form');
    const cancelBtn = document.getElementById('cancel-edit');
    
    if (!productForm) return;

    // Редактирование продукта
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.id;
            fetch(`/api/products/${productId}/`)
                .then(response => response.json())
                .then(product => {
                    document.getElementById('product-id').value = product.id;
                    document.getElementById('product-name').value = product.name;
                    document.querySelector('[name="price"]').value = product.price;
                    document.querySelector('[name="category"]').value = product.category;
                    document.querySelector('[name="description"]').value = product.description;
                    document.getElementById('product-available').checked = product.available;
                    
                    if (product.image_url) {
                        document.getElementById('image-name').textContent = 'Изображение загружено';
                    }
                    
                    productForm.querySelector('button[type="submit"]').innerHTML = 
                        '<i class="fas fa-save"></i> Обновить';
                    if (cancelBtn) cancelBtn.style.display = 'inline-block';
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('Ошибка при загрузке данных', 'error');
                });
        });
    });

    // Отмена редактирования
    if (cancelBtn) {
        cancelBtn.addEventListener('click', resetProductForm);
    }

    // Удаление продукта
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.id;
            showConfirmModal('Удалить этот кофе?', () => {
                fetch(`/api/products/${productId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => {
                    if (response.ok) {
                        document.querySelector(`tr[data-id="${productId}"]`).remove();
                        showMessage('Кофе удален', 'success');
                    } else {
                        throw new Error('Ошибка удаления');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('Ошибка при удалении', 'error');
                });
            });
        });
    });

    // Обработка формы продукта
    productForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const productId = formData.get('product_id');
        const method = productId ? 'PUT' : 'POST';
        const url = productId ? `/api/products/${productId}/` : '/api/products/';

        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';
        submitBtn.disabled = true;

        fetch(url, {
            method: method,
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                updateProductRow(data);
                resetProductForm();
                showMessage(productId ? 'Кофе обновлен' : 'Кофе добавлен', 'success');
            } else if (data.errors) {
                showMessage('Исправьте ошибки в форме', 'error');
                console.error(data.errors);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Ошибка при сохранении', 'error');
        })
        .finally(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    });
}

function initCategoryManagement() {
    const categoryForm = document.getElementById('category-form');
    
    if (!categoryForm) return;

    // Обработка формы категории
    categoryForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';
        submitBtn.disabled = true;

        fetch('/api/categories/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                updateCategoryRow(data);
                this.reset();
                showMessage('Категория добавлена', 'success');
            } else if (data.errors) {
                showMessage('Исправьте ошибки в форме', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Ошибка при сохранении', 'error');
        })
        .finally(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    });

    // Редактирование категории
    document.querySelectorAll('.btn-edit-category').forEach(btn => {
        btn.addEventListener('click', function() {
            const categoryId = this.dataset.id;
            const row = this.closest('tr');
            const name = row.querySelector('td').textContent;
            
            const newName = prompt('Введите новое название категории:', name);
            if (newName && newName !== name) {
                fetch(`/api/categories/${categoryId}/`, {
                    method: 'PUT',
                    body: JSON.stringify({name: newName}),
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.id) {
                        row.querySelector('td').textContent = data.name;
                        showMessage('Категория обновлена', 'success');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('Ошибка при обновлении', 'error');
                });
            }
        });
    });

    // Удаление категории
    document.querySelectorAll('.btn-delete-category').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.disabled) return;
            
            const categoryId = this.dataset.id;
            showConfirmModal('Удалить эту категорию?', () => {
                fetch(`/api/categories/${categoryId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => {
                    if (response.ok) {
                        document.querySelector(`tr[data-id="${categoryId}"]`).remove();
                        showMessage('Категория удалена', 'success');
                    } else {
                        throw new Error('Ошибка удаления');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('Ошибка при удалении', 'error');
                });
            });
        });
    });
}

function initImageUpload() {
    const fileInput = document.getElementById('product-image');
    if (!fileInput) return;

    fileInput.addEventListener('change', function() {
        const fileName = this.files[0]?.name || 'Выберите файл';
        document.getElementById('image-name').textContent = fileName;
        
        // Показ превью
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                let preview = document.querySelector('.image-preview');
                if (!preview) {
                    preview = document.createElement('div');
                    preview.className = 'image-preview';
                    document.querySelector('.image-upload-wrapper').appendChild(preview);
                }
                preview.innerHTML = `<img src="${e.target.result}" alt="Превью">`;
            };
            reader.readAsDataURL(this.files[0]);
        }
    });
}

function initModals() {
    const modal = document.getElementById('confirm-modal');
    if (!modal) return;

    // Закрытие модального окна
    modal.querySelector('.close').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    const cancelBtn = document.getElementById('cancel-delete');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // Закрытие при клике вне окна
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

function showConfirmModal(message, callback) {
    const modal = document.getElementById('confirm-modal');
    if (!modal) return;

    const confirmMessage = document.getElementById('confirm-message');
    if (confirmMessage) confirmMessage.textContent = message;
    
    const confirmBtn = document.getElementById('confirm-delete');
    if (confirmBtn) {
        confirmBtn.onclick = function() {
            callback();
            modal.style.display = 'none';
        };
    }

    modal.style.display = 'block';
}

function resetProductForm() {
    const form = document.getElementById('product-form');
    if (form) {
        form.reset();
        document.getElementById('product-id').value = '';
        document.getElementById('image-name').textContent = 'Выберите файл';
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.innerHTML = '<i class="fas fa-save"></i> Сохранить';
        
        const preview = document.querySelector('.image-preview');
        if (preview) preview.innerHTML = '';
    }
    
    const cancelBtn = document.getElementById('cancel-edit');
    if (cancelBtn) cancelBtn.style.display = 'none';
}

function updateProductRow(product) {
    let row = document.querySelector(`.products-table tr[data-id="${product.id}"]`);
    
    if (!row) {
        // Создаем новую строку если продукт новый
        const tbody = document.querySelector('.products-table tbody');
        if (tbody) {
            row = document.createElement('tr');
            row.dataset.id = product.id;
            row.innerHTML = `
                <td>${product.name}</td>
                <td>${product.category_name || ''}</td>
                <td>${product.price} ₽</td>
                <td>
                    <span class="status-badge ${product.available ? 'available' : 'unavailable'}">
                        ${product.available ? 'Доступен' : 'Не доступен'}
                    </span>
                </td>
                <td class="actions">
                    <button class="btn btn-edit" data-id="${product.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-delete" data-id="${product.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        }
    } else {
        // Обновляем существующую строку
        const cells = row.querySelectorAll('td');
        cells[0].textContent = product.name;
        cells[1].textContent = product.category_name || '';
        cells[2].textContent = `${product.price} ₽`;
        
        const badge = cells[3].querySelector('.status-badge');
        if (badge) {
            badge.className = `status-badge ${product.available ? 'available' : 'unavailable'}`;
            badge.textContent = product.available ? 'Доступен' : 'Не доступен';
        }
    }
}

function updateCategoryRow(category) {
    let row = document.querySelector(`.categories-table tr[data-id="${category.id}"]`);
    
    if (!row) {
        // Создаем новую строку если категория новая
        const tbody = document.querySelector('.categories-table tbody');
        if (tbody) {
            row = document.createElement('tr');
            row.dataset.id = category.id;
            row.innerHTML = `
                <td>${category.name}</td>
                <td>0</td>
                <td class="actions">
                    <button class="btn btn-edit-category" data-id="${category.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-delete-category" data-id="${category.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        }
    } else {
        // Обновляем существующую строку
        const nameCell = row.querySelector('td');
        if (nameCell) nameCell.textContent = category.name;
    }
}

/* ======================
   МОДУЛЬ КОРЗИНЫ
   ====================== */
function initCartModule() {
    // Ваш существующий код корзины
    // ...
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

/* ======================
   МОДУЛЬ ФОРМЫ ДОБАВЛЕНИЯ ТОВАРА (без изменений)
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