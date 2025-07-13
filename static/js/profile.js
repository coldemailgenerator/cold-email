
document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeSwitch = document.getElementById('darkModeSwitch');
    const body = document.body;
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.setAttribute('data-theme', savedTheme);
        darkModeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
        darkModeSwitch.checked = savedTheme === 'dark';
    }
    
    // Toggle dark mode from navbar
    darkModeToggle.addEventListener('click', function() {
        toggleDarkMode();
    });
    
    // Toggle dark mode from settings
    darkModeSwitch.addEventListener('change', function() {
        toggleDarkMode();
    });
    
    function toggleDarkMode() {
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        darkModeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        darkModeSwitch.checked = newTheme === 'dark';
    }
    
    // Animate stat numbers
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const finalValue = stat.textContent;
        if (!isNaN(finalValue)) {
            animateNumber(stat, 0, parseInt(finalValue), 1500);
        }
    });
    
    function animateNumber(element, start, end, duration) {
        const startTime = performance.now();
        
        function updateNumber(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(progress * (end - start) + start);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        }
        
        requestAnimationFrame(updateNumber);
    }
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.profile-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add click effects to security buttons
    const securityBtns = document.querySelectorAll('.security-btn');
    securityBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const btnText = this.querySelector('.btn-text').textContent;
            alert(`${btnText} functionality coming soon!`);
        });
    });
    
    // Add click effect to upgrade button
    const upgradeBtn = document.querySelector('.upgrade-btn');
    if (upgradeBtn) {
        upgradeBtn.addEventListener('click', function() {
            alert('Upgrade functionality coming soon!');
        });
    }
    
    // Add animation to profile elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.profile-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
});
