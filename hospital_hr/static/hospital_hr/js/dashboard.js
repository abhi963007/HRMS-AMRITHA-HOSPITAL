/**
 * Amrita Hospital HRMS - Dashboard JavaScript
 * Enterprise-grade UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    initSidebarToggle();
    
    // Table Search
    initTableSearch();
    
    // Auto-dismiss alerts
    initAlertDismiss();
    
    // Smooth scroll for navigation
    initSmoothScroll();
    
    // Landing page scroll effect
    initLandingNavScroll();
    
    // Form validation enhancement
    initFormValidation();
    
    // Animate metric cards on scroll
    initMetricAnimation();
    
    // Modal form handling
    initModalForms();
    
    // Delete confirmation modals
    initDeleteModals();
});

/**
 * Sidebar Toggle for Mobile
 */
function initSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 992) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }
}

/**
 * Table Search Functionality
 */
function initTableSearch() {
    const searchInputs = document.querySelectorAll('.table-search');
    
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableId = this.getAttribute('data-table');
            const table = document.getElementById(tableId);
            
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
                
                // Show empty state if no results
                const visibleRows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
                const emptyState = table.parentElement.querySelector('.empty-search-state');
                
                if (visibleRows.length === 0 && emptyState) {
                    emptyState.style.display = 'block';
                } else if (emptyState) {
                    emptyState.style.display = 'none';
                }
            }
        });
    });
}

/**
 * Auto-dismiss Alerts
 */
function initAlertDismiss() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Smooth Scroll
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

/**
 * Landing Page Navigation Scroll Effect
 */
function initLandingNavScroll() {
    const landingNav = document.querySelector('.landing-nav');
    
    if (landingNav) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                landingNav.classList.add('scrolled');
            } else {
                landingNav.classList.remove('scrolled');
            }
        });
    }
}

/**
 * Form Validation Enhancement
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Focus first invalid field
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
        });
        
        // Remove invalid class on input
        form.querySelectorAll('input, select, textarea').forEach(function(field) {
            field.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        });
    });
}

/**
 * Animate Metric Cards
 */
function initMetricAnimation() {
    const metricCards = document.querySelectorAll('.metric-card');
    
    if (metricCards.length > 0 && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    
                    // Animate counter
                    const valueEl = entry.target.querySelector('.metric-value');
                    if (valueEl) {
                        animateCounter(valueEl);
                    }
                    
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        metricCards.forEach(function(card) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.5s ease';
            observer.observe(card);
        });
    }
}

/**
 * Counter Animation
 */
function animateCounter(element) {
    const target = parseInt(element.textContent, 10);
    if (isNaN(target)) return;
    
    const duration = 1000;
    const step = target / (duration / 16);
    let current = 0;
    
    const timer = setInterval(function() {
        current += step;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

/**
 * Confirm Delete
 */
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

/**
 * Format Date
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-IN', options);
}

/**
 * Format Currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function() {
        showToast('Failed to copy', 'error');
    });
}

/**
 * Show Toast Notification
 */
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type || 'info'}`;
    toast.innerHTML = `
        <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : type === 'error' ? 'bi-exclamation-circle-fill' : 'bi-info-circle-fill'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(function() {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(function() {
        toast.classList.remove('show');
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, 3000);
}

/**
 * Debounce Function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Print Page
 */
function printPage() {
    window.print();
}

/**
 * Export Table to CSV
 */
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        
        cols.forEach(function(col) {
            rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    link.href = URL.createObjectURL(blob);
    link.download = filename || 'export.csv';
    link.click();
}

/**
 * Modal Form Handling
 * Opens forms in Bootstrap modals via AJAX
 */
function initModalForms() {
    document.addEventListener('click', function(e) {
        const trigger = e.target.closest('[data-modal-url]');
        if (!trigger) return;
        
        e.preventDefault();
        
        const url = trigger.getAttribute('data-modal-url');
        const title = trigger.getAttribute('data-modal-title') || 'Form';
        const size = trigger.getAttribute('data-modal-size') || 'lg';
        
        openFormModal(url, title, size);
    });
}

/**
 * Open Form in Modal
 */
function openFormModal(url, title, size) {
    const modal = document.getElementById('globalModal');
    const modalDialog = modal.querySelector('.modal-dialog');
    const modalTitle = document.getElementById('globalModalLabel');
    const modalBody = document.getElementById('globalModalBody');
    
    // Set modal size
    modalDialog.className = 'modal-dialog modal-dialog-centered modal-dialog-scrollable';
    if (size === 'xl') {
        modalDialog.classList.add('modal-xl');
    } else if (size === 'lg') {
        modalDialog.classList.add('modal-lg');
    } else if (size === 'sm') {
        modalDialog.classList.add('modal-sm');
    }
    
    // Set title and show loading
    modalTitle.textContent = title;
    modalBody.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading form...</p>
        </div>
    `;
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Fetch form content
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Extract form content from response
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Try to find the form card or form content - prioritize .form-card
        let formContent = doc.querySelector('.form-card') || 
                          doc.querySelector('form') ||
                          doc.querySelector('.card-body') ||
                          doc.querySelector('.modal-body');
        
        if (formContent) {
            // If we found .form-card, extract just the card-body
            if (formContent.classList.contains('form-card')) {
                const cardBody = formContent.querySelector('.card-body');
                if (cardBody) {
                    modalBody.innerHTML = cardBody.innerHTML;
                } else {
                    modalBody.innerHTML = formContent.innerHTML;
                }
            } else {
                modalBody.innerHTML = formContent.innerHTML;
            }
            
            // Ensure form has proper styling
            const form = modalBody.querySelector('form');
            if (form) {
                // Add modal form submission handler
                form.addEventListener('submit', handleModalFormSubmit);
                
                // Add form-control class to inputs if missing
                form.querySelectorAll('input, select, textarea').forEach(el => {
                    if (!el.classList.contains('form-control') && 
                        !el.classList.contains('form-select') &&
                        !el.classList.contains('form-check-input') &&
                        el.type !== 'hidden' &&
                        el.type !== 'submit') {
                        if (el.tagName === 'SELECT') {
                            el.classList.add('form-select');
                        } else if (el.type === 'checkbox' || el.type === 'radio') {
                            el.classList.add('form-check-input');
                        } else {
                            el.classList.add('form-control');
                        }
                    }
                });
            }
        } else {
            modalBody.innerHTML = '<div class="alert alert-danger">Failed to load form content.</div>';
        }
    })
    .catch(error => {
        console.error('Error loading form:', error);
        modalBody.innerHTML = '<div class="alert alert-danger">Failed to load form. Please try again.</div>';
    });
}

/**
 * Handle Modal Form Submission
 */
function handleModalFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('[type="submit"]');
    const originalBtnText = submitBtn ? submitBtn.innerHTML : '';
    
    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
    }
    
    fetch(form.action || window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        // Check if response is JSON (success response from server)
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                if (data.success) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('globalModal'));
                    if (modal) modal.hide();
                    showToast(data.message || 'Saved successfully!', 'success');
                    setTimeout(() => window.location.reload(), 500);
                    return null;
                }
                return { json: data };
            });
        }
        
        // Otherwise parse as HTML
        return response.text().then(html => ({ html: html }));
    })
    .then(result => {
        if (!result) return;
        
        // Handle JSON response
        if (result.json) {
            showToast('Error: ' + (result.json.message || 'Form submission failed'), 'error');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
            return;
        }
        
        // Handle HTML response
        const html = result.html;
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Form has validation errors - update the modal with the new form
        const modalBody = document.getElementById('globalModalBody');
        
        // Try to find the form content in order of specificity
        let formContent = doc.querySelector('.form-card');
        
        if (formContent) {
            // Extract the card-body from form-card
            const cardBody = formContent.querySelector('.card-body');
            if (cardBody) {
                modalBody.innerHTML = cardBody.innerHTML;
            } else {
                modalBody.innerHTML = formContent.innerHTML;
            }
            const newForm = modalBody.querySelector('form');
            if (newForm) {
                newForm.addEventListener('submit', handleModalFormSubmit);
                
                // Re-apply form control classes
                newForm.querySelectorAll('input, select, textarea').forEach(el => {
                    if (!el.classList.contains('form-control') && 
                        !el.classList.contains('form-select') &&
                        !el.classList.contains('form-check-input') &&
                        el.type !== 'hidden' &&
                        el.type !== 'submit') {
                        if (el.tagName === 'SELECT') {
                            el.classList.add('form-select');
                        } else if (el.type === 'checkbox' || el.type === 'radio') {
                            el.classList.add('form-check-input');
                        } else {
                            el.classList.add('form-control');
                        }
                    }
                });
            }
            
            // Show error message if there are form errors
            const errorFields = modalBody.querySelectorAll('.is-invalid, .text-danger, .errorlist');
            if (errorFields.length > 0) {
                showToast('Please fix the errors in the form', 'error');
            }
            
            // Reset button state for the new form
            const newSubmitBtn = modalBody.querySelector('[type="submit"]');
            if (newSubmitBtn) {
                newSubmitBtn.disabled = false;
            }
        } else {
            // No form content found - might be a success redirect
            // Close modal and reload
            const modal = bootstrap.Modal.getInstance(document.getElementById('globalModal'));
            if (modal) modal.hide();
            showToast('Saved successfully!', 'success');
            setTimeout(() => window.location.reload(), 500);
        }
    })
    .catch(error => {
        console.error('Form submission error:', error);
        showToast('An error occurred. Please try again.', 'error');
        
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}

/**
 * Delete Confirmation Modal
 */
function initDeleteModals() {
    document.addEventListener('click', function(e) {
        const trigger = e.target.closest('[data-delete-url]');
        if (!trigger) return;
        
        e.preventDefault();
        
        const url = trigger.getAttribute('data-delete-url');
        const message = trigger.getAttribute('data-delete-message') || 'Are you sure you want to delete this item?';
        const itemName = trigger.getAttribute('data-delete-item') || 'this item';
        
        showDeleteConfirmation(url, message, itemName);
    });
}

/**
 * Show Delete Confirmation Modal
 */
function showDeleteConfirmation(url, message, itemName) {
    const modal = document.getElementById('deleteModal');
    const messageEl = document.getElementById('deleteModalMessage');
    const confirmBtn = document.getElementById('deleteConfirmBtn');
    
    messageEl.textContent = message;
    confirmBtn.href = url;
    
    // Handle form-based delete (POST)
    confirmBtn.onclick = function(e) {
        e.preventDefault();
        
        // Create and submit a form for POST delete
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken.value;
            form.appendChild(csrfInput);
        }
        
        document.body.appendChild(form);
        form.submit();
    };
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Quick action to open modal from dashboard
 */
function openQuickAction(url, title, size) {
    openFormModal(url, title, size || 'lg');
}
