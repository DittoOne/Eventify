document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Re-enable button after 3 seconds in case of error
                setTimeout(function() {
                    submitBtn.disabled = false;
                    if (submitBtn.classList.contains('btn-primary')) {
                        submitBtn.innerHTML = 'Login';
                    } else if (submitBtn.classList.contains('btn-success')) {
                        submitBtn.innerHTML = 'Register';
                    }
                }, 3000);
            }
        });
    });
    
    // Form validation
    const passwordField = document.getElementById('password');
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            if (this.value.length < 6) {
                this.setCustomValidity('Password must be at least 6 characters long');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});