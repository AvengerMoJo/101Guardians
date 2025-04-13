// main.js - Enhanced with tab functionality and prayer interactions

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded - initializing scripts');
    // Mobile menu toggle for navbar
    setupNavbarToggle();
    // Dashboard data entry form functionality
    setupDashboardForm();
    // Tab switching functionality
    setupTabSwitching();
    // Prayer interaction buttons
    setupPrayerInteractions();
});

/**
 * Set up the navbar toggle functionality
 */
function setupNavbarToggle() {
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

/**
 * Set up tab switching functionality
 */
function setupTabSwitching() {
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

// Flag to prevent duplicate submissions
let isSubmitting = false;

/**
 * Set up event handlers for the dashboard prayer form
 */
function setupDashboardForm() {
    // Elements for the dashboard prayer form
    const addDataBtn = document.getElementById('addDataBtn');
    const dataForm = document.getElementById('dataForm');
    const saveDataBtn = document.getElementById('saveDataBtn');
    const cancelDataBtn = document.getElementById('cancelDataBtn');
    const dataTitle = document.getElementById('dataTitle');
    const dataContent = document.getElementById('dataContent');
    
    // Only setup event listeners if these elements exist (i.e., on dashboard page)
    if (addDataBtn && dataForm) {
        console.log('Dashboard form elements found - setting up event handlers');
        
        // Toggle form visibility
        addDataBtn.addEventListener('click', () => {
            console.log('Add data button clicked - showing form');
            dataForm.classList.remove('is-hidden');
            // Focus on the title input for better UX
            dataTitle.focus();
        });
        
        cancelDataBtn.addEventListener('click', () => {
            console.log('Cancel button clicked - hiding form');
            dataForm.classList.add('is-hidden');
            clearFormFields();
        });
        
        // Save data with improved error handling and protection against double submissions
        saveDataBtn.addEventListener('click', async (e) => {
            e.preventDefault(); // Prevent any default form submission
            if (!isSubmitting) {
                await submitPrayerData();
            } else {
                console.log('Submission already in progress, ignoring duplicate click');
            }
        });
        
        // Also handle form submission on Enter key in the textarea
        dataContent.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault(); // Prevent default behavior
                if (!isSubmitting) {
                    await submitPrayerData();
                } else {
                    console.log('Submission already in progress, ignoring duplicate Enter press');
                }
            }
        });
    }
}

/**
 * Set up event handlers for prayer interaction buttons (pray, praise)
 */
function setupPrayerInteractions() {
    const prayButtons = document.querySelectorAll('.prayer-interact-button');
    
    if (prayButtons.length > 0) {
        console.log('Setting up prayer interaction buttons');
        
        prayButtons.forEach(button => {
            button.addEventListener('click', async () => {
                const prayerId = button.dataset.prayerId;
                const interactionType = button.dataset.interactionType;
                
                if (!prayerId || !interactionType) {
                    console.error('Missing prayer ID or interaction type');
                    return;
                }
                
                try {
                    button.classList.add('is-loading');
                    
                    const response = await fetch(`/api/prayers/${prayerId}/interact`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ type: interactionType }),
                        credentials: 'same-origin'
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        
                        // Update the count display
                        const countElement = button.querySelector('.interaction-count');
                        if (countElement) {
                            countElement.textContent = result.count;
                        }
                        
                        // Add a success class briefly
                        button.classList.add('is-success');
                        setTimeout(() => {
                            button.classList.remove('is-success');
                        }, 1500);
                    } else {
                        console.error('Failed to record interaction');
                    }
                } catch (error) {
                    console.error('Error:', error);
                } finally {
                    button.classList.remove('is-loading');
                }
            });
        });
    }
}

/**
 * Clear form fields and reset the form
 */
function clearFormFields() {
    const dataTitle = document.getElementById('dataTitle');
    const dataContent = document.getElementById('dataContent');
    const privacyRadios = document.querySelectorAll('input[name="prayerPrivacy"]');
    
    if (dataTitle && dataContent) {
        dataTitle.value = '';
        dataContent.value = '';
        
        // Reset radio buttons to private
        if (privacyRadios.length > 0) {
            privacyRadios.forEach(radio => {
                if (radio.value === 'private') {
                    radio.checked = true;
                } else {
                    radio.checked = false;
                }
            });
        }
    }
}

/**
 * Submit prayer data to the server
 */
async function submitPrayerData() {
    if (isSubmitting) {
        console.log('Already submitting, ignoring duplicate call');
        return;
    }
    
    isSubmitting = true;
    const saveDataBtn = document.getElementById('saveDataBtn');
    if (saveDataBtn) {
        saveDataBtn.classList.add('is-loading');
        saveDataBtn.disabled = true;
    }
    
    const dataTitle = document.getElementById('dataTitle');
    const dataContent = document.getElementById('dataContent');
    const dataForm = document.getElementById('dataForm');
    const privacyRadios = document.querySelectorAll('input[name="prayerPrivacy"]');
    
    const title = dataTitle.value.trim();
    const content = dataContent.value.trim();
    
    // Determine if prayer is public
    let isPublic = false;
    privacyRadios.forEach(radio => {
        if (radio.checked && radio.value === 'public') {
            isPublic = true;
        }
    });
    
    if (!title || !content) {
        alert('Please fill in both title and content fields');
        isSubmitting = false;
        if (saveDataBtn) {
            saveDataBtn.classList.remove('is-loading');
            saveDataBtn.disabled = false;
        }
        return;
    }
    
    try {
        console.log('Submitting prayer data:', { title, content, is_public: isPublic });
        
        const response = await fetch('/api/prayers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                title, 
                content,
                is_public: isPublic 
            }),
            credentials: 'same-origin' // Ensure cookies are sent
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            console.log('Prayer saved successfully');
            // Reload page to show the new data
            window.location.reload();
        } else {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            alert(errorData.error || 'Failed to save prayer data');
            isSubmitting = false;
            if (saveDataBtn) {
                saveDataBtn.classList.remove('is-loading');
                saveDataBtn.disabled = false;
            }
        }
    } catch (error) {
        console.error('Fetch error:', error);
        alert('An error occurred while saving prayer data. Please try again later.');
        isSubmitting = false;
        if (saveDataBtn) {
            saveDataBtn.classList.remove('is-loading');
            saveDataBtn.disabled = false;
        }
    }
}

/**
 * Function to mark a prayer as answered
 */
async function markPrayerAsAnswered(prayerId) {
    const answerText = prompt('How was this prayer answered?');
    if (!answerText || answerText.trim() === '') {
        return; // User cancelled or provided empty answer
    }
    
    try {
        const response = await fetch(`/api/prayers/${prayerId}/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answer: answerText }),
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            alert('Prayer marked as answered!');
            window.location.reload();
        } else {
            const errorData = await response.json();
            alert(errorData.error || 'Failed to mark prayer as answered');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again later.');
    }
}