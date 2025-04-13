// main.js - Main entry point for JavaScript application

// Import all modules
import { setupNavbarToggle } from './components/navbar.js';
import { setupTabSwitching } from './components/tabs.js';
import { setupDashboardForm } from './prayers/form.js';
import { setupPrayerInteractions } from './prayers/interactions.js';
import { setupLanguageSwitcher } from './i18n.js';

// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded - initializing scripts');
    
    // Initialize UI components
    setupNavbarToggle();
    setupTabSwitching();
    
    // Initialize prayer functionality
    setupDashboardForm();
    setupPrayerInteractions();
    
    // Initialize i18n functionality
    setupLanguageSwitcher();
    
    // Log successful initialization
    console.log('All components initialized successfully');
});