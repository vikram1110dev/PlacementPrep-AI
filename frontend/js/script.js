document.addEventListener("DOMContentLoaded", function () {
    // 1. Sticky Navbar & Scroll Shadow
    const navbar = document.getElementById("navbar");
    
    window.addEventListener("scroll", function () {
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });

    // 2. Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                const navbarToggler = document.querySelector('.navbar-toggler');
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            }
        });
    });

    // 3. Scroll Reveal Animations (Intersection Observer)
    const elementsToAnimate = document.querySelectorAll('.feature-card, .company-card, .testimonial-card, .pricing-card, .timeline-step, .stats-section h2');
    
    // Add fade-up class to all elements initially
    elementsToAnimate.forEach(el => {
        el.classList.add('fade-up');
    });

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Add a slight delay based on index for staggered effect
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, (index % 4) * 100); // Max delay of 300ms for sibling elements
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all targeted elements
    elementsToAnimate.forEach(el => {
        observer.observe(el);
    });
});
