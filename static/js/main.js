// Main JavaScript file for the application

document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle functionality
    const navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
    
    if (navbarBurgers.length > 0) {
        navbarBurgers.forEach(el => {
            el.addEventListener('click', () => {
                const target = document.getElementById(el.dataset.target);
                el.classList.toggle('is-active');
                target.classList.toggle('is-active');
            });
        });
    }
    
    // Add notification functionality
    function showNotification(message, type = 'is-info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1000';
        notification.style.minWidth = '300px';
        
        // Add delete button
        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete';
        deleteButton.addEventListener('click', () => {
            notification.remove();
        });
        
        notification.appendChild(deleteButton);
        notification.appendChild(document.createTextNode(message));
        
        // Add to body
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Make the notification function global
    window.showNotification = showNotification;
    
    // Add form validation for any forms in the application
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-danger');
                } else {
                    field.classList.remove('is-danger');
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                showNotification('Please fill in all required fields', 'is-danger');
            }
        });
    });
    
    // Add input event listeners to remove error class when user types
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            if (input.classList.contains('is-danger')) {
                input.classList.remove('is-danger');
            }
        });
    });
});

// API helper function for making requests
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request error:', error);
        window.showNotification('An error occurred while communicating with the server', 'is-danger');
        throw error;
    }
}

// Make API helper global
window.apiRequest = apiRequest;:
