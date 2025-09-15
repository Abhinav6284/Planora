document.addEventListener('DOMContentLoaded', function () {
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    // Optional: stop observing after animation
                    // observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.1, // Trigger when 10% of the element is visible
        }
    );

    // Select all elements with the 'hidden' class to observe
    const hiddenElements = document.querySelectorAll('.hidden');
    hiddenElements.forEach(el => observer.observe(el));

    // Mobile nav toggle
    const navToggle = document.querySelector('.nav-toggle');
    const mainNav = document.getElementById('primary-navigation');

    if (navToggle && mainNav) {
        const setExpanded = expanded => {
            navToggle.setAttribute('aria-expanded', String(expanded));
            mainNav.setAttribute('aria-hidden', String(!expanded));
        };

        setExpanded(false);

        navToggle.addEventListener('click', () => {
            const expanded = navToggle.getAttribute('aria-expanded') === 'true';
            setExpanded(!expanded);
        });

        // Close menu on link click (mobile)
        mainNav.querySelectorAll('a').forEach(a =>
            a.addEventListener('click', () => setExpanded(false))
        );
    }
});