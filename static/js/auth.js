
document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.setAttribute('data-theme', savedTheme);
        darkModeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }
    
    darkModeToggle.addEventListener('click', function() {
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        darkModeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    });
    
    // Form validation
    const form = document.querySelector('.auth-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Email validation
        if (!emailInput.value.includes('@')) {
            showError(emailInput, 'Please enter a valid email address');
            isValid = false;
        } else {
            clearError(emailInput);
        }
        
        // Password validation
        if (passwordInput.value.length < 6) {
            showError(passwordInput, 'Password must be at least 6 characters long');
            isValid = false;
        } else {
            clearError(passwordInput);
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
    
    // Add floating animation to form inputs
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateY(-2px)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateY(0)';
        });
    });
});

function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleButton = document.querySelector('.toggle-password');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.textContent = '🙈';
    } else {
        passwordInput.type = 'password';
        toggleButton.textContent = '👁️';
    }
}

function showError(input, message) {
    clearError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '0.25rem';
    
    input.parentElement.appendChild(errorDiv);
    input.style.borderColor = '#dc3545';
}

function clearError(input) {
    const errorMessage = input.parentElement.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
    input.style.borderColor = 'var(--border-color)';
}
