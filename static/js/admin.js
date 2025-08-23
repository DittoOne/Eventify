document.addEventListener('DOMContentLoaded', function() {
    // Set minimum date to today for event creation/editing
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(function(input) {
        input.setAttribute('min', today);
    });
    
    // Form validation
    const eventForms = document.querySelectorAll('form');
    eventForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const dateInput = form.querySelector('input[name="date"]');
            const timeInput = form.querySelector('input[name="time"]');
            const capacityInput = form.querySelector('input[name="max_capacity"]');
            
            if (dateInput && timeInput) {
                const eventDate = new Date(dateInput.value + 'T' + timeInput.value);
                const now = new Date();
                
                if (eventDate <= now) {
                    e.preventDefault();
                    alert('Event date and time must be in the future.');
                    return;
                }
            }
            
            if (capacityInput && parseInt(capacityInput.value) < 1) {
                e.preventDefault();
                alert('Maximum capacity must be at least 1.');
                return;
            }
        });
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('button[type="submit"][class*="btn-danger"]');
    deleteButtons.forEach(function(button) {
        button.closest('form').addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-refresh dashboard stats every 30 seconds
    if (window.location.pathname.includes('/admin/dashboard')) {
        setInterval(function() {
            // You can implement AJAX refresh here if needed
            console.log('Dashboard stats could be refreshed here');
        }, 30000);
    }
});
                           


