// main.js - Enhanced with debugging and improved functionality

document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle for navbar
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

    // Dashboard data entry form functionality
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
            dataForm.classList.remove('is-hidden');
        });
        
        cancelDataBtn.addEventListener('click', () => {
            dataForm.classList.add('is-hidden');
            dataTitle.value = '';
            dataContent.value = '';
        });
        
        // Save data with improved error handling
        saveDataBtn.addEventListener('click', async () => {
            const title = dataTitle.value.trim();
            const content = dataContent.value.trim();
            
            if (!title || !content) {
                alert('Please fill in all fields');
                return;
            }
            
            try {
                console.log('Submitting data:', { title, content });
                
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
                    console.log('Data saved successfully');
                    // Reload page to show the new data
                    window.location.reload();
                } else {
                    const errorData = await response.json();
                    console.error('Server error:', errorData);
                    alert(errorData.error || 'Failed to save data');
                }
            } catch (error) {
                console.error('Fetch error:', error);
                alert('An error occurred while saving data');
            }
        });
    }
});
