/**
 * REVIEW SYSTEM - Interactive Star Rating and Review Management
 * Handles star selection, form validation, and dynamic interactions
 */

class ReviewSystem {
    constructor() {
        this.selectedRating = 0;
        this.hoveredRating = 0;
        this.init();
    }

    /**
     * Initialize the review system
     */
    init() {
        this.initStarRating();
        this.initFormValidation();
        this.initReviewActions();
    }

    /**
     * Initialize interactive star rating
     */
    initStarRating() {
        const starContainer = document.querySelector('.star-selection-container');
        if (!starContainer) return;

        const starIcons = starContainer.querySelectorAll('.star-icon');
        const ratingInput = document.getElementById('id_rating');
        const ratingDisplay = document.querySelector('.rating-label-display');

        starIcons.forEach((star, index) => {
            const rating = index + 1;

            // Handle click
            star.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.selectRating(rating, starIcons, ratingInput, ratingDisplay);
            });

            // Handle hover
            star.addEventListener('mouseenter', () => {
                this.hoverRating(rating, starIcons);
                this.updateRatingDisplay(rating, ratingDisplay);
            });

            // Handle hover end
            star.addEventListener('mouseleave', () => {
                this.hoverRating(this.selectedRating, starIcons);
                if (this.selectedRating > 0) {
                    this.updateRatingDisplay(this.selectedRating, ratingDisplay);
                } else {
                    ratingDisplay.classList.remove('show');
                }
            });

            // Keyboard support
            star.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectRating(rating, starIcons, ratingInput, ratingDisplay);
                    star.focus();
                }
            });
        });

        // Initialize with saved rating if exists
        if (ratingInput && ratingInput.value) {
            this.selectedRating = parseInt(ratingInput.value);
            this.updateStars(this.selectedRating, starIcons);
            this.updateRatingDisplay(this.selectedRating, ratingDisplay);
            ratingDisplay.classList.add('show');
        }
    }

    /**
     * Select a rating
     */
    selectRating(rating, starIcons, ratingInput, ratingDisplay) {
        this.selectedRating = rating;
        
        // Update input value
        if (ratingInput) {
            ratingInput.value = rating;
            // Trigger change event for form validation
            ratingInput.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Update stars
        this.updateStars(rating, starIcons);

        // Show rating display
        this.updateRatingDisplay(rating, ratingDisplay);
        ratingDisplay.classList.add('show');

        // Add visual feedback
        this.addSelectionFeedback(starIcons[rating - 1]);
    }

    /**
     * Hover effect on stars
     */
    hoverRating(rating, starIcons) {
        starIcons.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('hover');
            } else {
                star.classList.remove('hover');
            }
        });
    }

    /**
     * Update star states
     */
    updateStars(rating, starIcons) {
        starIcons.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('selected');
                star.innerHTML = '<i class="fas fa-star"></i>';
            } else {
                star.classList.remove('selected');
                star.innerHTML = '<i class="far fa-star"></i>';
            }
        });
    }

    /**
     * Update rating display label
     */
    updateRatingDisplay(rating, ratingDisplay) {
        if (!ratingDisplay) return;

        const labels = {
            1: 'Poor',
            2: 'Fair',
            3: 'Good',
            4: 'Very Good',
            5: 'Excellent'
        };

        ratingDisplay.innerHTML = `
            <span class="rating-label-badge">${labels[rating]}</span>
            <span>${rating} out of 5 stars</span>
        `;
    }

    /**
     * Add visual feedback when selecting a star
     */
    addSelectionFeedback(star) {
        // Remove any existing animation class
        star.classList.remove('pop-animation');
        
        // Trigger reflow to restart animation
        void star.offsetWidth;
        
        // Add animation class
        star.classList.add('pop-animation');
    }

    /**
     * Initialize form validation
     */
    initFormValidation() {
        const form = document.getElementById('review-form');
        if (!form) return;

        const submitBtn = form.querySelector('.review-submit-btn');
        const ratingInput = document.getElementById('id_rating');
        const titleInput = document.getElementById('review-title');
        const commentInput = document.getElementById('review-comment');

        // Real-time validation
        if (titleInput) {
            titleInput.addEventListener('blur', () => {
                this.validateField(titleInput, 'Title must be at least 5 characters');
            });
        }

        if (commentInput) {
            commentInput.addEventListener('blur', () => {
                this.validateField(commentInput, 'Review must be at least 20 characters');
            });
        }

        // Form submission
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            if (this.validateForm(ratingInput, titleInput, commentInput)) {
                // Show loading state
                this.showLoadingState(submitBtn);
                
                // Submit form
                setTimeout(() => {
                    form.submit();
                }, 500);
            }
        });

        // Disable submit button if rating not selected
        this.updateSubmitButtonState(submitBtn, ratingInput);
        ratingInput?.addEventListener('change', () => {
            this.updateSubmitButtonState(submitBtn, ratingInput);
        });
    }

    /**
     * Validate a single field
     */
    validateField(field, errorMessage) {
        const value = field.value.trim();
        const minLength = field.id === 'review-comment' ? 20 : 5;
        
        if (value.length < minLength) {
            this.showFieldError(field, errorMessage);
            return false;
        } else {
            this.clearFieldError(field);
            return true;
        }
    }

    /**
     * Validate entire form
     */
    validateForm(ratingInput, titleInput, commentInput) {
        let isValid = true;

        // Check rating
        if (!ratingInput || !ratingInput.value || parseInt(ratingInput.value) < 1) {
            this.showAlert('Please select at least one star rating', 'danger');
            isValid = false;
        }

        // Check title
        if (!this.validateField(titleInput, 'Title must be at least 5 characters')) {
            isValid = false;
        }

        // Check comment
        if (!this.validateField(commentInput, 'Review must be at least 20 characters')) {
            isValid = false;
        }

        return isValid;
    }

    /**
     * Show field error
     */
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.style.borderColor = '#ef4444';
        field.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';

        // Remove existing error message
        const existingError = field.nextElementSibling;
        if (existingError && existingError.classList.contains('form-text')) {
            existingError.remove();
        }

        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-text error';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i>${message}`;
        field.insertAdjacentElement('afterend', errorDiv);
    }

    /**
     * Clear field error
     */
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        field.style.borderColor = '';
        field.style.boxShadow = '';

        // Remove error message
        const errorDiv = field.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains('form-text')) {
            errorDiv.remove();
        }
    }

    /**
     * Update submit button state
     */
    updateSubmitButtonState(btn, ratingInput) {
        if (!btn || !ratingInput) return;

        const isValid = ratingInput.value && parseInt(ratingInput.value) >= 1;
        btn.disabled = !isValid;
    }

    /**
     * Show loading state
     */
    showLoadingState(btn) {
        if (!btn) return;
        
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        
        btn.dataset.originalHtml = originalText;
    }

    /**
     * Reset loading state
     */
    resetLoadingState(btn) {
        if (!btn || !btn.dataset.originalHtml) return;
        
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalHtml;
    }

    /**
     * Show alert message
     */
    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        
        const icons = {
            'danger': 'fa-exclamation-circle',
            'success': 'fa-check-circle',
            'info': 'fa-info-circle'
        };
        
        alertDiv.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
        `;
        
        // Insert at top of form
        const form = document.getElementById('review-form');
        if (form) {
            form.insertAdjacentElement('afterbegin', alertDiv);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                alertDiv.style.animation = 'slideOutUp 0.3s ease';
                setTimeout(() => alertDiv.remove(), 300);
            }, 5000);
        }
    }

    /**
     * Initialize review action buttons
     */
    initReviewActions() {
        // Handle helpful votes
        document.querySelectorAll('.review-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                
                if (btn.dataset.action === 'helpful') {
                    this.handleHelpfulVote(btn);
                } else if (btn.dataset.action === 'report') {
                    this.handleReportReview(btn);
                }
            });
        });
    }

    /**
     * Handle helpful vote
     */
    handleHelpfulVote(btn) {
        const reviewId = btn.dataset.reviewId;
        const voteType = btn.dataset.voteType;

        if (!reviewId) return;

        // Show loading state
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        btn.disabled = true;

        // Send request
        fetch(`/review/vote/${reviewId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: `vote_type=${voteType}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Toggle button state
                btn.classList.toggle('active');
                
                // Update count
                const countSpan = btn.querySelector('.review-helpful-count');
                if (countSpan) {
                    countSpan.textContent = `(${data.helpful_votes})`;
                }
                
                // Show feedback
                this.showAlert('Thank you for your feedback!', 'success');
            } else {
                this.showAlert('Error updating vote', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showAlert('Error updating vote', 'danger');
        })
        .finally(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
    }

    /**
     * Handle report review
     */
    handleReportReview(btn) {
        const reviewId = btn.dataset.reviewId;
        
        const reason = prompt('Please tell us why you\'re reporting this review:');
        if (!reason) return;

        // Send request
        fetch(`/review/report/${reviewId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCookie('csrftoken')
            },
            body: `reason=${encodeURIComponent(reason)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showAlert('Review reported successfully. Thank you!', 'success');
            } else {
                this.showAlert(data.error || 'Error reporting review', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showAlert('Error reporting review', 'danger');
        });
    }

    /**
     * Get CSRF token from cookies
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

/**
 * Initialize review system when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    new ReviewSystem();
});

/**
 * Handle tab switching
 */
function showTab(tabName, event) {
    if (event) {
        event.preventDefault();
    }

    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.style.display = 'none';
    });

    // Deactivate all buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.style.borderBottomColor = 'transparent';
        btn.style.color = '#666';
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.style.display = 'block';
    }

    // Activate selected button
    if (event && event.target) {
        event.target.style.borderBottomColor = '#f43f5e';
        event.target.style.color = '#f43f5e';
    }

    // Re-initialize review system if reviews tab
    if (tabName === 'reviews') {
        setTimeout(() => {
            const reviewSystem = new ReviewSystem();
            reviewSystem.initReviewActions();
        }, 100);
    }
}

/**
 * Handle image zoom/modal
 */
function openImageModal(src, alt = '') {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        cursor: pointer;
    `;

    const img = document.createElement('img');
    img.src = src;
    img.alt = alt;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    `;

    modal.appendChild(img);
    document.body.appendChild(modal);

    // Close on click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });

    // Close on Escape key
    const closeOnEscape = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', closeOnEscape);
        }
    };
    document.addEventListener('keydown', closeOnEscape);
}

/**
 * Change main product image
 */
function changeMainImage(src, event) {
    if (event) {
        event.preventDefault();
    }
    
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = src;
    }

    // Update active thumbnail
    document.querySelectorAll('.thumbnail-image').forEach(thumb => {
        thumb.style.borderColor = '#e0e0e0';
    });
    
    if (event && event.target) {
        event.target.style.borderColor = '#f43f5e';
    }
}
