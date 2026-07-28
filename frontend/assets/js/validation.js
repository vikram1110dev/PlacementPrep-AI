/**
 * Global Form Validation
 */

class Validation {
    static init() {
        // Fetch all forms that we want to apply custom Bootstrap validation styles to
        const forms = document.querySelectorAll('.needs-validation');

        Array.prototype.slice.call(forms)
            .forEach(function (form) {
                form.addEventListener('submit', function (event) {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                        // Optional: Show a global toast error
                        if(window.showToast) {
                            window.showToast('error', 'Please fill out all required fields correctly.');
                        }
                    } else {
                        // Prevent actual submission for frontend mockup
                        event.preventDefault();
                        if(window.showToast) {
                            window.showToast('success', 'Form submitted successfully!');
                        }
                    }
                    form.classList.add('was-validated');
                }, false);
            });
    }

    static isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    static isValidPassword(password) {
        // Min 8 chars, 1 letter, 1 number
        return /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/.test(password);
    }
}

document.addEventListener('DOMContentLoaded', () => Validation.init());
