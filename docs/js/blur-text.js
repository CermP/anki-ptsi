export class BlurText {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            delay: 200,
            animateBy: 'words', // 'words' or 'letters'
            direction: 'top',
            threshold: 0.1,
            rootMargin: '0px',
            animationFrom: options.animationFrom,
            animationTo: options.animationTo,
            stepDuration: 300, // ms duration per step (approx match to user's 0.35s)
            ...options
        };

        this.observer = null;
        this.init();
    }

    init() {
        if (!this.element) return;

        const text = this.element.textContent.trim();
        this.element.textContent = '';
        this.element.style.display = 'flex';
        this.element.style.flexWrap = 'wrap';

        // Prepare elements
        const segments = this.options.animateBy === 'words' ? text.split(' ') : text.split('');

        this.spans = segments.map((segment, index) => {
            const span = document.createElement('span');
            span.textContent = segment === ' ' ? '\u00A0' : segment;
            if (this.options.animateBy === 'words' && index < segments.length - 1) {
                span.textContent += '\u00A0';
            }

            span.style.display = 'inline-block';
            span.style.opacity = '0';
            span.style.filter = 'blur(10px)';
            span.style.transform = this.options.direction === 'top' ? 'translateY(-50px)' : 'translateY(50px)';
            span.style.transition = 'none'; // We'll use WAAPI
            span.style.willChange = 'transform, filter, opacity';

            this.element.appendChild(span);
            return span;
        });

        // Setup Observer
        this.observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting) {
                    this.animate();
                    this.observer.disconnect();
                }
            },
            {
                threshold: this.options.threshold,
                rootMargin: this.options.rootMargin
            }
        );

        this.observer.observe(this.element);
    }

    animate() {
        const { direction, stepDuration, delay } = this.options;

        // Define keyframes based on direction
        const fromY = direction === 'top' ? -50 : 50;
        const midY = direction === 'top' ? 5 : -5;

        const keyframes = [
            { filter: 'blur(10px)', opacity: 0, transform: `translateY(${fromY}px)` },
            { filter: 'blur(5px)', opacity: 0.5, transform: `translateY(${midY}px)`, offset: 0.4 }, // Approx step
            { filter: 'blur(0px)', opacity: 1, transform: 'translateY(0)' }
        ];

        this.spans.forEach((span, index) => {
            span.animate(keyframes, {
                duration: stepDuration * 2, // Total duration for the keyframes
                fill: 'forwards',
                delay: index * delay,
                easing: 'ease-out'
            });
        });
    }
}
