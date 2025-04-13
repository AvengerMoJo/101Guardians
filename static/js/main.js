// main.js - Enhanced with debugging and improved functionality

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded - initializing scripts');
    // Mobile menu toggle for navbar
    setupNavbarToggle();
    // Dashboard data entry form functionality
    setupDashboardForm();
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
 * Clear form fields and reset the form
 */
function clearFormFields() {
    const dataTitle = document.getElementById('dataTitle');
    const dataContent = document.getElementById('dataContent');
    
    if (dataTitle && dataContent) {
        dataTitle.value = '';
        dataContent.value = '';
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
    
    const title = dataTitle.value.trim();
    const content = dataContent.value.trim();
    
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
        console.log('Submitting prayer data:', { title, content });
        
        const response = await fetch('/api/data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
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