// crud.js - CRUD operations for prayers

import { apiPost, apiPut, apiDelete } from '../utils/api.js';
import { t } from '../i18n.js';

/**
 * Create a new prayer
 * @param {string} title - The prayer title
 * @param {string} content - The prayer content
 * @param {boolean} isPublic - Whether the prayer is public
 * @returns {Promise} - Promise that resolves when the prayer is created
 */
export async function createPrayer(title, content, isPublic) {
    console.log('Creating prayer:', { title, content, is_public: isPublic });
    
    try {
        return await apiPost('/api/prayers', {
            title,
            content,
            is_public: isPublic
        });
    } catch (error) {
        console.error('Error creating prayer:', error);
        throw new Error(error.message || t('Failed to create prayer'));
    }
}

/**
 * Update an existing prayer
 * @param {number} prayerId - The ID of the prayer to update
 * @param {string} title - The updated prayer title
 * @param {string} content - The updated prayer content
 * @param {boolean} isPublic - Whether the prayer is public
 * @returns {Promise} - Promise that resolves when the prayer is updated
 */
export async function updatePrayer(prayerId, title, content, isPublic) {
    console.log('Updating prayer:', { id: prayerId, title, content, is_public: isPublic });
    
    try {
        return await apiPut(`/api/prayers/${prayerId}`, {
            title,
            content,
            is_public: isPublic
        });
    } catch (error) {
        console.error('Error updating prayer:', error);
        throw new Error(error.message || t('Failed to update prayer'));
    }
}

/**
 * Delete a prayer
 * @param {number} prayerId - The ID of the prayer to delete
 * @returns {Promise} - Promise that resolves when the prayer is deleted
 */
export async function deletePrayer(prayerId) {
    // Confirm before deleting
    if (!confirm(t('Are you sure you want to delete this prayer? This action cannot be undone.'))) {
        return;
    }
    
    try {
        // Show processing status
        const deleteBtn = document.querySelector(`button[onclick="deletePrayer(${prayerId})"]`);
        if (deleteBtn) {
            deleteBtn.classList.add('is-loading');
            deleteBtn.disabled = true;
        }
        
        const result = await apiDelete(`/api/prayers/${prayerId}`);
        
        // Success message
        alert(t('Prayer deleted successfully'));
        
        // Reload page to update the UI
        window.location.reload();
        
        return result;
    } catch (error) {
        console.error('Error deleting prayer:', error);
        
        const deleteBtn = document.querySelector(`button[onclick="deletePrayer(${prayerId})"]`);
        if (deleteBtn) {
            deleteBtn.classList.remove('is-loading');
            deleteBtn.disabled = false;
        }
        
        alert(error.message || t('Failed to delete prayer'));
        throw error;
    }
}

/**
 * Mark a prayer as answered
 * @param {number} prayerId - The ID of the prayer to mark as answered
 * @returns {Promise} - Promise that resolves when the prayer is marked as answered
 */
export async function markPrayerAsAnswered(prayerId) {
    const answerText = prompt(t('How was this prayer answered?'));
    if (!answerText || answerText.trim() === '') {
        return; // User cancelled or provided empty answer
    }
    
    try {
        // Show processing indication
        const buttonEl = document.querySelector(`button[onclick="markPrayerAsAnswered(${prayerId})"]`);
        if (buttonEl) {
            buttonEl.classList.add('is-loading');
            buttonEl.disabled = true;
        }
        
        const result = await apiPost(`/api/prayers/${prayerId}/answer`, {
            answer: answerText
        });
        
        alert(t('Prayer marked as answered!'));
        
        // Store the current target tab before reload
        sessionStorage.setItem('activeTab', 'answered-prayers-tab');
        
        // Then reload the page
        window.location.reload();
        
        return result;
    } catch (error) {
        console.error('Error marking prayer as answered:', error);
        
        // Reset button state
        const buttonEl = document.querySelector(`button[onclick="markPrayerAsAnswered(${prayerId})"]`);
        if (buttonEl) {
            buttonEl.classList.remove('is-loading');
            buttonEl.disabled = false;
        }
        
        alert(error.message || t('Failed to mark prayer as answered'));
        throw error;
    }
}

// Make functions globally available for inline HTML event handlers
window.deletePrayer = deletePrayer;
window.markPrayerAsAnswered = markPrayerAsAnswered;