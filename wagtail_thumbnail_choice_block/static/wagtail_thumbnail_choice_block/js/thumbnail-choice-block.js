/**
 * Thumbnail Choice Block JavaScript
 *
 * Handles interaction, selection state, and filtering for thumbnail radio buttons
 */

(function() {
    'use strict';

    function initThumbnailChoiceBlocks() {
        // Find all thumbnail radio selects
        const containers = document.querySelectorAll('.thumbnail-radio-select');

        containers.forEach(container => {
            // Skip if already initialized
            if (container.dataset.initialized) return;
            container.dataset.initialized = 'true';

            // Get all radio options in this container
            const options = container.querySelectorAll('.thumbnail-radio-option');
            const filterInput = container.querySelector('.thumbnail-filter-input');
            const dropdown = container.querySelector('.thumbnail-dropdown');
            const noResultsMessage = container.querySelector('.thumbnail-no-results');
            const thumbnailPreview = container.querySelector('.thumbnail-selected-preview');

            // Function to update the input display with selected option
            function updateInputDisplay() {
                const selectedOption = container.querySelector('.thumbnail-radio-option.selected');
                if (selectedOption && filterInput) {
                    const label = selectedOption.querySelector('.thumbnail-label');
                    filterInput.value = label ? label.textContent : '';

                    // Update thumbnail preview
                    if (thumbnailPreview) {
                        const thumbnailWrapper = selectedOption.querySelector('.thumbnail-wrapper');
                        if (thumbnailWrapper) {
                            // Clone the thumbnail content
                            thumbnailPreview.innerHTML = thumbnailWrapper.innerHTML;
                            thumbnailPreview.classList.add('visible');
                            filterInput.classList.add('has-thumbnail');
                        } else {
                            thumbnailPreview.innerHTML = '';
                            thumbnailPreview.classList.remove('visible');
                            filterInput.classList.remove('has-thumbnail');
                        }
                    }
                } else {
                    // No selection, clear thumbnail
                    if (thumbnailPreview) {
                        thumbnailPreview.innerHTML = '';
                        thumbnailPreview.classList.remove('visible');
                    }
                    if (filterInput) {
                        filterInput.classList.remove('has-thumbnail');
                    }
                }
            }

            // Function to toggle dropdown visibility
            function toggleDropdown() {
                if (dropdown) {
                    dropdown.classList.toggle('show');
                    container.classList.toggle('open');
                    // If opening dropdown, focus on filtering (allow typing)
                    if (dropdown.classList.contains('show')) {
                        filterInput.removeAttribute('readonly');
                        filterInput.select();
                    }
                }
            }

            // Function to close dropdown
            function closeDropdown() {
                if (dropdown) {
                    dropdown.classList.remove('show');
                    container.classList.remove('open');
                    filterInput.setAttribute('readonly', 'readonly');

                    // Clear the filter query and reset all options to visible
                    if (filterInput) {
                        filterInput.value = '';
                    }
                    options.forEach(option => {
                        option.style.display = '';
                    });
                    if (noResultsMessage) {
                        noResultsMessage.style.display = 'none';
                    }

                    // Update display to show selected value
                    updateInputDisplay();
                }
            }

            // Handle click on input to toggle dropdown
            if (filterInput) {
                filterInput.addEventListener('click', function(e) {
                    e.stopPropagation();
                    toggleDropdown();
                });

                // Handle filtering when typing
                filterInput.addEventListener('input', function(e) {
                    const filterValue = e.target.value.toLowerCase().trim();
                    let visibleCount = 0;

                    options.forEach(option => {
                        const label = option.dataset.label || '';

                        if (filterValue === '' || label.includes(filterValue)) {
                            option.style.display = '';
                            visibleCount++;
                        } else {
                            option.style.display = 'none';
                        }
                    });

                    // Show/hide "no results" message
                    if (noResultsMessage) {
                        if (visibleCount === 0 && filterValue !== '') {
                            noResultsMessage.style.display = 'block';
                        } else {
                            noResultsMessage.style.display = 'none';
                        }
                    }
                });
            }

            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!container.contains(e.target)) {
                    closeDropdown();
                }
            });

            // Initialize selection behavior for each option
            options.forEach(option => {
                const input = option.querySelector('input[type="radio"]');

                if (!input) return;

                // Handle click on the label
                option.addEventListener('click', function(e) {
                    // Update selected state on all options in this group
                    options.forEach(opt => opt.classList.remove('selected'));
                    option.classList.add('selected');

                    // Close dropdown and update input display
                    closeDropdown();
                });

                // Handle keyboard navigation
                input.addEventListener('change', function() {
                    options.forEach(opt => opt.classList.remove('selected'));
                    option.classList.add('selected');
                    updateInputDisplay();
                });

                // Set initial state
                if (input.checked) {
                    option.classList.add('selected');
                }
            });

            // Initialize the input display with the selected value
            updateInputDisplay();
        });
    }

    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThumbnailChoiceBlocks);
    } else {
        initThumbnailChoiceBlocks();
    }

    // Re-initialize when Wagtail adds new blocks dynamically
    document.addEventListener('wagtail:block-added', function() {
        initThumbnailChoiceBlocks();
    });
})();
