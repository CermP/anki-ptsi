/**
 * main.js
 * Handles search functionality and interactions for the Anki-PTSI website.
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const deckCards = document.querySelectorAll('.deck-card');
    const subjectSections = document.querySelectorAll('.subject-section');
    const noResultsMessage = document.getElementById('no-results');

    // Focus search on slash key press
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement !== searchInput) {
            e.preventDefault();
            searchInput.focus();
        }
    });

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            filterDecks(query);
        });
    }

    function filterDecks(query) {
        let visibleCount = 0;

        // resets if query is empty
        if (!query) {
            deckCards.forEach(card => card.classList.remove('hidden'));
            subjectSections.forEach(section => section.classList.remove('hidden'));
            if (noResultsMessage) noResultsMessage.style.display = 'none';
            return;
        }

        subjectSections.forEach(section => {
            const sectionCards = section.querySelectorAll('.deck-card');
            let hasVisibleCards = false;

            sectionCards.forEach(card => {
                const title = card.querySelector('.deck-name').textContent.toLowerCase();
                // We can also search in subject if we want, but for now strict card matching
                // const subject = section.querySelector('.subject-title').textContent.toLowerCase();
                
                if (title.includes(query)) {
                    card.classList.remove('hidden');
                    hasVisibleCards = true;
                    visibleCount++;
                } else {
                    card.classList.add('hidden');
                }
            });

            // Hide the entire subject section if no cards match
            if (hasVisibleCards) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        });

        // Show "No results" message
        if (noResultsMessage) {
            noResultsMessage.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }
});
