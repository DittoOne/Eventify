document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                setTimeout(function() {
                    alert.remove();
                }, 150);
            }
        }, 5000);
    });
});
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchForm = document.querySelector('form[action*="search"]');
    const searchInput = document.querySelector('input[name="q"]');
    
    // Auto-focus search input
    if (searchInput) {
        searchInput.focus();
    }
    
    // Search on Enter key
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchForm.submit();
            }
        });
    }
    
    clearBtn.addEventListener('click', function() {
        searchInput.value = '';
        document.querySelector('select[name="category"]').value = 'all';
        document.querySelector('input[name="start_date"]').value = '';
        document.querySelector('input[name="end_date"]').value = '';
        searchForm.submit();
    });
    
    // Event card hover effects
    const eventItems = document.querySelectorAll('.event-item');
    eventItems.forEach(function(item) {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });
    });
    
    //Form validation for date filters
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', function() {
            if (this.value && endDateInput.value && this.value > endDateInput.value) {
                alert('Start date cannot be after end date');
                this.value = '';
            }
        });
        
        endDateInput.addEventListener('change', function() {
            if (this.value && startDateInput.value && this.value < startDateInput.value) {
                alert('End date cannot be before start date');
                this.value = '';
            }
        });
    }
    
    // Loading animation for search
    if (searchForm) {
        searchForm.addEventListener('submit', function() {
            const submitBtn = searchForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
            
            // Reset after 3 seconds if form doesn't submit
            setTimeout(function() {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }, 3000);
        });
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape' && document.activeElement === searchInput) {
            searchInput.blur();
        }
    });
    
    // URL parameter handling for better UX
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('q') || urlParams.get('category') !== 'all' || urlParams.get('start_date') || urlParams.get('end_date')) {
        // Show that filters are active
        const filterBtn = document.querySelector('button[type="submit"]:contains("Apply Filters")');
        if (filterBtn) {
            filterBtn.classList.add('btn-primary');
            filterBtn.classList.remove('btn-outline-primary');
        }
    }
});