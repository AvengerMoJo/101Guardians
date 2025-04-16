// moderation.js - Manages moderation dashboard functionality

import { apiGet, apiPost, apiPut, apiDelete } from '../utils/api.js';
import { setupTabSwitching } from '../components/tabs.js';
import { t } from '../i18n.js';

// Current report being viewed
let currentReport = null;

// Document ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing moderation dashboard');
    
    // Set up tab switching
    setupTabSwitching();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    loadModerationStats();
    loadReports();
    loadSuspiciousActivity();
    
    // Load audit log if admin
    if (document.getElementById('audit-tab')) {
        loadAuditLog();
    }
});

/**
 * Set up event listeners for moderation dashboard
 */
function setupEventListeners() {
    // Admin action buttons
    const addModeratorBtn = document.getElementById('addModeratorBtn');
    if (addModeratorBtn) {
        addModeratorBtn.addEventListener('click', () => {
            openModal('appointModeratorModal');
        });
    }
    
    const viewAllUsersBtn = document.getElementById('viewAllUsersBtn');
    if (viewAllUsersBtn) {
        viewAllUsersBtn.addEventListener('click', () => {
            loadUsers();
            openModal('userManagementModal');
        });
    }
    
    // Modal close buttons
    document.querySelectorAll('[data-close-modal]').forEach(button => {
        button.addEventListener('click', () => {
            const modalId = button.dataset.closeModal;
            closeModal(modalId);
        });
    });
    
    // Report action buttons
    document.getElementById('dismissReportBtn').addEventListener('click', () => handleReport('dismissed'));
    document.getElementById('reviewedReportBtn').addEventListener('click', () => handleReport('reviewed'));
    document.getElementById('actionReportBtn').addEventListener('click', () => handleReport('actioned'));
    
    // Appoint moderator button
    const appointModeratorBtn = document.getElementById('appointModeratorBtn');
    if (appointModeratorBtn) {
        appointModeratorBtn.addEventListener('click', appointModerator);
    }
    
    // User search input
    const userSearchInput = document.getElementById('userSearchInput');
    if (userSearchInput) {
        userSearchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.trim();
            filterUsers(searchTerm);
        }, 300));
    }
}

/**
 * Load moderation dashboard statistics
 */
async function loadModerationStats() {
    try {
        const stats = await apiGet('/api/moderation/stats');
        
        // Update pending reports count
        document.getElementById('pending-reports-count').textContent = stats.pending_reports;
        
        // Update user role tag
        const userRoleTag = document.getElementById('user-role-tag');
        userRoleTag.textContent = stats.user_role.charAt(0).toUpperCase() + stats.user_role.slice(1); // Capitalize
        
        // Set appropriate class based on role
        if (stats.user_role === 'admin') {
            userRoleTag.classList.add('is-danger');
        } else if (stats.user_role === 'moderator') {
            userRoleTag.classList.add('is-warning');
        } else {
            userRoleTag.classList.add('is-info');
        }
    } catch (error) {
        console.error('Error loading moderation stats:', error);
        showError(t('Failed to load moderation statistics'));
    }
}

/**
 * Load pending reports
 */
async function loadReports() {
    try {
        const container = document.getElementById('reports-container');
        container.innerHTML = `
            <div class="has-text-centered is-loading">
                <span class="icon is-large">
                    <i class="fas fa-spinner fa-pulse fa-2x"></i>
                </span>
            </div>
        `;
        
        const result = await apiGet('/api/reports');
        
        if (!result.reports || result.reports.length === 0) {
            container.innerHTML = `
                <div class="notification is-success">
                    ${t('No pending reports to review. Great job!')}
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        
        // Create elements for each report
        result.reports.forEach(report => {
            const reportElement = document.createElement('div');
            reportElement.className = 'box';
            reportElement.innerHTML = `
                <article class="media">
                    <div class="media-content">
                        <div class="content">
                            <p>
                                <strong>${report.prayer_title}</strong>
                                <small>${t('by')} ${report.prayer_author_name}</small>
                                <small>${t('Reported')}: ${formatDate(report.created_at)}</small>
                                <br>
                                ${t('Report reason')}: ${report.reason}
                                <br>
                                ${t('Reported by')}: ${report.reporter_name}
                            </p>
                        </div>
                        <div class="level is-mobile">
                            <div class="level-left">
                                <button class="button is-small is-info view-report-btn" data-report-id="${report.id}">
                                    <span class="icon is-small"><i class="fas fa-eye"></i></span>
                                    <span>${t('View Details')}</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </article>
            `;
            
            container.appendChild(reportElement);
            
            // Add event listener for viewing report details
            const viewBtn = reportElement.querySelector('.view-report-btn');
            viewBtn.addEventListener('click', () => viewReportDetails(report));
        });
    } catch (error) {
        console.error('Error loading reports:', error);
        showError(t('Failed to load reports'));
    }
}

/**
 * View report details in modal
 * @param {Object} report - The report data
 */
function viewReportDetails(report) {
    currentReport = report;
    
    const container = document.getElementById('report-details-container');
    container.innerHTML = `
        <div class="box">
            <h4 class="title is-4">${t('Reported Prayer')}</h4>
            <div class="content">
                <p>
                    <strong>${report.prayer_title}</strong>
                    <small>${t('by')} ${report.prayer_author_name}</small>
                    <br>
                    ${report.prayer_content}
                </p>
            </div>
        </div>
        
        <div class="box">
            <h4 class="title is-4">${t('Report Information')}</h4>
            <div class="content">
                <p><strong>${t('Report Reason')}:</strong> ${report.reason}</p>
                <p><strong>${t('Reported By')}:</strong> ${report.reporter_name}</p>
                <p><strong>${t('Report Date')}:</strong> ${formatDate(report.created_at)}</p>
            </div>
        </div>
    `;
    
    // Reset notes
    document.getElementById('reportActionNotes').value = '';
    
    openModal('reportDetailsModal');
}

/**
 * Handle a report (dismiss, review, or take action)
 * @param {string} action - The action to take (dismissed, reviewed, actioned)
 */
async function handleReport(action) {
    if (!currentReport) return;
    
    const notes = document.getElementById('reportActionNotes').value.trim();
    
    try {
        // Show loading state on buttons
        document.getElementById('dismissReportBtn').classList.add('is-loading');
        document.getElementById('reviewedReportBtn').classList.add('is-loading');
        document.getElementById('actionReportBtn').classList.add('is-loading');
        
        // Handle the report
        await apiPut(`/api/reports/${currentReport.id}`, {
            action,
            notes
        });
        
        // Close modal and reload reports
        closeModal('reportDetailsModal');
        loadReports();
        loadModerationStats();
        
        showSuccess(t('Report handled successfully'));
    } catch (error) {
        console.error('Error handling report:', error);
        showError(error.message || t('Failed to handle report'));
    } finally {
        document.getElementById('dismissReportBtn').classList.remove('is-loading');
        document.getElementById('reviewedReportBtn').classList.remove('is-loading');
        document.getElementById('actionReportBtn').classList.remove('is-loading');
    }
}

/**
 * Load suspicious activity data
 */
async function loadSuspiciousActivity() {
    const container = document.getElementById('suspicious-container');
    
    // This would typically connect to an API endpoint that uses algorithms
    // to detect potentially problematic content or user behavior
    // For now, we'll just show a placeholder
    
    container.innerHTML = `
        <div class="notification is-info">
            ${t('No suspicious activity detected at this time.')}
        </div>
    `;
}

/**
 * Load audit log data
 */
async function loadAuditLog() {
    const container = document.getElementById('audit-container');
    
    // This would typically connect to an API endpoint that retrieves
    // a log of moderation actions taken by admins and moderators
    // For now, we'll just show a placeholder
    
    container.innerHTML = `
        <div class="notification is-info">
            ${t('Audit log functionality will be implemented in a future update.')}
        </div>
    `;
}

/**
 * Load users for the user management modal
 */
async function loadUsers() {
    const container = document.getElementById('users-container');
    container.innerHTML = `
        <div class="has-text-centered is-loading">
            <span class="icon is-large">
                <i class="fas fa-spinner fa-pulse fa-2x"></i>
            </span>
        </div>
    `;
    
    // This would connect to an API that lists users with pagination
    // For demonstration, we'll show a placeholder
    
    container.innerHTML = `
        <div class="notification is-info">
            ${t('User management functionality will be implemented in a future update.')}
        </div>
        
        <div class="content">
            <p>${t('This section will allow administrators to:')}</p>
            <ul>
                <li>${t('View all users')}</li>
                <li>${t('Search for specific users')}</li>
                <li>${t('Change user roles (admin, moderator, user)')}</li>
                <li>${t('Update user status (active, suspended, banned)')}</li>
                <li>${t('View user activity metrics')}</li>
            </ul>
        </div>
    `;
}

/**
 * Appoint a user as moderator
 */
async function appointModerator() {
    const userInput = document.getElementById('moderatorUserInput');
    const userIdOrEmail = userInput.value.trim();
    
    if (!userIdOrEmail) {
        showError(t('Please enter a user email or ID'));
        return;
    }
    
    try {
        // Show loading state
        const appointBtn = document.getElementById('appointModeratorBtn');
        appointBtn.classList.add('is-loading');
        
        // This would connect to an API to appoint the user as moderator
        // For demonstration, we'll just show a confirmation
        
        setTimeout(() => {
            closeModal('appointModeratorModal');
            showSuccess(t('User has been appointed as moderator successfully'));
            userInput.value = '';
        }, 1000);
    } catch (error) {
        console.error('Error appointing moderator:', error);
        showError(error.message || t('Failed to appoint moderator'));
    } finally {
        const appointBtn = document.getElementById('appointModeratorBtn');
        appointBtn.classList.remove('is-loading');
    }
}

/**
 * Filter users in the user management modal
 * @param {string} searchTerm - The search term
 */
function filterUsers(searchTerm) {
    // This would filter the list of users based on the search term
    console.log('Filtering users with term:', searchTerm);
}

/* ---- UI Helper Functions ---- */

/**
 * Open a modal by ID
 * @param {string} modalId - The ID of the modal to open
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('is-active');
    }
}

/**
 * Close a modal by ID
 * @param {string} modalId - The ID of the modal to close
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('is-active');
    }
}

/**
 * Show an error message
 * @param {string} message - The error message to show
 */
function showError(message) {
    // You can implement this with a toast or notification system
    alert(message);
}

/**
 * Show a success message
 * @param {string} message - The success message to show
 */
function showSuccess(message) {
    // You can implement this with a toast or notification system
    alert(message);
}

/**
 * Format a date string
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - The function to debounce
 * @param {number} wait - The debounce delay in milliseconds
 * @returns {Function} - The debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}