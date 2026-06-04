document.addEventListener('DOMContentLoaded', () => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const hero = document.querySelector('.hero');
  const heroContent = document.querySelector('.hero-content');

  if (finePointer && !reduceMotion) {
    const aura = document.createElement('div');
    aura.className = 'cursor-aura';
    aura.setAttribute('aria-hidden', 'true');
    document.body.appendChild(aura);

    let auraFrame = null;
    let pointerX = window.innerWidth / 2;
    let pointerY = window.innerHeight / 2;
    let auraX = pointerX;
    let auraY = pointerY;

    const animateAura = () => {
      auraX += (pointerX - auraX) * 0.14;
      auraY += (pointerY - auraY) * 0.14;
      aura.style.transform = `translate3d(${auraX}px, ${auraY}px, 0) translate(-50%, -50%)`;
      auraFrame = requestAnimationFrame(animateAura);
    };

    window.addEventListener('pointermove', (event) => {
      pointerX = event.clientX;
      pointerY = event.clientY;
      aura.classList.add('is-visible');
    }, { passive: true });

    document.documentElement.addEventListener('pointerleave', () => {
      aura.classList.remove('is-visible');
    });

    auraFrame = requestAnimationFrame(animateAura);

    if (hero && heroContent) {
      hero.addEventListener('pointermove', (event) => {
        const rect = hero.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;

        hero.style.setProperty('--hero-bg-x', `${x * 24}px`);
        hero.style.setProperty('--hero-bg-y', `${y * 16}px`);
        heroContent.style.setProperty('--hero-rotate-x', `${y * -4}deg`);
        heroContent.style.setProperty('--hero-rotate-y', `${x * 5}deg`);
        heroContent.style.setProperty('--hero-shift-x', `${x * 10}px`);
        heroContent.style.setProperty('--hero-shift-y', `${y * 7}px`);
      }, { passive: true });

      hero.addEventListener('pointerleave', () => {
        hero.style.setProperty('--hero-bg-x', '0px');
        hero.style.setProperty('--hero-bg-y', '0px');
        heroContent.style.setProperty('--hero-rotate-x', '0deg');
        heroContent.style.setProperty('--hero-rotate-y', '0deg');
        heroContent.style.setProperty('--hero-shift-x', '0px');
        heroContent.style.setProperty('--hero-shift-y', '0px');
      });
    }

    const tiltSelector = [
      '.about-card',
      '.dna-structure-card',
      '.app-card',
      '.card',
      '.dna-image-wrapper',
      '.dna-description',
      '.fact-item',
      '.component-item',
      '.base-card',
      '.step-item',
      '.feature-item',
      '.stat-item',
      '.trait-category'
    ].join(',');

    document.querySelectorAll(tiltSelector).forEach((element) => {
      element.classList.add('interactive-3d');

      element.addEventListener('animationend', () => {
        if (element.style.animation) element.style.animation = '';
      });

      element.addEventListener('pointermove', (event) => {
        const rect = element.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width;
        const y = (event.clientY - rect.top) / rect.height;
        const strength = element.matches('.about-card, .dna-structure-card, .app-card, .card') ? 2.2 : 4.2;

        element.style.setProperty('--card-rotate-x', `${(0.5 - y) * strength}deg`);
        element.style.setProperty('--card-rotate-y', `${(x - 0.5) * strength}deg`);
        element.style.setProperty('--spotlight-x', `${x * 100}%`);
        element.style.setProperty('--spotlight-y', `${y * 100}%`);
        element.classList.add('is-tilting');
      }, { passive: true });

      element.addEventListener('pointerleave', () => {
        element.style.setProperty('--card-rotate-x', '0deg');
        element.style.setProperty('--card-rotate-y', '0deg');
        element.style.setProperty('--spotlight-x', '50%');
        element.style.setProperty('--spotlight-y', '50%');
        element.classList.remove('is-tilting');
      });
    });

    document.querySelectorAll('.btn').forEach((button) => {
      button.classList.add('magnetic-control');

      button.addEventListener('pointermove', (event) => {
        const rect = button.getBoundingClientRect();
        const x = event.clientX - (rect.left + rect.width / 2);
        const y = event.clientY - (rect.top + rect.height / 2);
        button.style.setProperty('--magnetic-x', `${x * 0.08}px`);
        button.style.setProperty('--magnetic-y', `${y * 0.12}px`);
      }, { passive: true });

      button.addEventListener('pointerleave', () => {
        button.style.setProperty('--magnetic-x', '0px');
        button.style.setProperty('--magnetic-y', '0px');
      });
    });
  }

  const revealTargets = document.querySelectorAll(
    '.about-card, .dna-structure-card, .app-card, .wrap > .card, .grid > .card'
  );

  revealTargets.forEach((element) => {
    element.style.removeProperty('opacity');
    element.style.removeProperty('animation');
  });

  window.setTimeout(() => {
    revealTargets.forEach((element) => {
      element.style.removeProperty('opacity');
      element.style.removeProperty('animation');
    });
  }, 180);

  if (!reduceMotion && 'IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting && entry.boundingClientRect.top > window.innerHeight) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -8% 0px'
    });

    revealTargets.forEach((element) => {
      element.classList.add('reveal-ready');
      revealObserver.observe(element);
    });
  } else {
    revealTargets.forEach((element) => element.classList.add('is-visible'));
  }

});
