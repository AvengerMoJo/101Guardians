// tabs.js - Handles tab switching functionality

/**
 * Set up tab switching functionality for dashboard
 */
export function setupTabSwitching() {
    const tabs = document.querySelectorAll('#dashboard-tabs li');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabs.length > 0 && tabContents.length > 0) {
        console.log('Setting up dashboard tabs');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                tabs.forEach(t => t.classList.remove('is-active'));
                
                // Add active class to clicked tab
                tab.classList.add('is-active');
                
                // Hide all tab contents
                tabContents.forEach(content => content.classList.add('is-hidden'));
                
                // Show the target tab content
                const targetId = tab.dataset.target;
                const targetContent = document.getElementById(targetId);
                if (targetContent) {
                    targetContent.classList.remove('is-hidden');
                }
            });
        });
    }
}