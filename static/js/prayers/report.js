// report.js - Handles prayer reporting functionality

import { apiPost } from '../utils/api.js';
import { t } from '../i18n.js';

// Current prayer being reported
let reportedPrayerId = null;

/**
 * Set up report prayer functionality
 */
export function setupReportButtons() {
    // Add event listener for report buttons
    document.querySelectorAll('.report-prayer-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            const prayerId = button.dataset.prayerId;
            openReportModal(prayerId);
        });
    });
    
    // Set up modal events
    const reportModal = document.getElementById('reportPrayerModal');
    if (reportModal) {
        // Close button
        reportModal.querySelector('.delete').addEventListener('click', () => {
            closeReportModal();
        });
        
        // Cancel button
        reportModal.querySelector('.cancel-report-btn').addEventListener('click', () => {
            closeReportModal();
        });
        
        // Submit button
        reportModal.querySelector('.submit-report-btn').addEventListener('click', () => {
            submitReport();
        });
    }
}

/**
 * Open the report modal for a prayer
 * @param {number} prayerId - The ID of the prayer to report
 */
function openReportModal(prayerId) {
    reportedPrayerId = prayerId;
    
    // Reset the form
    const reasonSelect = document.getElementById('reportReasonSelect');
    const reasonText = document.getElementById('reportReasonText');
    
    if (reasonSelect) reasonSelect.value = '';
    if (reasonText) reasonText.value = '';
    
    // Show the modal
    const modal = document.getElementById('reportPrayerModal');
    if (modal) {
        modal.classList.add('is-active');
    }
}

/**
 * Close the report modal
 */
function closeReportModal() {
    const modal = document.getElementById('reportPrayerModal');
    if (modal) {
        modal.classList.remove('is-active');
    }
    
    reportedPrayerId = null;
}

/**
 * Submit a prayer report
 */
async function submitReport() {
    if (!reportedPrayerId) return;
    
    const reasonSelect = document.getElementById('reportReasonSelect');
    const reasonText = document.getElementById('reportReasonText');
    
    let reason = '';
    
    // Get reason from select or text input
    if (reasonSelect && reasonSelect.value) {
        reason = reasonSelect.value;
    } else if (reasonText && reasonText.value.trim()) {
        reason = reasonText.value.trim();
    } else {
        alert(t('Please provide a reason for the report'));
        return;
    }
    
    try {
        // Show loading state
        const submitBtn = document.querySelector('.submit-report-btn');
        submitBtn.classList.add('is-loading');
        
        // Submit the report
        await apiPost('/api/reports', {
            prayer_id: reportedPrayerId,
            reason: reason
        });
        
        // Close the modal
        closeReportModal();
        
        // Show success message
        alert(t('Thank you for your report. Our moderators will review it shortly.'));
    } catch (error) {
        console.error('Error submitting report:', error);
        alert(error.message || t('Failed to submit report'));
    } finally {
        const submitBtn = document.querySelector('.submit-report-btn');
        if (submitBtn) {
            submitBtn.classList.remove('is-loading');
        }
    }
}

// Make functions globally available
window.openReportModal = openReportModal;
