// Modern JavaScript for Planora App
class PlanoraApp {
    constructor() {
        this.isScrolling = false;
        this.animatedElements = new Set();
        this.init();
    }

    // ========================================
    // INITIALIZATION
    // ========================================

    init() {
        this.setupEventListeners();
        this.setupAnimations();
        this.setupSmoothScrolling();
        this.setupFormValidation();
        this.setupMobileMenu();
        console.log('🚀 Planora App Initialized');
    }

    setupEventListeners() {
        // Header scroll effect with throttling
        window.addEventListener('scroll', this.throttle(() => {
            this.handleScroll();
        }, 16)); // 60fps

        // Mobile menu toggle
        const mobileToggle = document.getElementById('mobile-toggle');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        // Button click tracking with ripple effect
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.createRippleEffect(e, btn);
            });
        });

        // Window resize handler
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    // ========================================
    // SMOOTH SCROLLING
    // ========================================

    setupSmoothScrolling() {
        // Smooth scroll for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // ========================================
    // FORM VALIDATION
    // ========================================

    setupFormValidation() {
        // Real-time form validation
        const emailInputs = document.querySelectorAll('input[type="email"]');
        const passwordInputs = document.querySelectorAll('input[type="password"]');

        emailInputs.forEach(input => {
            input.addEventListener('blur', this.validateEmail);
            input.addEventListener('input', this.clearValidationErrors);
        });

        passwordInputs.forEach(input => {
            input.addEventListener('blur', this.validatePassword);
            input.addEventListener('input', this.clearValidationErrors);
        });

        // Form submission validation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    validateEmail(e) {
        const email = e.target.value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(email);
        
        if (email && !isValid) {
            e.target.style.borderColor = '#ef4444';
            PlanoraApp.showFieldError(e.target, 'Please enter a valid email address');
        } else {
            e.target.style.borderColor = 'var(--glass-border)';
            PlanoraApp.clearFieldError(e.target);
        }
    }

    validatePassword(e) {
        const password = e.target.value;
        const isValid = password.length >= 6;
        
        if (password && !isValid) {
            e.target.style.borderColor = '#ef4444';
            PlanoraApp.showFieldError(e.target, 'Password must be at least 6 characters');
        } else {
            e.target.style.borderColor = 'var(--glass-border)';
            PlanoraApp.clearFieldError(e.target);
        }
    }

    clearValidationErrors(e) {
        e.target.style.borderColor = 'var(--glass-border)';
        PlanoraApp.clearFieldError(e.target);
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = '#ef4444';
                PlanoraApp.showFieldError(field, 'This field is required');
                isValid = false;
            }
        });

        // Password confirmation check
        const password = form.querySelector('input[name="password"]');
        const confirmPassword = form.querySelector('input[name="confirm-password"]');
        
        if (password && confirmPassword && password.value !== confirmPassword.value) {
            confirmPassword.style.borderColor = '#ef4444';
            PlanoraApp.showFieldError(confirmPassword, 'Passwords do not match');
            isValid = false;
        }

        return isValid;
    }

    static showFieldError(field, message) {
        PlanoraApp.clearFieldError(field);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.cssText = 'color: #ef4444; font-size: 0.875rem; margin-top: 0.25rem;';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    static clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    // ========================================
    // ANIMATIONS & EFFECTS
    // ========================================

    setupAnimations() {
        this.setupIntersectionObserver();
        this.setupPricingCardAnimations();
        this.setupFormTransitions();
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.animatedElements.has(entry.target)) {
                    this.animateElement(entry.target);
                    this.animatedElements.add(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observe elements for animation
        document.querySelectorAll('.feature-card, .pricing-card, .glass-card, .dashboard-card').forEach(el => {
            observer.observe(el);
        });
    }

    animateElement(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        
        // Trigger animation
        requestAnimationFrame(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        });
    }

    setupPricingCardAnimations() {
        document.querySelectorAll('.pricing-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = card.classList.contains('featured') 
                    ? 'scale(1.05) translateY(-10px)' 
                    : 'translateY(-10px)';
                card.style.boxShadow = 'var(--glass-shadow)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = card.classList.contains('featured') 
                    ? 'scale(1.05)' 
                    : 'translateY(0)';
                card.style.boxShadow = '';
            });
        });
    }

    setupFormTransitions() {
        const authForms = document.querySelectorAll('.auth-form');
        authForms.forEach(form => {
            form.style.opacity = '0';
            form.style.transform = 'translateY(20px)';
            form.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            
            // Animate in
            setTimeout(() => {
                form.style.opacity = '1';
                form.style.transform = 'translateY(0)';
            }, 100);
        });
    }

    // ========================================
    // MOBILE MENU
    // ========================================

    setupMobileMenu() {
        this.mobileMenuOpen = false;
    }

    toggleMobileMenu() {
        const navLinks = document.getElementById('nav-links');
        const mobileToggle = document.getElementById('mobile-toggle');
        
        this.mobileMenuOpen = !this.mobileMenuOpen;
        
        if (this.mobileMenuOpen) {
            navLinks.classList.add('active');
            document.body.classList.add('menu-open');
            mobileToggle.classList.add('active');
        } else {
            navLinks.classList.remove('active');
            document.body.classList.remove('menu-open');
            mobileToggle.classList.remove('active');
        }
    }

    // ========================================
    // SCROLL EFFECTS
    // ========================================

    handleScroll() {
        const scrollY = window.scrollY;
        const header = document.getElementById('header');
        
        if (header) {
            if (scrollY > 100) {
                header.style.background = 'rgba(10, 11, 30, 0.95)';
                header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
            } else {
                header.style.background = 'rgba(10, 11, 30, 0.8)';
                header.style.boxShadow = 'none';
            }
        }

        // Update scroll progress indicator
        this.updateScrollProgress();
    }

    updateScrollProgress() {
        const scrollProgress = document.getElementById('scroll-progress');
        if (scrollProgress) {
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrolled = (window.scrollY / scrollHeight) * 100;
            scrollProgress.style.width = `${scrolled}%`;
        }
    }

    // ========================================
    // UTILITY FUNCTIONS
    // ========================================

    createRippleEffect(event, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        `;
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    handleResize() {
        // Handle responsive changes
        if (window.innerWidth > 768 && this.mobileMenuOpen) {
            this.toggleMobileMenu();
        }
    }

    // Performance utilities
    throttle(func, limit) {
        let inThrottle;
        return function () {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

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
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PlanoraApp();
});

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);