document.addEventListener('DOMContentLoaded', function () {
    // Обновление количества при изменении
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function () {
            this.form.submit();
        });
    });

    // Подтверждение удаления товара
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            if (!confirm('Вы уверены, что хотите удалить этот товар из корзины?')) {
                e.preventDefault();
            }
        });
    });
});