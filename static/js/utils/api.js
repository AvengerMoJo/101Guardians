// api.js - API utilities for making requests

/**
 * Make a GET request to the API
 * @param {string} url - The URL to fetch
 * @returns {Promise} - Promise that resolves with the API response
 */
export async function apiGet(url) {
    const response = await fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `API error: ${response.status}`);
    }
    
    return response.json();
}

/**
 * Make a POST request to the API
 * @param {string} url - The URL to post to
 * @param {object} data - The data to send
 * @returns {Promise} - Promise that resolves with the API response
 */
export async function apiPost(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `API error: ${response.status}`);
    }
    
    return response.json();
}

/**
 * Make a PUT request to the API
 * @param {string} url - The URL to put to
 * @param {object} data - The data to send
 * @returns {Promise} - Promise that resolves with the API response
 */
export async function apiPut(url, data) {
    const response = await fetch(url, {
        method: 'PUT',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `API error: ${response.status}`);
    }
    
    return response.json();
}

/**
 * Make a DELETE request to the API
 * @param {string} url - The URL to delete
 * @returns {Promise} - Promise that resolves with the API response
 */
export async function apiDelete(url) {
    const response = await fetch(url, {
        method: 'DELETE',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `API error: ${response.status}`);
    }
    
    return response.json();
}