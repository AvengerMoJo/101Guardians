// form.js - Handles prayer form functionality

import { createPrayer, updatePrayer } from './crud.js';

// Flag to prevent duplicate submissions
let isSubmitting = false;

/**
 * Set up event handlers for the dashboard prayer form
 */
export function setupDashboardForm() {
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
            // Reset form to create mode
            if (saveDataBtn) {
                saveDataBtn.textContent = 'Save Prayer';
                saveDataBtn.dataset.mode = 'create';
                delete saveDataBtn.dataset.prayerId;
            }
            // Clear form fields
            clearFormFields();
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
export function clearFormFields() {
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
 * Show the edit prayer form and populate it with the prayer data
 * @param {number} prayerId - The ID of the prayer to edit
 * @param {string} title - The prayer title
 * @param {string} content - The prayer content
 * @param {boolean} isPublic - Whether the prayer is public
 */
export function editPrayer(prayerId, title, content, isPublic) {
    // Get form elements
    const dataForm = document.getElementById('dataForm');
    const dataTitle = document.getElementById('dataTitle');
    const dataContent = document.getElementById('dataContent');
    const privacyRadios = document.querySelectorAll('input[name="prayerPrivacy"]');
    
    // Show the form
    dataForm.classList.remove('is-hidden');
    
    // Set the form data
    dataTitle.value = title;
    dataContent.value = content;
    
    // Set the privacy radio button
    privacyRadios.forEach(radio => {
        if ((radio.value === 'public' && isPublic) || 
            (radio.value === 'private' && !isPublic)) {
            radio.checked = true;
        } else {
            radio.checked = false;
        }
    });
    
    // Change the form to edit mode
    const saveDataBtn = document.getElementById('saveDataBtn');
    if (saveDataBtn) {
        saveDataBtn.textContent = 'Update Prayer';
        saveDataBtn.dataset.mode = 'edit';
        saveDataBtn.dataset.prayerId = prayerId;
    }
    
    // Scroll to the form
    dataForm.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Submit prayer data (create new or update existing)
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
    
    try {
        // Get form data
        const dataTitle = document.getElementById('dataTitle');
        const dataContent = document.getElementById('dataContent');
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
        
        // Validate data
        if (!title || !content) {
            alert('Please fill in both title and content fields');
            return;
        }
        
        // Check if this is an edit or a new prayer
        const mode = saveDataBtn.dataset.mode || 'create';
        const prayerId = saveDataBtn.dataset.prayerId;
        
        if (mode === 'edit' && prayerId) {
            await updatePrayer(prayerId, title, content, isPublic);
        } else {
            await createPrayer(title, content, isPublic);
        }
        
        // Reload page to show changes
        window.location.reload();
    } catch (error) {
        console.error('Error submitting prayer:', error);
        alert(error.message || 'An error occurred while processing your prayer');
    } finally {
        isSubmitting = false;
        if (saveDataBtn) {
            saveDataBtn.classList.remove('is-loading');
            saveDataBtn.disabled = false;
        }
    }
}

// Make functions globally available for inline HTML event handlers
window.editPrayer = editPrayer;