// navbar.js - Handles navbar toggle functionality

/**
 * Set up the navbar toggle functionality for mobile devices
 */
export function setupNavbarToggle() {
    const navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
    
    if (navbarBurgers.length > 0) {
        console.log('Setting up navbar burger toggles');
        
        navbarBurgers.forEach(el => {
            el.addEventListener('click', () => {
                const target = document.getElementById(el.dataset.target);
                el.classList.toggle('is-active');
                target.classList.toggle('is-active');
            });
        });
    }
}