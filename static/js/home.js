
document.addEventListener('DOMContentLoaded', function() {
    // Animate stats on scroll
    const statNumbers = document.querySelectorAll('.stat-content h3');
    let statsAnimated = false;

    function animateStats() {
        if (statsAnimated) return;
        
        statNumbers.forEach((stat, index) => {
            const targetText = stat.textContent;
            const targetNumber = parseInt(targetText.replace(/[^\d]/g, ''));
            
            if (!isNaN(targetNumber) && targetNumber > 0) {
                let current = 0;
                const increment = targetNumber / 30;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= targetNumber) {
                        current = targetNumber;
                        clearInterval(timer);
                    }
                    stat.textContent = targetText.replace(/\d+/, Math.floor(current));
                }, 50);
            }
        });
        
        statsAnimated = true;
    }

    // Intersection Observer for stats animation
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateStats();
                }
            });
        }, { threshold: 0.5 });

        observer.observe(statsSection);
    }

    // Add loading state to buttons
    const actionButtons = document.querySelectorAll('.action-btn, .btn-hero, .empty-cta');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add subtle loading animation
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

    // Floating card animation enhancement
    const floatingCard = document.querySelector('.floating-card');
    if (floatingCard) {
        floatingCard.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-15px) scale(1.05)';
        });
        
        floatingCard.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    }

    // Tips section interactivity
    const tips = document.querySelectorAll('.tip');
    tips.forEach(tip => {
        tip.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(16, 52, 166, 0.05)';
            this.style.borderRadius = '8px';
            this.style.transform = 'translateX(10px)';
        });
        
        tip.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
            this.style.borderRadius = '';
            this.style.transform = '';
        });
    });

    // Welcome message time-based greeting
    const welcomeTitle = document.querySelector('.hero-text h1');
    if (welcomeTitle) {
        const hour = new Date().getHours();
        let greeting = 'Welcome back';
        
        if (hour < 12) {
            greeting = 'Good morning';
        } else if (hour < 17) {
            greeting = 'Good afternoon';
        } else {
            greeting = 'Good evening';
        }
        
        const userName = welcomeTitle.textContent.split(',')[1];
        welcomeTitle.textContent = `${greeting},${userName}`;
    }

    // Progressive loading animation for cards
    const cards = document.querySelectorAll('.stat-card, .action-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
