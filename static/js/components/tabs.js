// tabs.js - Handles tab switching functionality with theme transitions

/**
 * Set up tab switching functionality for dashboard
 */
export function setupTabSwitching() {
    const tabs = document.querySelectorAll('#dashboard-tabs li');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabs.length > 0 && tabContents.length > 0) {
        console.log('Setting up dashboard tabs with theme transitions');
        
        // Check if we need to activate a specific tab (e.g., after marking a prayer as answered)
        const activeTabId = sessionStorage.getItem('activeTab');
        if (activeTabId) {
            // Find the tab with this target
            const targetTab = Array.from(tabs).find(tab => tab.dataset.target === activeTabId);
            if (targetTab) {
                // Simulate a click on this tab
                setTimeout(() => {
                    targetTab.click();
                    // Clear the stored tab ID so it doesn't persist across page views
                    sessionStorage.removeItem('activeTab');
                }, 100);
            }
        }
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                tabs.forEach(t => t.classList.remove('is-active'));
                
                // Add active class to clicked tab
                tab.classList.add('is-active');
                
                // Get the target tab content
                const targetId = tab.dataset.target;
                const targetContent = document.getElementById(targetId);
                
                // Apply fade-out effect to all tab contents before hiding them
                tabContents.forEach(content => {
                    if (!content.classList.contains('is-hidden')) {
                        content.style.opacity = '0';
                        setTimeout(() => {
                            content.classList.add('is-hidden');
                            content.style.opacity = '';
                        }, 200);
                    }
                });
                
                // Show the target tab content with fade-in effect
                if (targetContent) {
                    setTimeout(() => {
                        targetContent.classList.remove('is-hidden');
                        targetContent.style.opacity = '0';
                        
                        // Trigger reflow to ensure the opacity transition works
                        void targetContent.offsetWidth;
                        
                        // Apply the fade-in
                        targetContent.style.opacity = '1';
                    }, 210);
                }
            });
        });
    }
}