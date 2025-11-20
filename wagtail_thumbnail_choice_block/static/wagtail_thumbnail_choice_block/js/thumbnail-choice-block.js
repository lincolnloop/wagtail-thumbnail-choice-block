/**
 * Thumbnail Choice Block JavaScript
 *
 * Handles interaction and selection state for thumbnail radio buttons
 */

(function() {
    'use strict';

    function initThumbnailChoiceBlocks() {
        // Find all thumbnail radio selects
        const containers = document.querySelectorAll('.thumbnail-radio-select');

        containers.forEach(container => {
            // Get all radio options in this container
            const options = container.querySelectorAll('.thumbnail-radio-option');

            options.forEach(option => {
                const input = option.querySelector('input[type="radio"]');

                if (!input) return;

                // Handle click on the label
                option.addEventListener('click', function(e) {
                    // Update selected state on all options in this group
                    options.forEach(opt => opt.classList.remove('selected'));
                    option.classList.add('selected');
                });

                // Handle keyboard navigation
                input.addEventListener('change', function() {
                    options.forEach(opt => opt.classList.remove('selected'));
                    option.classList.add('selected');
                });

                // Set initial state
                if (input.checked) {
                    option.classList.add('selected');
                }
            });
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
