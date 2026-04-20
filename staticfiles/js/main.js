document.addEventListener('DOMContentLoaded', function() {
    // 1. Password Visibility Toggle
    const toggleIcons = document.querySelectorAll('.toggle-password-icon');
    toggleIcons.forEach(icon => {
        icon.addEventListener('click', function() {
            // Find the sibling input within the same input-group
            const inputGroup = this.closest('.input-group');
            const input = inputGroup.querySelector('input.toggle-password-input');
            
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.classList.remove('bi-eye');
                    this.classList.add('bi-eye-slash');
                } else {
                    input.type = 'password';
                    this.classList.remove('bi-eye-slash');
                    this.classList.add('bi-eye');
                }
            }
        });
    });

    // 2. Form validation and button loading state
    const forms = document.querySelectorAll('form.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Custom validations for register form
            if (form.id === 'registerForm') {
                const passInput = form.querySelector('#regPassword');
                const confirmInput = form.querySelector('#regConfirmPassword');
                const termsCheckbox = form.querySelector('#id_terms');
                
                // Reset custom validities
                passInput.setCustomValidity('');
                confirmInput.setCustomValidity('');
                termsCheckbox.setCustomValidity('');
                
                // Check password length
                if (passInput.value.length < 8) {
                    passInput.setCustomValidity('Password must be at least 8 characters long.');
                    isValid = false;
                }
                
                // Check password match
                if (passInput.value !== confirmInput.value) {
                    confirmInput.setCustomValidity('Passwords do not match.');
                    isValid = false;
                }
                
                // Check terms
                if (!termsCheckbox.checked) {
                    termsCheckbox.setCustomValidity('You must agree to the terms and conditions.');
                    isValid = false;
                }
            }
            
            if (!form.checkValidity() || !isValid) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Form is valid, show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
                    submitBtn.disabled = true;
                    // We must let the form submit normally, so we don't preventDefault here
                    // However, if we disable the button right away, sometimes it prevents submission depending on browser.
                    // A safer way is to delay disabling or let the form submit naturally while visually showing loading.
                }
            }
            
            form.classList.add('was-validated');
        });
    });
});
