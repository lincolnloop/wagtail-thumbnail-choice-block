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

            // Get all radio options and headings in this container
            const options = container.querySelectorAll('.thumbnail-radio-option');
            const headings = container.querySelectorAll('.thumbnail-radio-heading');
            const filterInput = container.querySelector('.thumbnail-filter-input');
            const dropdown = container.querySelector('.thumbnail-dropdown');
            const noResultsMessage = container.querySelector('.thumbnail-no-results');
            const thumbnailPreview = container.querySelector('.thumbnail-selected-preview');

            // Skip if no options found
            if (options.length === 0) {
                return;
            }

            // Read the translated placeholder from the server-rendered HTML
            const placeholder = filterInput ? filterInput.getAttribute('placeholder') : 'Select an option...';

            // Ensure no results message is hidden initially
            if (noResultsMessage) {
                noResultsMessage.style.display = 'none';
            }

            // Function to update the input display with selected option
            function updateInputDisplay(selectedOption) {
                // If no option provided, find it in the DOM
                if (!selectedOption) {
                    selectedOption = container.querySelector('.thumbnail-radio-option.selected');
                }

                if (selectedOption && filterInput) {
                    const label = selectedOption.querySelector('.thumbnail-label');
                    const input = selectedOption.querySelector('input[type="radio"]');
                    const labelText = label ? label.textContent.trim() : '';
                    const inputValue = input ? input.value : '';

                    // Check if this is a blank choice (empty value or "---" label)
                    const isBlankChoice = inputValue === '' || labelText === '---';

                    if (isBlankChoice) {
                        // For blank choice, show placeholder text
                        filterInput.value = '';
                        filterInput.setAttribute('placeholder', placeholder);
                        // Hide thumbnail for blank choice
                        if (thumbnailPreview) {
                            thumbnailPreview.innerHTML = '';
                            thumbnailPreview.classList.remove('visible');
                        }
                        if (filterInput) {
                            filterInput.classList.remove('has-thumbnail');
                        }
                    } else {
                        // For regular choice, show the label
                        filterInput.value = labelText;
                        // Clear placeholder to ensure value is visible
                        filterInput.removeAttribute('placeholder');

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
                    }
                } else {
                    // No selection, clear thumbnail and show placeholder
                    if (thumbnailPreview) {
                        thumbnailPreview.innerHTML = '';
                        thumbnailPreview.classList.remove('visible');
                    }
                    if (filterInput) {
                        filterInput.value = '';
                        filterInput.setAttribute('placeholder', placeholder);
                        filterInput.classList.remove('has-thumbnail');
                    }
                }
            }

            // Track the selection when dropdown opens
            let selectionBeforeOpen = null;

            // Function to toggle dropdown visibility
            function toggleDropdown() {
                if (dropdown) {
                    dropdown.classList.toggle('show');
                    container.classList.toggle('open');
                    // If opening dropdown, focus on filtering (allow typing)
                    if (dropdown.classList.contains('show')) {
                        // Save the current selection before opening
                        const currentSelected = container.querySelector('.thumbnail-radio-option.selected input[type="radio"]:checked');
                        selectionBeforeOpen = currentSelected ? currentSelected.value : null;

                        filterInput.removeAttribute('readonly');
                        filterInput.select();
                        // Ensure all options and headings are visible when opening
                        options.forEach(option => {
                            option.style.display = '';
                        });
                        headings.forEach(h => { h.style.display = ''; });
                        if (noResultsMessage) {
                            noResultsMessage.style.display = 'none';
                        }
                    }
                }
            }

            // Function to close dropdown
            function closeDropdown(selectedOption) {
                if (dropdown) {
                    dropdown.classList.remove('show');
                    container.classList.remove('open');
                    filterInput.setAttribute('readonly', 'readonly');

                    // Reset all options and headings to visible
                    options.forEach(option => {
                        option.style.display = '';
                    });
                    headings.forEach(h => { h.style.display = ''; });
                    if (noResultsMessage) {
                        noResultsMessage.style.display = 'none';
                    }

                    // Only update display if we have a specific selection
                    // (not when just closing due to clicking outside)
                    if (selectedOption) {
                        updateInputDisplay(selectedOption);
                    }
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

                    if (filterValue === '') {
                        // Show everything
                        options.forEach(o => { o.style.display = ''; });
                        headings.forEach(h => { h.style.display = ''; });
                        if (noResultsMessage) noResultsMessage.style.display = 'none';
                        return;
                    }

                    // 1. Determine which options match directly
                    const optionVisible = new Map();
                    options.forEach(opt => {
                        optionVisible.set(opt, (opt.dataset.label || '').includes(filterValue));
                    });

                    // 2. Walk DOM in order; a heading match reveals the heading + all descendants
                    //    until a sibling heading of equal or lesser depth.
                    const matchedHeadings = new Set();
                    const allItems = Array.from(
                        container.querySelectorAll('.thumbnail-radio-heading, .thumbnail-radio-option')
                    );
                    for (let i = 0; i < allItems.length; i++) {
                        const item = allItems[i];
                        if (item.classList.contains('thumbnail-radio-heading')) {
                            const headingDepth = parseInt(item.dataset.depth, 10);
                            if ((item.dataset.label || '').includes(filterValue)) {
                                matchedHeadings.add(item);
                                item.style.display = '';
                                for (let j = i + 1; j < allItems.length; j++) {
                                    const child = allItems[j];
                                    const childDepth = parseInt(child.dataset.depth, 10);
                                    if (child.classList.contains('thumbnail-radio-heading')
                                            && childDepth <= headingDepth) break;
                                    child.style.display = '';
                                    if (child.classList.contains('thumbnail-radio-option')) {
                                        optionVisible.set(child, true);
                                    }
                                }
                            }
                        }
                    }

                    // 3. Apply option visibility
                    options.forEach(opt => {
                        opt.style.display = optionVisible.get(opt) ? '' : 'none';
                    });

                    // 4. Show/hide headings that weren't matched directly but have visible descendants
                    headings.forEach(heading => {
                        if (matchedHeadings.has(heading)) return;
                        const depth = parseInt(heading.dataset.depth, 10);
                        const idx = allItems.indexOf(heading);
                        let anyChildVisible = false;
                        for (let j = idx + 1; j < allItems.length; j++) {
                            const child = allItems[j];
                            if (child.classList.contains('thumbnail-radio-heading')
                                    && parseInt(child.dataset.depth, 10) <= depth) break;
                            if (child.classList.contains('thumbnail-radio-option')
                                    && child.style.display !== 'none') {
                                anyChildVisible = true;
                                break;
                            }
                        }
                        heading.style.display = anyChildVisible ? '' : 'none';
                    });

                    // 5. "No results" message
                    const visibleCount = Array.from(options).filter(o => o.style.display !== 'none').length;
                    if (noResultsMessage) {
                        noResultsMessage.style.display = (visibleCount === 0) ? 'block' : 'none';
                    }
                });

                // Handle keyboard navigation
                filterInput.addEventListener('keydown', function(e) {
                    const isDropdownOpen = dropdown && dropdown.classList.contains('show');

                    // Get visible options
                    const visibleOptions = Array.from(options).filter(opt => opt.style.display !== 'none');

                    // Arrow Down/Right: Open dropdown or move to next option
                    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                        e.preventDefault();
                        if (!isDropdownOpen) {
                            toggleDropdown();
                        } else if (visibleOptions.length > 0) {
                            const currentIndex = visibleOptions.findIndex(opt => opt.classList.contains('selected'));
                            const nextIndex = currentIndex < visibleOptions.length - 1 ? currentIndex + 1 : 0;
                            const nextOption = visibleOptions[nextIndex];
                            const input = nextOption.querySelector('input[type="radio"]');
                            if (input) {
                                input.checked = true;
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        }
                    }

                    // Arrow Up/Left: Move to previous option
                    else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                        e.preventDefault();
                        if (isDropdownOpen && visibleOptions.length > 0) {
                            const currentIndex = visibleOptions.findIndex(opt => opt.classList.contains('selected'));
                            const prevIndex = currentIndex > 0 ? currentIndex - 1 : visibleOptions.length - 1;
                            const prevOption = visibleOptions[prevIndex];
                            const input = prevOption.querySelector('input[type="radio"]');
                            if (input) {
                                input.checked = true;
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        }
                    }

                    // Enter: Select current option and close dropdown
                    else if (e.key === 'Enter') {
                        e.preventDefault();
                        if (isDropdownOpen) {
                            const selectedOption = container.querySelector('.thumbnail-radio-option.selected');
                            if (selectedOption) {
                                closeDropdown(selectedOption);
                            }
                        } else {
                            toggleDropdown();
                        }
                    }

                    // Escape: Close dropdown and revert to previous selection
                    else if (e.key === 'Escape') {
                        e.preventDefault();
                        if (isDropdownOpen) {
                            // Revert to the selection before opening
                            if (selectionBeforeOpen !== null) {
                                options.forEach(option => {
                                    const input = option.querySelector('input[type="radio"]');
                                    if (input && input.value === selectionBeforeOpen) {
                                        input.checked = true;
                                        option.classList.add('selected');
                                    } else {
                                        option.classList.remove('selected');
                                    }
                                });
                            } else {
                                // No previous selection, uncheck all
                                options.forEach(option => {
                                    const input = option.querySelector('input[type="radio"]');
                                    if (input) input.checked = false;
                                    option.classList.remove('selected');
                                });
                            }
                            closeDropdown();
                            // Restore the display to show reverted selection
                            updateInputDisplay();
                        }
                    }

                    // Space: Toggle dropdown when closed, or select when open
                    else if (e.key === ' ') {
                        // Only handle space if input is readonly (not in filter mode)
                        if (filterInput.hasAttribute('readonly')) {
                            e.preventDefault();
                            if (!isDropdownOpen) {
                                toggleDropdown();
                            } else {
                                const selectedOption = container.querySelector('.thumbnail-radio-option.selected');
                                if (selectedOption) {
                                    closeDropdown(selectedOption);
                                }
                            }
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

            // Track the initially selected option
            let initiallySelectedOption = null;

            // Initialize selection behavior for each option
            options.forEach(option => {
                const input = option.querySelector('input[type="radio"]');

                if (!input) return;

                // Ensure option is visible initially
                option.style.display = '';

                // Handle click on the label
                option.addEventListener('click', function(e) {
                    // Update selected state on all options in this group
                    options.forEach(opt => opt.classList.remove('selected'));
                    option.classList.add('selected');

                    // Close dropdown and update input display with the selected option
                    closeDropdown(option);
                });

                // Handle keyboard navigation
                input.addEventListener('change', function() {
                    options.forEach(opt => opt.classList.remove('selected'));
                    option.classList.add('selected');
                    updateInputDisplay(option);
                });

                // Set initial state
                if (input.checked) {
                    option.classList.add('selected');
                    initiallySelectedOption = option;
                }
            });

            // Initialize the input display with the selected value
            if (initiallySelectedOption) {
                updateInputDisplay(initiallySelectedOption);
            }
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

    // Fallback: Initialize on first interaction with any thumbnail filter input
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('thumbnail-filter-input')) {
            const container = e.target.closest('.thumbnail-radio-select');
            if (container && !container.dataset.initialized) {
                initThumbnailChoiceBlocks();
            }
        }
    }, true);
})();
