// interactions.js - Handles prayer interaction functionality (pray, praise)

import { apiPost } from '../utils/api.js';

/**
 * Set up event handlers for prayer interaction buttons (pray, praise)
 */
export function setupPrayerInteractions() {
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
                    
                    const result = await interactWithPrayer(prayerId, interactionType);
                    
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
                } catch (error) {
                    console.error('Error with prayer interaction:', error);
                    // Show error feedback
                    button.classList.add('is-danger');
                    setTimeout(() => {
                        button.classList.remove('is-danger');
                    }, 1500);
                } finally {
                    button.classList.remove('is-loading');
                }
            });
        });
    }
}

/**
 * Interact with a prayer (pray or praise)
 * @param {number} prayerId - The ID of the prayer to interact with
 * @param {string} interactionType - The type of interaction ('pray' or 'praise')
 * @returns {Promise} - Promise that resolves with the interaction result
 */
async function interactWithPrayer(prayerId, interactionType) {
    try {
        return await apiPost(`/api/prayers/${prayerId}/interact`, {
            type: interactionType
        });
    } catch (error) {
        console.error('API error with prayer interaction:', error);
        throw new Error(error.message || 'Failed to record interaction');
    }
}