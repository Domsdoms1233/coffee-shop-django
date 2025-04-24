document.addEventListener('DOMContentLoaded', function() {
    const foxcoinsCheckbox = document.getElementById('use_foxcoins');
    const foxcoinsInput = document.getElementById('foxcoins_input');
    const amountInput = document.querySelector('input[name="foxcoins_amount"]');
    
    if (foxcoinsCheckbox && foxcoinsInput && amountInput) {
        // Инициализация
        const maxAllowed = parseInt("{{ max_foxcoins }}");
        const available = parseInt("{{ request.user.foxcoins }}");
        
        foxcoinsCheckbox.addEventListener('change', function() {
            foxcoinsInput.classList.toggle('d-block', this.checked);
            foxcoinsInput.classList.toggle('d-none', !this.checked);
            
            if (this.checked) {
                amountInput.value = Math.min(maxAllowed, available);
            }
        });
        
        amountInput.addEventListener('input', function() {
            const value = parseInt(this.value) || 0;
            this.value = Math.min(Math.max(value, 1), maxAllowed, available);
        });
    }
});