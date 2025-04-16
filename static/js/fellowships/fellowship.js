// fellowship.js - Manages fellowship functionality

import { apiGet, apiPost, apiPut, apiDelete } from '../utils/api.js';
import { setupTabSwitching } from '../components/tabs.js';
import { t } from '../i18n.js';

// Current fellowship details for the modal
let currentFellowship = null;

// Document ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing fellowship page');
    
    // Set up tab switching
    setupTabSwitching();
    setupDetailTabSwitching();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load fellowship data
    loadFellowships();
});

/**
 * Set up event listeners for fellowship page
 */
function setupEventListeners() {
    // Create fellowship button
    document.getElementById('createFellowshipBtn').addEventListener('click', () => {
        openModal('createFellowshipModal');
    });
    
    // Save new fellowship
    document.getElementById('saveFellowshipBtn').addEventListener('click', createFellowship);
    
    // Join fellowship button
    document.getElementById('joinFellowshipBtn').addEventListener('click', joinFellowship);
    
    // Modal close buttons
    document.querySelectorAll('[data-close-modal]').forEach(button => {
        button.addEventListener('click', () => {
            const modalId = button.dataset.closeModal;
            closeModal(modalId);
        });
    });
    
    // Fellowship settings
    document.getElementById('saveFellowshipChangesBtn').addEventListener('click', saveFellowshipChanges);
    document.getElementById('leaveFellowshipBtn').addEventListener('click', leaveFellowship);
    document.getElementById('deleteFellowshipBtn').addEventListener('click', deleteFellowship);
    
    // Join code actions
    document.getElementById('regenerateCodeBtn').addEventListener('click', regenerateJoinCode);
    document.getElementById('copyCodeBtn').addEventListener('click', copyJoinCode);
    
    // Share prayer button
    document.getElementById('sharePrayerBtn').addEventListener('click', () => {
        loadUserPrayers();
        openModal('sharePrayerModal');
    });
}

/**
 * Set up tab switching for fellowship details
 */
function setupDetailTabSwitching() {
    const tabs = document.querySelectorAll('#fellowship-detail-tabs li');
    const tabContents = document.querySelectorAll('.detail-tab-content');
    
    if (tabs.length > 0 && tabContents.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                tabs.forEach(t => t.classList.remove('is-active'));
                
                // Add active class to clicked tab
                tab.classList.add('is-active');
                
                // Hide all tab contents
                tabContents.forEach(content => {
                    content.classList.add('is-hidden');
                });
                
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

/**
 * Load fellowships from the API
 */
async function loadFellowships() {
    try {
        const result = await apiGet('/api/fellowships');
        
        // Render user fellowships
        const userFellowshipsContainer = document.getElementById('my-fellowships-container');
        userFellowshipsContainer.innerHTML = '';
        
        if (result.user_fellowships.length === 0) {
            userFellowshipsContainer.innerHTML = `
                <div class="column is-12">
                    <div class="notification is-info">
                        ${t("You haven't joined any fellowships yet. Create a new fellowship or join an existing one with a join code.")}
                    </div>
                </div>
            `;
        } else {
            result.user_fellowships.forEach(fellowship => {
                const card = createFellowshipCard(fellowship, true);
                userFellowshipsContainer.appendChild(card);
            });
        }
        
        // Render public fellowships
        const publicFellowshipsContainer = document.getElementById('public-fellowships-container');
        publicFellowshipsContainer.innerHTML = '';
        
        if (result.public_fellowships.length === 0) {
            publicFellowshipsContainer.innerHTML = `
                <div class="column is-12">
                    <div class="notification is-info">
                        ${t('There are no public fellowships available to join at the moment.')}
                    </div>
                </div>
            `;
        } else {
            result.public_fellowships.forEach(fellowship => {
                const card = createFellowshipCard(fellowship, false);
                publicFellowshipsContainer.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading fellowships:', error);
        showError(t('Failed to load fellowships'));
    }
}

/**
 * Create a fellowship card element
 * @param {Object} fellowship - Fellowship data
 * @param {boolean} isMember - Whether the user is a member
 * @returns {HTMLElement} - The fellowship card element
 */
function createFellowshipCard(fellowship, isMember) {
    const column = document.createElement('div');
    column.className = 'column is-4';
    
    const privacyBadge = fellowship.is_private 
        ? `<span class="tag is-warning">${t('Private')}</span>` 
        : `<span class="tag is-success">${t('Public')}</span>`;
    
    const roleBadge = fellowship.user_role
        ? `<span class="tag is-info">${fellowship.user_role}</span>`
        : '';
        
    column.innerHTML = `
        <div class="card fellowship-card" data-fellowship-id="${fellowship.id}">
            <div class="card-content">
                <div class="media">
                    <div class="media-left">
                        <figure class="image is-48x48">
                            <img src="${fellowship.creator_pic || 'https://bulma.io/images/placeholders/48x48.png'}" 
                                alt="${t('Creator')}" 
                                onerror="this.src='https://bulma.io/images/placeholders/48x48.png'"
                                style="object-fit: cover; width: 48px; height: 48px; border-radius: 50%;">
                        </figure>
                    </div>
                    <div class="media-content">
                        <p class="title is-4">${fellowship.name}</p>
                        <p class="subtitle is-6">${t('by')} ${fellowship.creator_name}</p>
                    </div>
                </div>
                
                <div class="content">
                    <p>${fellowship.description || t('No description provided.')}</p>
                    <div class="tags">
                        ${privacyBadge}
                        ${roleBadge}
                        <span class="tag">
                            <span class="icon"><i class="fas fa-users"></i></span>
                            <span>${fellowship.member_count}</span>
                        </span>
                    </div>
                </div>
            </div>
            <footer class="card-footer">
                ${isMember 
                    ? `<a class="card-footer-item view-fellowship" data-fellowship-id="${fellowship.id}">
                        <span class="icon"><i class="fas fa-eye"></i></span>
                        <span>${t('View')}</span>
                       </a>`
                    : `<a class="card-footer-item join-public-fellowship" data-fellowship-id="${fellowship.id}">
                        <span class="icon"><i class="fas fa-sign-in-alt"></i></span>
                        <span>${t('Join')}</span>
                       </a>`
                }
            </footer>
        </div>
    `;
    
    // Add event listener for viewing fellowship
    const viewBtn = column.querySelector('.view-fellowship');
    if (viewBtn) {
        viewBtn.addEventListener('click', () => viewFellowship(fellowship.id));
    }
    
    // Add event listener for joining public fellowship
    const joinBtn = column.querySelector('.join-public-fellowship');
    if (joinBtn) {
        joinBtn.addEventListener('click', () => joinPublicFellowship(fellowship.id));
    }
    
    return column;
}

/**
 * Create a new fellowship
 */
async function createFellowship() {
    const nameInput = document.getElementById('fellowshipName');
    const descriptionInput = document.getElementById('fellowshipDescription');
    const privacyRadios = document.getElementsByName('fellowshipPrivacy');
    
    const name = nameInput.value.trim();
    const description = descriptionInput.value.trim();
    let isPrivate = true;
    
    // Get selected privacy option
    for (const radio of privacyRadios) {
        if (radio.checked) {
            isPrivate = radio.value === 'private';
            break;
        }
    }
    
    if (!name) {
        showError(t('Please enter a fellowship name'));
        return;
    }
    
    try {
        // Show loading state
        const saveBtn = document.getElementById('saveFellowshipBtn');
        saveBtn.classList.add('is-loading');
        
        // Create the fellowship
        const result = await apiPost('/api/fellowships', {
            name,
            description,
            is_private: isPrivate
        });
        
        // Close modal and reset form
        closeModal('createFellowshipModal');
        nameInput.value = '';
        descriptionInput.value = '';
        
        // Reload fellowships
        loadFellowships();
        
        // Show success message with join code if private
        if (result.fellowship.is_private && result.fellowship.join_code) {
            showSuccess(
                `${t('Fellowship created successfully!')} ${t('Join code')}: <strong>${result.fellowship.join_code}</strong>. ${t('Share this code with others to invite them.')}`
            );
        } else {
            showSuccess(t('Fellowship created successfully!'));
        }
    } catch (error) {
        console.error('Error creating fellowship:', error);
        showError(error.message || t('Failed to create fellowship'));
    } finally {
        const saveBtn = document.getElementById('saveFellowshipBtn');
        saveBtn.classList.remove('is-loading');
    }
}

/**
 * Join a fellowship using the join code
 */
async function joinFellowship() {
    const joinCodeInput = document.getElementById('joinCodeInput');
    const joinCode = joinCodeInput.value.trim();
    
    if (!joinCode) {
        showError(t('Please enter a join code'));
        return;
    }
    
    try {
        // Show loading state
        const joinBtn = document.getElementById('joinFellowshipBtn');
        joinBtn.classList.add('is-loading');
        
        // Join the fellowship
        const result = await apiPost('/api/fellowships/join', {
            join_code: joinCode
        });
        
        // Reset input
        joinCodeInput.value = '';
        
        // Reload fellowships
        loadFellowships();
        
        // Show success message
        showSuccess(t('Joined fellowship successfully!'));
        
        // Switch to My Fellowships tab
        const myFellowshipsTab = document.querySelector('#fellowship-tabs li[data-target="my-fellowships-tab"]');
        if (myFellowshipsTab) {
            myFellowshipsTab.click();
        }
    } catch (error) {
        console.error('Error joining fellowship:', error);
        showError(error.message || t('Failed to join fellowship'));
    } finally {
        const joinBtn = document.getElementById('joinFellowshipBtn');
        joinBtn.classList.remove('is-loading');
    }
}

/**
 * Join a public fellowship
 * @param {number} fellowshipId - The ID of the fellowship to join
 */
async function joinPublicFellowship(fellowshipId) {
    try {
        // Join the fellowship (public fellowships don't need a join code)
        const result = await apiPost('/api/fellowships/join', {
            fellowship_id: fellowshipId
        });
        
        // Reload fellowships
        loadFellowships();
        
        // Show success message
        showSuccess(t('Joined fellowship successfully!'));
        
        // Switch to My Fellowships tab
        const myFellowshipsTab = document.querySelector('#fellowship-tabs li[data-target="my-fellowships-tab"]');
        if (myFellowshipsTab) {
            myFellowshipsTab.click();
        }
    } catch (error) {
        console.error('Error joining public fellowship:', error);
        showError(error.message || t('Failed to join fellowship'));
    }
}

/**
 * View fellowship details
 * @param {number} fellowshipId - The ID of the fellowship to view
 */
async function viewFellowship(fellowshipId) {
    try {
        // Show loading state in modal
        document.getElementById('fellowship-prayers-container').innerHTML = `
            <div class="has-text-centered is-loading">
                <span class="icon is-large">
                    <i class="fas fa-spinner fa-pulse fa-2x"></i>
                </span>
            </div>
        `;
        
        document.getElementById('fellowship-members-container').innerHTML = `
            <div class="has-text-centered is-loading">
                <span class="icon is-large">
                    <i class="fas fa-spinner fa-pulse fa-2x"></i>
                </span>
            </div>
        `;
        
        // Reset to prayers tab
        const prayersTab = document.querySelector('#fellowship-detail-tabs li[data-target="fellowship-prayers-tab"]');
        if (prayersTab) {
            prayersTab.click();
        }
        
        // Get fellowship details
        const fellowship = await apiGet(`/api/fellowships/${fellowshipId}`);
        currentFellowship = fellowship;
        
        // Set modal title
        document.getElementById('fellowshipDetailsTitle').textContent = fellowship.name;
        
        // Render prayers
        renderFellowshipPrayers(fellowship.prayers);
        
        // Render members
        renderFellowshipMembers(fellowship.members);
        
        // Populate settings form if user is admin
        if (fellowship.user_role === 'admin') {
            document.getElementById('editFellowshipName').value = fellowship.name || '';
            document.getElementById('editFellowshipDescription').value = fellowship.description || '';
            
            // Set privacy radio
            const privateRadio = document.querySelector('input[name="editFellowshipPrivacy"][value="private"]');
            const publicRadio = document.querySelector('input[name="editFellowshipPrivacy"][value="public"]');
            
            if (fellowship.is_private) {
                privateRadio.checked = true;
                publicRadio.checked = false;
                
                // Show and populate join code
                document.getElementById('joinCodeSection').style.display = 'block';
                document.getElementById('fellowshipJoinCode').value = fellowship.join_code || '';
            } else {
                privateRadio.checked = false;
                publicRadio.checked = true;
                
                // Hide join code section
                document.getElementById('joinCodeSection').style.display = 'none';
            }
            
            // Show settings tab
            document.getElementById('settings-tab-btn').style.display = 'block';
        } else {
            // Hide settings tab for non-admins
            document.getElementById('settings-tab-btn').style.display = 'none';
        }
        
        // Open the modal
        openModal('fellowshipDetailsModal');
    } catch (error) {
        console.error('Error viewing fellowship:', error);
        showError(error.message || t('Failed to load fellowship details'));
    }
}

/**
 * Render fellowship prayers
 * @param {Array} prayers - List of prayers in the fellowship
 */
function renderFellowshipPrayers(prayers) {
    const container = document.getElementById('fellowship-prayers-container');
    
    if (!prayers || prayers.length === 0) {
        container.innerHTML = `
            <div class="notification is-info">
                ${t('No prayers have been shared in this fellowship yet.')}
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    
    prayers.forEach(prayer => {
        const prayerElement = document.createElement('div');
        prayerElement.className = 'box';
        
        const answeredBadge = prayer.is_answered 
            ? `<span class="tag is-success">${t('Answered')}</span>` 
            : '';
            
        prayerElement.innerHTML = `
            <article class="media">
                <div class="media-left">
                    <figure class="image is-48x48">
                        <img src="${prayer.user_pic || 'https://bulma.io/images/placeholders/48x48.png'}" 
                            alt="${t('User')}" 
                            onerror="this.src='https://bulma.io/images/placeholders/48x48.png'"
                            style="object-fit: cover; width: 48px; height: 48px; border-radius: 50%;">
                    </figure>
                </div>
                <div class="media-content">
                    <div class="content">
                        <p>
                            <strong>${prayer.title}</strong>
                            <small>${t('by')} ${prayer.user_name}</small>
                            <small>${formatDate(prayer.created_at)}</small>
                            ${answeredBadge}
                            <br>
                            ${prayer.content}
                        </p>
                        ${prayer.is_answered && prayer.answer ? `
                            <p class="has-text-success">
                                <strong>${t('How It Was Answered:')}</strong> ${prayer.answer}
                            </p>
                        ` : ''}
                    </div>
                    <div class="level is-mobile">
                        <div class="level-left">
                            <button class="level-item button is-small prayer-interact-button" data-prayer-id="${prayer.id}" data-interaction-type="${prayer.is_answered ? 'praise' : 'pray'}">
                                <span class="icon is-small">
                                    <i class="fas fa-${prayer.is_answered ? 'heart' : 'pray'}"></i>
                                </span>
                                <span>${prayer.is_answered ? t('Praise') : t('Pray')}</span>
                            </button>
                        </div>
                        <div class="level-right">
                            <small class="has-text-grey">${t('Shared')}: ${formatDate(prayer.shared_at)}</small>
                        </div>
                    </div>
                </div>
            </article>
        `;
        
        container.appendChild(prayerElement);
    });
}

/**
 * Render fellowship members
 * @param {Array} members - List of members in the fellowship
 */
function renderFellowshipMembers(members) {
    const container = document.getElementById('fellowship-members-container');
    
    if (!members || members.length === 0) {
        container.innerHTML = `
            <div class="notification is-info">
                ${t('No members found.')}
            </div>
        `;
        return;
    }
    
    // Sort members by role (admin first, then moderator, then member)
    const sortedMembers = [...members].sort((a, b) => {
        const roleOrder = { 'admin': 0, 'moderator': 1, 'member': 2 };
        return roleOrder[a.role] - roleOrder[b.role];
    });
    
    container.innerHTML = '';
    
    sortedMembers.forEach(member => {
        const memberElement = document.createElement('div');
        memberElement.className = 'box';
        
        let roleBadge = '';
        if (member.role === 'admin') {
            roleBadge = `<span class="tag is-danger">${t('Admin')}</span>`;
        } else if (member.role === 'moderator') {
            roleBadge = `<span class="tag is-warning">${t('Moderator')}</span>`;
        } else {
            roleBadge = `<span class="tag is-info">${t('Member')}</span>`;
        }
        
        // Only show actions if current user is admin
        const canManage = currentFellowship.user_role === 'admin';
        
        memberElement.innerHTML = `
            <div class="media">
                <div class="media-left">
                    <figure class="image is-48x48">
                        <img src="${member.profile_pic || 'https://bulma.io/images/placeholders/48x48.png'}" 
                            alt="${t('User')}" 
                            onerror="this.src='https://bulma.io/images/placeholders/48x48.png'"
                            style="object-fit: cover; width: 48px; height: 48px; border-radius: 50%;">
                    </figure>
                </div>
                <div class="media-content">
                    <div class="content">
                        <p>
                            <strong>${member.name}</strong>
                            ${roleBadge}
                            <br>
                            <small>${member.email}</small>
                            <br>
                            <small>${t('Joined')}: ${formatDate(member.joined_at)}</small>
                        </p>
                    </div>
                </div>
                ${canManage && member.user_id !== currentFellowship.created_by ? `
                    <div class="media-right">
                        <div class="dropdown is-hoverable is-right">
                            <div class="dropdown-trigger">
                                <button class="button is-small" aria-haspopup="true" aria-controls="dropdown-menu">
                                    <span class="icon is-small">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </span>
                                </button>
                            </div>
                            <div class="dropdown-menu" id="dropdown-menu" role="menu">
                                <div class="dropdown-content">
                                    <a class="dropdown-item set-role" data-user-id="${member.user_id}" data-role="admin">
                                        ${t('Make Admin')}
                                    </a>
                                    <a class="dropdown-item set-role" data-user-id="${member.user_id}" data-role="moderator">
                                        ${t('Make Moderator')}
                                    </a>
                                    <a class="dropdown-item set-role" data-user-id="${member.user_id}" data-role="member">
                                        ${t('Set as Member')}
                                    </a>
                                    <hr class="dropdown-divider">
                                    <a class="dropdown-item has-text-danger remove-member" data-user-id="${member.user_id}">
                                        ${t('Remove from Fellowship')}
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        container.appendChild(memberElement);
        
        // Add event listeners for admin actions
        if (canManage && member.user_id !== currentFellowship.created_by) {
            const roleButtons = memberElement.querySelectorAll('.set-role');
            roleButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const userId = button.dataset.userId;
                    const role = button.dataset.role;
                    updateMemberRole(userId, role);
                });
            });
            
            const removeButton = memberElement.querySelector('.remove-member');
            if (removeButton) {
                removeButton.addEventListener('click', () => {
                    const userId = removeButton.dataset.userId;
                    removeMember(userId);
                });
            }
        }
    });
}

/**
 * Update a member's role
 * @param {string} userId - The ID of the user to update
 * @param {string} role - The new role (admin, moderator, member)
 */
async function updateMemberRole(userId, role) {
    if (!currentFellowship) return;
    
    try {
        await apiPut(`/api/fellowships/${currentFellowship.id}/members/${userId}`, {
            role: role
        });
        
        // Refresh fellowship view
        viewFellowship(currentFellowship.id);
        
        showSuccess(t('Member role updated successfully'));
    } catch (error) {
        console.error('Error updating member role:', error);
        showError(error.message || t('Failed to update member role'));
    }
}

/**
 * Remove a member from the fellowship
 * @param {string} userId - The ID of the user to remove
 */
async function removeMember(userId) {
    if (!currentFellowship) return;
    
    if (!confirm(t('Are you sure you want to remove this member from the fellowship?'))) {
        return;
    }
    
    try {
        await apiDelete(`/api/fellowships/${currentFellowship.id}/members/${userId}`);
        
        // Refresh fellowship view
        viewFellowship(currentFellowship.id);
        
        showSuccess(t('Member removed successfully'));
    } catch (error) {
        console.error('Error removing member:', error);
        showError(error.message || t('Failed to remove member'));
    }
}

/**
 * Save fellowship changes
 */
async function saveFellowshipChanges() {
    if (!currentFellowship) return;
    
    const nameInput = document.getElementById('editFellowshipName');
    const descriptionInput = document.getElementById('editFellowshipDescription');
    const privacyRadios = document.getElementsByName('editFellowshipPrivacy');
    
    const name = nameInput.value.trim();
    const description = descriptionInput.value.trim();
    let isPrivate = true;
    
    // Get selected privacy option
    for (const radio of privacyRadios) {
        if (radio.checked) {
            isPrivate = radio.value === 'private';
            break;
        }
    }
    
    if (!name) {
        showError(t('Please enter a fellowship name'));
        return;
    }
    
    try {
        // Show loading state
        const saveBtn = document.getElementById('saveFellowshipChangesBtn');
        saveBtn.classList.add('is-loading');
        
        // Update the fellowship
        await apiPut(`/api/fellowships/${currentFellowship.id}`, {
            name,
            description,
            is_private: isPrivate
        });
        
        // Refresh fellowship view
        closeModal('fellowshipDetailsModal');
        loadFellowships();
        
        showSuccess(t('Fellowship updated successfully'));
    } catch (error) {
        console.error('Error updating fellowship:', error);
        showError(error.message || t('Failed to update fellowship'));
    } finally {
        const saveBtn = document.getElementById('saveFellowshipChangesBtn');
        saveBtn.classList.remove('is-loading');
    }
}

/**
 * Leave the current fellowship
 */
async function leaveFellowship() {
    if (!currentFellowship) return;
    
    if (!confirm(t('Are you sure you want to leave this fellowship?'))) {
        return;
    }
    
    try {
        await apiDelete(`/api/fellowships/${currentFellowship.id}/members/${currentFellowship.user_id}`);
        
        // Close modal and reload fellowships
        closeModal('fellowshipDetailsModal');
        loadFellowships();
        
        showSuccess(t('Left fellowship successfully'));
    } catch (error) {
        console.error('Error leaving fellowship:', error);
        showError(error.message || t('Failed to leave fellowship'));
    }
}

/**
 * Delete the current fellowship
 */
async function deleteFellowship() {
    if (!currentFellowship) return;
    
    if (!confirm(t('Are you sure you want to delete this fellowship? This cannot be undone.'))) {
        return;
    }
    
    try {
        await apiDelete(`/api/fellowships/${currentFellowship.id}`);
        
        // Close modal and reload fellowships
        closeModal('fellowshipDetailsModal');
        loadFellowships();
        
        showSuccess(t('Fellowship deleted successfully'));
    } catch (error) {
        console.error('Error deleting fellowship:', error);
        showError(error.message || t('Failed to delete fellowship'));
    }
}

/**
 * Regenerate the join code for the current fellowship
 */
async function regenerateJoinCode() {
    if (!currentFellowship || !currentFellowship.is_private) return;
    
    try {
        // Show loading state
        const regenerateBtn = document.getElementById('regenerateCodeBtn');
        regenerateBtn.classList.add('is-loading');
        
        // Regenerate the join code
        const result = await apiPost(`/api/fellowships/${currentFellowship.id}/regenerate-code`, {});
        
        // Update the join code field
        document.getElementById('fellowshipJoinCode').value = result.join_code;
        
        showSuccess(t('Join code regenerated successfully'));
    } catch (error) {
        console.error('Error regenerating join code:', error);
        showError(error.message || t('Failed to regenerate join code'));
    } finally {
        const regenerateBtn = document.getElementById('regenerateCodeBtn');
        regenerateBtn.classList.remove('is-loading');
    }
}

/**
 * Copy the join code to the clipboard
 */
function copyJoinCode() {
    const joinCodeInput = document.getElementById('fellowshipJoinCode');
    joinCodeInput.select();
    document.execCommand('copy');
    
    showSuccess(t('Join code copied to clipboard'));
}

/**
 * Load user prayers for sharing
 */
async function loadUserPrayers() {
    if (!currentFellowship) return;
    
    try {
        const container = document.getElementById('user-prayers-container');
        container.innerHTML = `
            <div class="has-text-centered is-loading">
                <span class="icon is-large">
                    <i class="fas fa-spinner fa-pulse fa-2x"></i>
                </span>
            </div>
        `;
        
        // Get user prayers
        const result = await apiGet('/api/prayers');
        
        if (!result || result.length === 0) {
            container.innerHTML = `
                <div class="notification is-info">
                    ${t("You don't have any prayers to share. Create prayers from your dashboard first.")}
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        
        // Create buttons for each prayer
        result.forEach(prayer => {
            const prayerElement = document.createElement('div');
            prayerElement.className = 'box';
            
            const answeredBadge = prayer.is_answered 
                ? `<span class="tag is-success">${t('Answered')}</span>` 
                : '';
                
            const publicBadge = prayer.is_public
                ? `<span class="tag is-info">${t('Public')}</span>`
                : `<span class="tag is-light">${t('Private')}</span>`;
                
            prayerElement.innerHTML = `
                <div class="content">
                    <p>
                        <strong>${prayer.title}</strong>
                        <small>${formatDate(prayer.created_at)}</small>
                        ${answeredBadge}
                        ${publicBadge}
                        <br>
                        ${prayer.content}
                    </p>
                    ${prayer.is_answered && prayer.answer ? `
                        <p class="has-text-success">
                            <strong>${t('How It Was Answered:')}</strong> ${prayer.answer}
                        </p>
                    ` : ''}
                </div>
                <button class="button is-primary share-prayer-btn" data-prayer-id="${prayer.id}">
                    <span class="icon"><i class="fas fa-share"></i></span>
                    <span>${t('Share with Fellowship')}</span>
                </button>
            `;
            
            container.appendChild(prayerElement);
            
            // Add event listener for sharing
            const shareBtn = prayerElement.querySelector('.share-prayer-btn');
            shareBtn.addEventListener('click', () => {
                sharePrayer(prayer.id);
            });
        });
    } catch (error) {
        console.error('Error loading user prayers:', error);
        showError(error.message || t('Failed to load prayers'));
    }
}

/**
 * Share a prayer with the current fellowship
 * @param {number} prayerId - The ID of the prayer to share
 */
async function sharePrayer(prayerId) {
    if (!currentFellowship) return;
    
    try {
        // Share the prayer
        await apiPost(`/api/fellowships/${currentFellowship.id}/prayers`, {
            prayer_id: prayerId
        });
        
        // Close modal and refresh fellowship view
        closeModal('sharePrayerModal');
        viewFellowship(currentFellowship.id);
        
        showSuccess(t('Prayer shared successfully'));
    } catch (error) {
        console.error('Error sharing prayer:', error);
        showError(error.message || t('Failed to share prayer'));
    }
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