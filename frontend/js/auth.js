// Toggle Password Visibility
function togglePassword(inputId, iconElement) {
    const input = document.getElementById(inputId);
    const icon = iconElement.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    } else {
        input.type = 'password';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    }
}

// Password Strength Meter
const regPassword = document.getElementById('regPassword');
if (regPassword) {
    regPassword.addEventListener('input', function() {
        const val = this.value;
        const strengthBar = document.getElementById('strengthBar');
        const strengthText = document.getElementById('strengthText');
        
        strengthBar.className = 'strength-bar'; // reset classes
        
        if (val.length === 0) {
            strengthBar.style.width = '0';
            strengthText.textContent = 'Password strength';
            strengthText.className = 'text-muted strength-text';
        } else if (val.length < 6) {
            strengthBar.classList.add('strength-weak');
            strengthText.textContent = 'Weak';
            strengthText.className = 'text-danger strength-text';
        } else if (val.length < 10 || !/\d/.test(val) || !/[a-zA-Z]/.test(val)) {
            strengthBar.classList.add('strength-medium');
            strengthText.textContent = 'Medium (Use letters & numbers)';
            strengthText.className = 'text-warning strength-text';
        } else {
            strengthBar.classList.add('strength-strong');
            strengthText.textContent = 'Strong';
            strengthText.className = 'text-success strength-text';
        }
    });
}

// Utility: Simulate API Call loading
function simulateApiCall(button, callback) {
    const btnText = button.querySelector('.btn-text');
    const spinner = button.querySelector('.spinner-border');
    
    // UI state loading
    button.disabled = true;
    spinner.classList.remove('d-none');
    
    setTimeout(() => {
        // UI state normal
        button.disabled = false;
        spinner.classList.add('d-none');
        callback();
    }, 1500); // Simulate 1.5s delay
}

// Form Validation Logic
const forms = document.querySelectorAll('form');

Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
        event.preventDefault();
        event.stopPropagation();
        
        let isValid = true;
        
        // Custom validations
        
        // 1. Password Match (Register)
        if (form.id === 'registerForm') {
            const pwd = document.getElementById('regPassword');
            const confirmPwd = document.getElementById('confirmPassword');
            if (pwd && confirmPwd) {
                if (pwd.value !== confirmPwd.value) {
                    confirmPwd.setCustomValidity("Passwords do not match.");
                    isValid = false;
                } else {
                    confirmPwd.setCustomValidity("");
                }
                
                // Password length
                if (pwd.value.length > 0 && pwd.value.length < 6) {
                    pwd.setCustomValidity("Must be at least 6 characters.");
                    isValid = false;
                } else {
                    pwd.setCustomValidity("");
                }
            }
        }
        
        // HTML5 Validation
        if (!form.checkValidity() || !isValid) {
            form.classList.add('was-validated');
            return; // Stop here if invalid
        }
        
        // If Valid, Simulate API call
        const submitBtn = form.querySelector('button[type="submit"]');
        simulateApiCall(submitBtn, () => {
            if (form.id === 'forgotPasswordForm') {
                form.classList.add('d-none');
                document.getElementById('successMessage').classList.remove('d-none');
            } else if (form.id === 'loginForm') {
                window.location.href = 'dashboard.html';
            } else if (form.id === 'registerForm') {
                window.location.href = 'login.html';
            }
        });

    }, false);
    
    // Live validation as user types
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            if (form.classList.contains('was-validated')) {
                // If form was already validated once, check on input to update UI live
                input.checkValidity();
                
                // Specific check for confirm password live
                if (input.id === 'confirmPassword' || input.id === 'regPassword') {
                    const pwd = document.getElementById('regPassword');
                    const confirmPwd = document.getElementById('confirmPassword');
                    if (confirmPwd && pwd) {
                        if (pwd.value !== confirmPwd.value) {
                            confirmPwd.setCustomValidity("Passwords do not match.");
                        } else {
                            confirmPwd.setCustomValidity("");
                        }
                    }
                }
            }
        });
    });
});
