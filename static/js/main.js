document.addEventListener("DOMContentLoaded", () => {
    const themeToggleBtn = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;

    const sunIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    const moonIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';

    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);
    if(themeToggleBtn) themeToggleBtn.innerHTML = savedTheme === 'dark' ? sunIcon : moonIcon;

    if(themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeToggleBtn.innerHTML = newTheme === 'dark' ? sunIcon : moonIcon;
        });
    }

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in-up').forEach((el) => {
        observer.observe(el);
    });
});

const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('passwordInput');
    const eyeIcon = document.getElementById('eyeIcon');

    if (togglePassword && passwordInput && eyeIcon) {
        togglePassword.addEventListener('click', function () {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
            } else {
                passwordInput.type = 'password';
                eyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
            }
        });
    }

const userTypeSelect = document.getElementById('userTypeSelect');
    const companyField = document.getElementById('companyField');
    const inviteCodeField = document.getElementById('inviteCodeField');

    if (userTypeSelect && companyField && inviteCodeField) {
        userTypeSelect.addEventListener('change', function() {
            if (this.value === 'kurumsal_admin') {
                companyField.style.display = 'block';
                inviteCodeField.style.display = 'none';
            } else {
                companyField.style.display = 'none';
                inviteCodeField.style.display = 'block';
            }
        });
    }

    const toggleRegPassword = document.getElementById('toggleRegPassword');
    const regPasswordInput = document.getElementById('regPasswordInput');
    const regEyeIcon = document.getElementById('regEyeIcon');

    if (toggleRegPassword && regPasswordInput && regEyeIcon) {
        toggleRegPassword.addEventListener('click', function () {
            if (regPasswordInput.type === 'password') {
                regPasswordInput.type = 'text';
                regEyeIcon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
            } else {
                regPasswordInput.type = 'password';
                regEyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
            }
        });
    }

    const strengthBar = document.getElementById('passwordStrengthBar');
    const strengthText = document.getElementById('passwordStrengthText');
    const submitBtn = document.getElementById('registerSubmitBtn');

    if (regPasswordInput && strengthBar && strengthText && submitBtn) {
        regPasswordInput.addEventListener('input', function() {
            const val = regPasswordInput.value;
            let strength = 0;

            if (val.length >= 8) strength += 25; 
            if (val.match(/[a-z]+/)) strength += 25; 
            if (val.match(/[A-Z]+/)) strength += 25; 
            if (val.match(/[0-9]+/) || val.match(/[\W_]+/)) strength += 25; 

            strengthBar.style.width = strength + '%';

            if (val.length === 0) {
                strengthBar.style.width = '0%';
                strengthBar.className = 'progress-bar';
                strengthText.textContent = 'Şifre gücü...';
                strengthText.style.color = 'var(--text-muted)';
                submitBtn.disabled = false; 
            } else if (strength <= 25) {
                strengthBar.className = 'progress-bar bg-danger';
                strengthText.textContent = 'Zayıf (En az 8 karakter ve rakam/harf karması yapın)';
                strengthText.style.color = '#EF4444';
                submitBtn.disabled = true; 
            } else if (strength <= 75) {
                strengthBar.className = 'progress-bar bg-warning';
                strengthText.textContent = 'Orta (Daha güvenli bir şifre için özel karakter ekleyin)';
                strengthText.style.color = '#F59E0B';
                submitBtn.disabled = false; 
            } else {
                strengthBar.className = 'progress-bar bg-success';
                strengthText.textContent = 'Güçlü (Harika şifre!)';
                strengthText.style.color = '#10B981';
                submitBtn.disabled = false;
            }
        });
    }