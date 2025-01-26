// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabLinks = document.querySelectorAll('.admin-nav a');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            tabLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link and corresponding section
            this.classList.add('active');
            const targetId = this.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Initialize search functionality
    initializeSearch();
    
    // Initialize feature card animations
    initializeAnimations();
});

// Search functionality
function initializeSearch() {
    const userSearch = document.getElementById('userSearch');
    if (userSearch) {
        userSearch.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('.admin-table tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
}

// Volunteer application handling
function approveVolunteer(id) {
    if (confirm('Are you sure you want to approve this volunteer?')) {
        sendRequest(`/admin/approve-volunteer/${id}`, 'POST')
            .then(data => {
                if (data.success) {
                    showNotification('Volunteer approved successfully!', 'success');
                    setTimeout(() => window.location.reload(), 1000);
                }
            });
    }
}

function rejectVolunteer(id) {
    if (confirm('Are you sure you want to reject this volunteer?')) {
        sendRequest(`/admin/reject-volunteer/${id}`, 'POST')
            .then(data => {
                if (data.success) {
                    showNotification('Volunteer rejected successfully!', 'success');
                    setTimeout(() => window.location.reload(), 1000);
                }
            });
    }
}

// Disaster management
function addDisaster() {
    window.location.href = '/admin/add-disaster';
}

function editDisaster(id) {
    window.location.href = `/admin/edit-disaster/${id}`;
}

function deleteDisaster(id) {
    if (confirm('Are you sure you want to delete this disaster zone?')) {
        sendRequest(`/admin/delete-disaster/${id}`, 'POST')
            .then(data => {
                if (data.success) {
                    showNotification('Disaster zone deleted successfully!', 'success');
                    setTimeout(() => window.location.reload(), 1000);
                }
            });
    }
}

// Helper functions
async function sendRequest(url, method = 'GET', data = null) {
    try {
        // Get CSRF token if it exists
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken || ''
            },
            credentials: 'same-origin'
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || 'Operation failed');
        }
        
        return result;
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'An error occurred', 'error');
        throw error;
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // Add notification to the page
    const container = document.querySelector('.notification-container') || createNotificationContainer();
    container.appendChild(notification);

    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.className = 'notification-container';
    document.body.appendChild(container);
    return container;
}

// Animation functions
function initializeAnimations() {
    const features = document.querySelectorAll('.feature-card');
    features.forEach((feature, index) => {
        feature.style.animationDelay = `${index * 0.2}s`;
    });
}

// Filter functionality
function filterDisasters() {
    const typeFilter = document.getElementById('disasterType').value;
    const severityFilter = document.getElementById('disasterSeverity').value;
    
    document.querySelectorAll('.disaster-card').forEach(card => {
        const type = card.getAttribute('data-type');
        const severity = card.getAttribute('data-severity');
        
        const typeMatch = !typeFilter || type === typeFilter;
        const severityMatch = !severityFilter || severity === severityFilter;
        
        card.style.display = typeMatch && severityMatch ? '' : 'none';
    });
}

// Add these event listeners when the document loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize filters if they exist
    const typeFilter = document.getElementById('disasterType');
    const severityFilter = document.getElementById('disasterSeverity');
    
    if (typeFilter) {
        typeFilter.addEventListener('change', filterDisasters);
    }
    if (severityFilter) {
        severityFilter.addEventListener('change', filterDisasters);
    }
}); 