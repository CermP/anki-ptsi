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
            const query = e.target.value.trim();
            filterDecks(query);
        });
    }

    // Utility function to remove accents and convert to lowercase
    function normalizeText(text) {
        return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
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

        const normalizedQuery = normalizeText(query);
        const queryTokens = normalizedQuery.split(/\s+/).filter(token => token.length > 0);

        subjectSections.forEach(section => {
            const sectionCards = section.querySelectorAll('.deck-card');
            let hasVisibleCards = false;

            const subject = normalizeText(section.querySelector('.subject-title').textContent);

            sectionCards.forEach(card => {
                const title = normalizeText(card.querySelector('.deck-name').textContent);
                const searchableContent = subject + " " + title;

                // Check if ALL words/tokens from the query are found in the content (AND logic)
                const isMatch = queryTokens.every(token => searchableContent.includes(token));

                if (isMatch) {
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
