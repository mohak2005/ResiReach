// --- Services Card Slider ---
document.addEventListener('DOMContentLoaded', function() {
  const slider = document.getElementById('servicesSlider');
  const btnLeft = document.querySelector('.slider-btn-left');
  const btnRight = document.querySelector('.slider-btn-right');
  let sliderIndex = 0;

  function cardsPerView() {
    if (window.innerWidth <= 600) return 1;
    if (window.innerWidth <= 900) return 2;
    return 3;
  }

  function updateSlider() {
    if (!slider) return;
    const cardCount = slider.children.length;
    const card = slider.children[0];
    if (!card) return;
    const gap = 18;
    const cardWidth = card.offsetWidth + gap;
    const maxIndex = Math.max(0, cardCount - cardsPerView());

    // clamp index in valid range
    sliderIndex = Math.max(0, Math.min(sliderIndex, maxIndex));
    slider.style.transform = `translateX(-${sliderIndex * cardWidth}px)`;
  }

  if (btnLeft && btnRight && slider) {
    btnLeft.addEventListener('click', () => {
      sliderIndex--;
      updateSlider();
    });
    btnRight.addEventListener('click', () => {
      sliderIndex++;
      updateSlider();
    });
    window.addEventListener('resize', updateSlider);
    updateSlider();
  }
});

// --- Events Card Slider ---
document.addEventListener('DOMContentLoaded', function() {
  const slider = document.getElementById('eventsSlider');
  const btnLeft = document.querySelector('.events-btn-left');
  const btnRight = document.querySelector('.events-btn-right');
  let sliderIndex = 0;

  function cardsPerView() {
    if (window.innerWidth <= 600) return 1;
    if (window.innerWidth <= 900) return 2;
    return 3;
  }

  function updateSlider() {
    if (!slider) return;
    const cardCount = slider.children.length;
    const card = slider.children[0];
    if (!card) return;
    const gap = 18;
    const cardWidth = card.offsetWidth + gap;
    const maxIndex = Math.max(0, cardCount - cardsPerView());
    sliderIndex = Math.max(0, Math.min(sliderIndex, maxIndex));
    slider.style.transform = `translateX(-${sliderIndex * cardWidth}px)`;
  }

  if (btnLeft && btnRight && slider) {
    btnLeft.addEventListener('click', () => {
      sliderIndex--;
      updateSlider();
    });
    btnRight.addEventListener('click', () => {
      sliderIndex++;
      updateSlider();
    });
    window.addEventListener('resize', updateSlider);
    updateSlider();
  }
});

// NAV toggle
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');
hamburger && hamburger.addEventListener('click', () => {
  if (navLinks.style.display === 'flex') navLinks.style.display = 'none';
  else navLinks.style.display = 'flex';
});

// Modal logic
const modalBackdrop = document.getElementById('modalBackdrop');
const serviceButtons = document.querySelectorAll('.service-card button, #requestBtn, #requestBtnTop');
const modalClose = document.getElementById('modalClose');
const modalCancel = document.getElementById('modalCancel');
const serviceField = document.getElementById('serviceField');
const serviceForm = document.getElementById('serviceForm');

function openModal(serviceName = '') {
  serviceField.value = serviceName;
  modalBackdrop.style.display = 'flex';
  modalBackdrop.setAttribute('aria-hidden','false');
}

function closeModal() {
  modalBackdrop.style.display = 'none';
  modalBackdrop.setAttribute('aria-hidden','true');
  serviceForm.reset();
}

serviceButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
    const s = e.currentTarget.getAttribute('data-service') || 'General Service';
    openModal(s);
  });
});

modalClose.addEventListener('click', closeModal);
modalCancel.addEventListener('click', closeModal);
modalBackdrop.addEventListener('click', (e) => { 
  if (e.target === modalBackdrop) closeModal(); 
});

// handle form submission (replace with AJAX to backend / WP endpoint)
serviceForm.addEventListener('submit', (e) => {
  e.preventDefault();
  // Minimal client validation handled by required attributes
  const payload = {
    service: document.getElementById('serviceField').value,
    name: document.getElementById('name').value,
    flat: document.getElementById('flat').value,
    phone: document.getElementById('phone').value,
    datetime: document.getElementById('datetime').value,
    details: document.getElementById('details').value
  };

  // TODO: Send 'payload' to your server endpoint (e.g., WP REST API or form handler).
  // Example (commented): 
  // fetch('/wp-json/resireach/v1/request', { method:'POST', body:JSON.stringify(payload), headers:{'Content-Type':'application/json'}})

  // Temporary confirmation:
  alert('Request submitted:\nService: ' + payload.service + '\nName: ' + payload.name);
  closeModal();
});

// Accessibility: close modal with Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (modalBackdrop.style.display === 'flex') closeModal();
  }
});


