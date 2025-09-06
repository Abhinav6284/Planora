// ========================================
// PLANORA - ENHANCED DYNAMIC JAVASCRIPT
// Professional Interactive Functionality
// ========================================

class PlanoraApp {
    constructor() {
        this.isScrolling = false;
        this.animatedElements = new Set();
        this.statsData = [
            { label: 'Active Users', value: 12500, suffix: '+', icon: '👥' },
            { label: 'Tasks Completed', value: 89432, suffix: '', icon: '✅' },
            { label: 'Projects Managed', value: 3245, suffix: '+', icon: '📊' },
            { label: 'Teams Onboarded', value: 456, suffix: '+', icon: '🏢' }
        ];
        this.featuresData = [
            {
                title: 'AI-Powered Prioritization',
                description: 'Our intelligent engine analyzes your tasks and suggests the most optimal path to completion.',
                icon: '🤖',
                gradient: 'linear-gradient(135deg, #00d4ff, #7c3aed)'
            },
            {
                title: 'End-to-End Encryption',
                description: 'Your data is protected with military-grade encryption, ensuring complete privacy.',
                icon: '🔒',
                gradient: 'linear-gradient(135deg, #7c3aed, #f59e0b)'
            },
            {
                title: 'Seamless Integration',
                description: 'Connect with your favorite tools through our robust API for limitless customization.',
                icon: '🔗',
                gradient: 'linear-gradient(135deg, #f59e0b, #00d4ff)'
            }
        ];
        this.init();
    }

    // ========================================
    // INITIALIZATION
    // ========================================

    init() {
        this.setupEventListeners();
        this.generateDynamicContent();
        this.setupAnimations();
        this.setupAccessibility();
        this.setupPerformanceOptimizations();
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

        // Smooth scroll navigation
        this.setupSmoothScrolling();

        // Button click tracking
        this.setupButtonTracking();

        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeydown(e));

        // Window resize handler
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    // ========================================
    // DYNAMIC CONTENT GENERATION
    // ========================================

    generateDynamicContent() {
        this.generateStats();
        this.generateFeatures();
        this.generateProgressIndicators();
    }

    generateStats() {
        const statsContainer = document.querySelector('.hero-stats');
        if (!statsContainer) return;

        statsContainer.innerHTML = '';

        this.statsData.forEach((stat, index) => {
            const statElement = this.createElement('div', {
                className: 'stat fade-in',
                'data-delay': index * 0.1
            });

            const iconElement = this.createElement('div', {
                className: 'stat-icon'
            }, stat.icon);

            const numberElement = this.createElement('span', {
                className: 'stat-number',
                'data-target': stat.value,
                'data-suffix': stat.suffix
            }, '0');

            const labelElement = this.createElement('span', {
                className: 'stat-label'
            }, stat.label);

            // Add progress bar
            const progressElement = this.createElement('div', {
                className: 'stat-progress'
            });
            const progressBar = this.createElement('div', {
                className: 'stat-progress-bar',
                'data-width': Math.min((stat.value / 100000) * 100, 100)
            });
            progressElement.appendChild(progressBar);

            statElement.appendChild(iconElement);
            statElement.appendChild(numberElement);
            statElement.appendChild(labelElement);
            statElement.appendChild(progressElement);

            statsContainer.appendChild(statElement);
        });
    }

    generateFeatures() {
        const featuresGrid = document.querySelector('.features-grid');
        if (!featuresGrid) return;

        // Keep existing content and enhance it
        const existingCards = featuresGrid.querySelectorAll('.feature-card');
        existingCards.forEach((card, index) => {
            if (this.featuresData[index]) {
                this.enhanceFeatureCard(card, this.featuresData[index], index);
            }
        });
    }

    enhanceFeatureCard(card, data, index) {
        card.classList.add('fade-in');
        card.setAttribute('data-delay', index * 0.2);

        const icon = card.querySelector('.feature-icon');
        if (icon) {
            icon.style.background = data.gradient;
            icon.innerHTML = data.icon;
        }

        // Add hover effects
        card.addEventListener('mouseenter', () => {
            this.animateCardHover(card, true);
        });

        card.addEventListener('mouseleave', () => {
            this.animateCardHover(card, false);
        });
    }

    generateProgressIndicators() {
        // Create scroll progress indicator
        const progressBar = this.createElement('div', {
            className: 'scroll-progress',
            id: 'scroll-progress'
        });
        document.body.appendChild(progressBar);
    }

    // ========================================
    // ANIMATIONS & EFFECTS
    // ========================================

    setupAnimations() {
        this.setupIntersectionObserver();
        this.setupParallaxEffects();
        this.setupLoadingAnimations();
    }

    setupIntersectionObserver() {
        const observerOptions = {
            root: null,
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.animatedElements.has(entry.target)) {
                    this.animateElement(entry.target);
                    this.animatedElements.add(entry.target);
                }
            });
        }, observerOptions);

        // Observe all animatable elements
        const elements = document.querySelectorAll('.fade-in, .hero-stats, .glass-card, .feature-card');
        elements.forEach(el => observer.observe(el));
    }

    animateElement(element) {
        const delay = parseFloat(element.getAttribute('data-delay')) || 0;

        setTimeout(() => {
            element.classList.add('visible');

            // Special animations for specific elements
            if (element.classList.contains('hero-stats')) {
                this.animateCounters();
                this.animateProgressBars();
            }

            if (element.classList.contains('glass-card')) {
                this.animateGlassCard(element);
            }
        }, delay * 1000);
    }

    animateCounters() {
        const counters = document.querySelectorAll('.stat-number');

        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const suffix = counter.getAttribute('data-suffix') || '';
            const duration = 2000; // 2 seconds
            const frameDuration = 1000 / 60; // 60fps
            const totalFrames = Math.round(duration / frameDuration);
            let frame = 0;

            const timer = setInterval(() => {
                frame++;
                const progress = this.easeOutQuart(frame / totalFrames);
                const currentValue = Math.round(target * progress);

                counter.textContent = this.formatNumber(currentValue) + suffix;

                if (frame === totalFrames) {
                    clearInterval(timer);
                }
            }, frameDuration);
        });
    }

    animateProgressBars() {
        const progressBars = document.querySelectorAll('.stat-progress-bar');

        progressBars.forEach((bar, index) => {
            const targetWidth = parseFloat(bar.getAttribute('data-width'));

            setTimeout(() => {
                bar.style.width = targetWidth + '%';
                bar.style.transition = 'width 1.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            }, index * 200);
        });
    }

    animateGlassCard(card) {
        card.style.transform = 'translateY(0) scale(1)';
        card.style.opacity = '1';

        // Add shimmer effect
        const shimmer = this.createElement('div', {
            className: 'card-shimmer'
        });
        card.appendChild(shimmer);

        setTimeout(() => {
            shimmer.remove();
        }, 1000);
    }

    animateCardHover(card, isHover) {
        if (isHover) {
            card.style.transform = 'translateY(-12px) scale(1.02)';
            card.style.boxShadow = '0 20px 40px rgba(0, 212, 255, 0.3)';
        } else {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = '';
        }
    }

    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');

        window.addEventListener('scroll', this.throttle(() => {
            const scrolled = window.pageYOffset;

            parallaxElements.forEach(element => {
                const rate = parseFloat(element.getAttribute('data-parallax')) || 0.5;
                const yPos = -(scrolled * rate);
                element.style.transform = `translateY(${yPos}px)`;
            });
        }, 16));
    }

    setupLoadingAnimations() {
        // Stagger hero text animations
        const heroElements = document.querySelectorAll('.hero-subtitle, .hero-title, .hero-description, .hero-cta');

        heroElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';

            setTimeout(() => {
                element.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, (index + 1) * 200);
        });
    }

    // ========================================
    // NAVIGATION & INTERACTION
    // ========================================

    handleScroll() {
        const header = document.getElementById('header');
        const scrollProgress = document.getElementById('scroll-progress');

        // Header scroll effect
        if (header) {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }

        // Update scroll progress
        if (scrollProgress) {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            scrollProgress.style.width = scrolled + '%';
        }
    }

    toggleMobileMenu() {
        const toggle = document.getElementById('mobile-toggle');
        const menu = document.getElementById('nav-links');

        if (!toggle || !menu) return;

        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';

        toggle.setAttribute('aria-expanded', !isExpanded);
        menu.classList.toggle('active');

        // Add body class to prevent scrolling
        document.body.classList.toggle('menu-open');

        // Focus management
        if (!isExpanded) {
            menu.querySelector('a')?.focus();
        }
    }

    setupSmoothScrolling() {
        const navLinks = document.querySelectorAll('a[href^="#"]');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();

                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    const headerHeight = document.getElementById('header')?.offsetHeight || 0;
                    const targetPosition = targetElement.offsetTop - headerHeight;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });

                    // Close mobile menu if open
                    const menu = document.getElementById('nav-links');
                    if (menu?.classList.contains('active')) {
                        this.toggleMobileMenu();
                    }
                }
            });
        });
    }

    setupButtonTracking() {
        const buttons = document.querySelectorAll('.btn');

        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                // Add click ripple effect
                this.createRippleEffect(e, button);

                // Analytics tracking
                this.trackEvent('button_click', {
                    button_text: button.textContent.trim(),
                    button_class: button.className,
                    page_section: this.getPageSection(button)
                });
            });
        });
    }

    // ========================================
    // ACCESSIBILITY
    // ========================================

    setupAccessibility() {
        // Keyboard navigation
        this.setupKeyboardNavigation();

        // Screen reader announcements
        this.setupScreenReaderSupport();

        // Focus management
        this.setupFocusManagement();
    }

    setupKeyboardNavigation() {
        // Tab through interactive elements
        const focusableElements = document.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        focusableElements.forEach(element => {
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    if (element.tagName === 'BUTTON' || element.hasAttribute('role')) {
                        e.preventDefault();
                        element.click();
                    }
                }
            });
        });
    }

    setupScreenReaderSupport() {
        // Add live region for dynamic content updates
        const liveRegion = this.createElement('div', {
            'aria-live': 'polite',
            'aria-atomic': 'true',
            className: 'sr-only'
        });
        document.body.appendChild(liveRegion);

        this.liveRegion = liveRegion;
    }

    setupFocusManagement() {
        // Return focus to trigger element when modals close
        document.addEventListener('focusin', (e) => {
            this.lastFocusedElement = e.target;
        });
    }

    handleKeydown(e) {
        // Escape key handling
        if (e.key === 'Escape') {
            const menu = document.getElementById('nav-links');
            if (menu?.classList.contains('active')) {
                this.toggleMobileMenu();
            }
        }
    }

    // ========================================
    // UTILITY FUNCTIONS
    // ========================================

    createElement(tag, attributes = {}, textContent = null) {
        const element = document.createElement(tag);

        Object.entries(attributes).forEach(([key, value]) => {
            if (key.startsWith('data-') || key.startsWith('aria-')) {
                element.setAttribute(key, value);
            } else if (key === 'className') {
                element.className = value;
            } else {
                element[key] = value;
            }
        });

        if (textContent) {
            element.textContent = textContent;
        }

        return element;
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    createRippleEffect(event, element) {
        const ripple = this.createElement('span', {
            className: 'ripple'
        });

        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';

        element.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    trackEvent(eventName, properties = {}) {
        // Analytics integration point
        console.log(`📊 Event: ${eventName}`, properties);

        // Integrate with your analytics service here
        // Example: gtag('event', eventName, properties);
    }

    getPageSection(element) {
        const sections = ['hero', 'features', 'pricing', 'cta'];
        let currentSection = 'unknown';

        sections.forEach(section => {
            const sectionElement = document.querySelector(`.${section}`);
            if (sectionElement?.contains(element)) {
                currentSection = section;
            }
        });

        return currentSection;
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

    // Easing functions
    easeOutQuart(t) {
        return 1 - (--t) * t * t * t;
    }

    handleResize() {
        // Recalculate animations and layouts on resize
        this.animatedElements.clear();
        this.setupIntersectionObserver();
    }

    setupPerformanceOptimizations() {
        // Preload critical images
        this.preloadImages();

        // Setup service worker if available
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').catch(() => {
                console.log('Service Worker registration failed');
            });
        }
    }

    preloadImages() {
        const images = [
            '/static/images/hero-bg.jpg',
            '/static/images/feature-1.jpg',
            '/static/images/feature-2.jpg'
        ];

        images.forEach(src => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = src;
            document.head.appendChild(link);
        });
    }
}

// ========================================
// INITIALIZATION
// ========================================

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.planoraApp = new PlanoraApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log('🔄 Page became visible - refreshing animations');
    }
});
