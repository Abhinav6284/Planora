// Enhanced JavaScript for StudyPath Pro

class StudyPathPro {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.startAnimations();
    }

    init() {
        this.setupTheme();
        this.setupScrollEffects();
        this.setupProgressAnimations();
        this.setupModalSystem();
    }

    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        themeToggle?.addEventListener('click', () => this.toggleTheme());

        // Smooth scrolling for navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });

        // Demo modal
        document.querySelectorAll('[data-modal]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                this.openModal(trigger.dataset.modal);
            });
        });

        // Close modals
        document.querySelectorAll('.modal-close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => this.closeModal());
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModal();
        });

        // Intersection Observer for animations
        this.setupIntersectionObserver();
    }

    setupTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark' ||
            (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.body.classList.add('dark-mode');
        }
    }

    toggleTheme() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        // Add ripple effect to theme toggle
        this.createRipple(document.getElementById('themeToggle'));
    }

    setupScrollEffects() {
        const header = document.getElementById('header');
        let lastScroll = 0;

        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;

            // Header background on scroll
            if (currentScroll > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }

            // Parallax effect for floating shapes
            const shapes = document.querySelectorAll('.floating-shape');
            shapes.forEach((shape, index) => {
                const speed = 0.5 + (index * 0.2);
                const yPos = -(currentScroll * speed);
                shape.style.transform = `translateY(${yPos}px)`;
            });

            lastScroll = currentScroll;
        });
    }

    setupProgressAnimations() {
        // Animated counters
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateProgress(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        document.querySelectorAll('.progress-fill').forEach(el => {
            observer.observe(el);
        });

        // Statistics counter animation
        document.querySelectorAll('[data-count]').forEach(el => {
            observer.observe(el);
        });
    }

    animateProgress(element) {
        if (element.classList.contains('progress-fill')) {
            // Animate progress ring
            element.style.animation = 'progressAnimation 2s ease forwards';
        } else if (element.hasAttribute('data-count')) {
            // Animate counter
            const target = parseInt(element.dataset.count);
            this.animateCounter(element, target);
        }
    }

    animateCounter(element, target) {
        let current = 0;
        const increment = target / 100;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current).toLocaleString();
        }, 20);
    }

    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');

                    // Stagger animation for feature cards
                    if (entry.target.classList.contains('feature-card')) {
                        const cards = entry.target.parentElement.children;
                        Array.from(cards).forEach((card, index) => {
                            setTimeout(() => {
                                card.classList.add('fade-in-up');
                            }, index * 100);
                        });
                    }
                }
            });
        }, observerOptions);

        // Observe elements for scroll animations
        document.querySelectorAll('.feature-card, .step, .pricing-card').forEach(el => {
            observer.observe(el);
        });
    }

    setupModalSystem() {
        this.modals = new Map();
        document.querySelectorAll('.modal').forEach(modal => {
            this.modals.set(modal.id, modal);
        });
    }

    openModal(modalId) {
        const modal = this.modals.get(modalId + 'Modal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';

            // Focus trap
            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            focusableElements[0]?.focus();
        }
    }

    closeModal() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    createRipple(element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = '50%';
        ripple.style.top = '50%';
        ripple.style.transform = 'translate(-50%, -50%)';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.6)';
        ripple.style.pointerEvents = 'none';
        ripple.style.animation = 'ripple 0.6s linear';

        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    startAnimations() {
        // Add CSS for ripple animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: translate(-50%, -50%) scale(2);
                    opacity: 0;
                }
            }
            
            .animate-in {
                animation: fadeInUp 0.8s ease forwards;
            }
            
            .fade-in-up {
                animation: fadeInUp 0.6s ease forwards;
            }
        `;
        document.head.appendChild(style);

        // Initialize AOS-like animations
        this.initScrollAnimations();
    }

    initScrollAnimations() {
        const elements = document.querySelectorAll('[data-animate]');
        elements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
        });
    }

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Performance optimizations
    requestTick(callback) {
        if (!this.ticking) {
            requestAnimationFrame(() => {
                callback();
                this.ticking = false;
            });
            this.ticking = true;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StudyPathPro();
});

// Service Worker for PWA (if needed)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Add loading animation utility
const addLoading = (element) => {
    element.classList.add('loading');
    return () => element.classList.remove('loading');
};

// Form validation utilities
const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

const showAlert = (message, type = 'info') => {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        color: white;
        background: ${type === 'error' ? '#ef4444' : '#10b981'};
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(alert);
    setTimeout(() => {
        alert.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
};

// Add CSS for alert animations
const alertStyles = document.createElement('style');
alertStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(alertStyles);
