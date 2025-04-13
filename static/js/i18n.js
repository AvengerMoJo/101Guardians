// i18n.js - Handles client-side translation functionality

/**
 * Helper function to update the page language
 * @param {string} langCode - The language code to switch to
 */
export function changeLanguage(langCode) {
    // Create a form to submit the language change
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = `/language/${langCode}`;
    
    // Append the form to the document and submit it
    document.body.appendChild(form);
    form.submit();
}

/**
 * Set up language switcher functionality
 */
export function setupLanguageSwitcher() {
    const langLinks = document.querySelectorAll('.navbar-dropdown a.navbar-item');
    
    if (langLinks.length > 0) {
        console.log('Setting up language switcher');
        
        langLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                const langCode = href.split('/language/')[1];
                
                // Show loading indicator
                document.body.classList.add('is-loading');
                
                // Change the language
                changeLanguage(langCode);
            });
        });
    }
}

/**
 * Handle translation of dynamic content (added after page load)
 * This is a placeholder for future functionality if needed
 * @param {string} key - The translation key
 * @param {Object} params - Parameters for the translation (for string substitution)
 * @returns {string} - The translated string
 */
export function translate(key, params = {}) {
    // In a more advanced implementation, this function would look up translations
    // from a loaded dictionary. For now, we'll just return the key since most
    // translations are handled server-side by Flask-Babel.
    return key;
}

// Export a shorthand function name for translations
export const t = translate;