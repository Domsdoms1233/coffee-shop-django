document.addEventListener('DOMContentLoaded', function() {
    // Инициализация модуля сообщений
    initMessagesModule();
    
    // Инициализация превью изображений
    initImageUpload();
    
    // Инициализация админ-панели если есть на странице
    if (document.querySelector('.admin-page')) {
        initAdminModule();
    }
});

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

    // Подтверждение удаления
    document.querySelectorAll('form.delete-form').forEach(form => {
        const deleteBtn = form.querySelector('button[type="submit"]');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function(e) {
                if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                    e.preventDefault();
                }
            });
        }
    });
}

/* ======================
   МОДУЛЬ ЗАГРУЗКИ ИЗОБРАЖЕНИЙ
   ====================== */
function initImageUpload() {
    const imageInput = document.getElementById('id_image');
    if (!imageInput) return;

    imageInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                let previewContainer = document.querySelector('.image-preview');
                if (!previewContainer) {
                    previewContainer = document.createElement('div');
                    previewContainer.className = 'image-preview mt-2';
                    imageInput.parentNode.appendChild(previewContainer);
                }
                
                let preview = previewContainer.querySelector('img');
                if (!preview) {
                    preview = document.createElement('img');
                    preview.style.maxWidth = '200px';
                    preview.style.maxHeight = '200px';
                    preview.style.borderRadius = '4px';
                    preview.style.border = '1px solid #ddd';
                    previewContainer.appendChild(preview);
                }
                
                preview.src = e.target.result;
            };
            reader.readAsDataURL(this.files[0]);
        }
    });
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