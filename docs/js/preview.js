/**
 * preview.js
 * Handles deck preview modal and link copying logic.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ---- COPY LINK LOGIC ----
    const copyBtns = document.querySelectorAll('.copy-link-btn');
    const toast = document.getElementById('toast-notification');

    function showToast() {
        if (!toast) return;
        toast.classList.remove('hidden');
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.classList.add('hidden'), 300); // Wait for transition
        }, 2000);
    }

    copyBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const deckId = btn.getAttribute('data-deck-id');
            const url = new URL(window.location.href);
            url.hash = deckId;

            navigator.clipboard.writeText(url.toString()).then(() => {
                showToast();
            }).catch(err => {
                console.error("Failed to copy URL: ", err);
            });
        });
    });

    // ---- PREVIEW LOGIC ----
    const previewBtns = document.querySelectorAll('.preview-btn');
    const modal = document.getElementById('preview-modal');
    const closeBtn = document.getElementById('close-modal');

    const flashcard = document.getElementById('flashcard');
    const flashcardFront = document.getElementById('flashcard-front');
    const flashcardBack = document.getElementById('flashcard-back');
    const flipBtn = document.getElementById('flip-card');

    const prevBtn = document.getElementById('prev-card');
    const nextBtn = document.getElementById('next-card');

    const titleEl = document.getElementById('modal-deck-title');
    const currentIdxEl = document.getElementById('current-card-idx');
    const totalCardsEl = document.getElementById('total-cards-count');

    let currentCards = [];
    let currentIndex = 0;
    let isFlipped = false;

    function openModal() {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    function closeModal() {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
        currentCards = [];
        resetCard();
    }

    function resetCard() {
        isFlipped = false;
        flashcard.classList.remove('flipped');
        // Small delay to allow flip animation to start before content changes
        setTimeout(() => {
            flashcardFront.scrollTop = 0;
            flashcardBack.scrollTop = 0;
        }, 150);
    }

    function updateCardDisplay() {
        if (currentCards.length === 0) return;

        const card = currentCards[currentIndex];
        flashcardFront.innerHTML = card.front;
        flashcardBack.innerHTML = card.back;

        currentIdxEl.textContent = currentIndex + 1;
        totalCardsEl.textContent = currentCards.length;

        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex === currentCards.length - 1;
    }

    previewBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const previewUrl = btn.getAttribute('data-preview-url');
            const deckTitle = btn.getAttribute('data-deck-title');

            titleEl.textContent = "Chargement...";
            flashcardFront.innerHTML = "<div class='loading'>Chargement des cartes...</div>";
            flashcardBack.innerHTML = "";
            currentIdxEl.textContent = "--";
            totalCardsEl.textContent = "--";
            prevBtn.disabled = true;
            nextBtn.disabled = true;
            resetCard();

            openModal();

            try {
                const response = await fetch(previewUrl);
                if (!response.ok) throw new Error("Preview not found");

                const cards = await response.json();

                if (cards && cards.length > 0) {
                    currentCards = cards;
                    currentIndex = 0;
                    titleEl.textContent = deckTitle;
                    updateCardDisplay();
                } else {
                    titleEl.textContent = "Deck invalide";
                    flashcardFront.innerHTML = "Aucune carte trouvée pour ce deck.";
                }
            } catch (err) {
                console.error(err);
                titleEl.textContent = "Erreur";
                flashcardFront.innerHTML = "Impossible de charger l'aperçu du deck.<br>Ce deck n'a peut-être pas encore été régénéré.";
            }
        });
    });

    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal(); // direct click on overlay
    });

    document.addEventListener('keydown', (e) => {
        if (modal.classList.contains('hidden')) return;

        if (e.key === 'Escape') closeModal();
        else if (e.key === 'ArrowRight') {
            if (!nextBtn.disabled) { currentIndex++; resetCard(); setTimeout(updateCardDisplay, 150); }
        }
        else if (e.key === 'ArrowLeft') {
            if (!prevBtn.disabled) { currentIndex--; resetCard(); setTimeout(updateCardDisplay, 150); }
        }
        else if (e.key === ' ' || e.key === 'Enter') {
            e.preventDefault();
            toggleFlip();
        }
    });

    function toggleFlip() {
        isFlipped = !isFlipped;
        flashcard.classList.toggle('flipped', isFlipped);
    }

    flipBtn.addEventListener('click', toggleFlip);
    flashcard.addEventListener('click', toggleFlip);

    nextBtn.addEventListener('click', () => {
        currentIndex++;
        resetCard();
        setTimeout(updateCardDisplay, 150);
    });

    prevBtn.addEventListener('click', () => {
        currentIndex--;
        resetCard();
        setTimeout(updateCardDisplay, 150);
    });
});
