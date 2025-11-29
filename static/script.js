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
    
    // Update button states
    btnLeft.disabled = sliderIndex === 0;
    btnRight.disabled = sliderIndex >= maxIndex;
  }

  if (btnLeft && btnRight && slider) {
    btnLeft.addEventListener('click', () => {
      if (sliderIndex > 0) {
        sliderIndex--;
        updateSlider();
      }
    });
    
    btnRight.addEventListener('click', () => {
      const maxIndex = Math.max(0, slider.children.length - cardsPerView());
      if (sliderIndex < maxIndex) {
        sliderIndex++;
        updateSlider();
      }
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
    
    // Update button states
    if (btnLeft && btnRight) {
      btnLeft.disabled = sliderIndex === 0;
      btnRight.disabled = sliderIndex >= maxIndex;
    }
  }

  if (btnLeft && btnRight && slider) {
    btnLeft.addEventListener('click', () => {
      if (sliderIndex > 0) {
        sliderIndex--;
        updateSlider();
      }
    });
    
    btnRight.addEventListener('click', () => {
      const maxIndex = Math.max(0, slider.children.length - cardsPerView());
      if (sliderIndex < maxIndex) {
        sliderIndex++;
        updateSlider();
      }
    });
    
    window.addEventListener('resize', updateSlider);
    updateSlider();
  }
});

// --- Mobile Navigation Toggle ---
document.addEventListener('DOMContentLoaded', function() {
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');
  
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      const isVisible = navLinks.style.display === 'flex';
      navLinks.style.display = isVisible ? 'none' : 'flex';
      
      // Update aria label for accessibility
      hamburger.setAttribute('aria-label', isVisible ? 'Open menu' : 'Close menu');
    });

    // Close mobile menu when clicking on a link
    navLinks.addEventListener('click', (e) => {
      if (e.target.tagName === 'A' && window.innerWidth <= 900) {
        navLinks.style.display = 'none';
        hamburger.setAttribute('aria-label', 'Open menu');
      }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) {
        navLinks.style.display = 'flex';
      } else {
        navLinks.style.display = 'none';
      }
    });
  }
});
// Profile Dropdown Toggle
// LOGIN DROPDOWN
document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("profileBtn");
    const dropdown = document.getElementById("profileDropdown");

    btn.addEventListener("click", function (e) {
        e.stopPropagation();
        dropdown.classList.toggle("show");
    });

    // Close dropdown on outside click
    document.addEventListener("click", function () {
        dropdown.classList.remove("show");
    });

});



// --- Modal Logic for Service Requests ---
document.addEventListener('DOMContentLoaded', function() {
  const modalBackdrop = document.getElementById('modalBackdrop');
  const serviceButtons = document.querySelectorAll('.service-card button, #requestBtn');
  const modalClose = document.getElementById('modalClose');
  const modalCancel = document.getElementById('modalCancel');
  const serviceField = document.getElementById('serviceField');
  const serviceForm = document.getElementById('serviceForm');

  // Check if modal elements exist
  if (!modalBackdrop || !serviceForm) {
    console.log("Modal elements not found - service request modal disabled");
    return;
  }

  function openModal(serviceName = '') {
    if (serviceField) {
      serviceField.value = serviceName;
    }
    modalBackdrop.style.display = 'flex';
    modalBackdrop.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
  }

  function closeModal() {
    modalBackdrop.style.display = 'none';
    modalBackdrop.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = ''; // Restore scrolling
    if (serviceForm) {
      serviceForm.reset();
    }
  }

  // Attach event listeners to service buttons
  serviceButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const service = e.currentTarget.getAttribute('data-service') || 'General Service';
      openModal(service);
    });
  });

  // Modal close handlers
  if (modalClose) {
    modalClose.addEventListener('click', closeModal);
  }
  
  if (modalCancel) {
    modalCancel.addEventListener('click', closeModal);
  }

  // Close modal when clicking backdrop
  modalBackdrop.addEventListener('click', (e) => { 
    if (e.target === modalBackdrop) closeModal(); 
  });

  // Handle form submission
  if (serviceForm) {
    serviceForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      // Basic form validation
      const requiredFields = serviceForm.querySelectorAll('[required]');
      let isValid = true;
      
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          field.style.borderColor = '#ff4444';
        } else {
          field.style.borderColor = '';
        }
      });
      
      if (!isValid) {
        alert('Please fill in all required fields.');
        return;
      }

      // Prepare form data
      const formData = new FormData(serviceForm);
      const payload = {
        service: formData.get('service') || 'General Service',
        name: formData.get('name'),
        flat: formData.get('flat'),
        phone: formData.get('phone'),
        datetime: formData.get('datetime'),
        details: formData.get('details')
      };

      // Simulate form submission (replace with actual API call)
      console.log('Service request submitted:', payload);
      
      // Show success message
      alert(`Service request submitted successfully!\n\nService: ${payload.service}\nName: ${payload.name}\nWe will contact you shortly.`);
      
      // Close modal and reset form
      closeModal();
      
      // Here you would typically send the data to your server:
      // fetch('/api/service-request', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(payload)
      // })
      // .then(response => response.json())
      // .then(data => {
      //   alert('Request submitted successfully!');
      //   closeModal();
      // })
      // .catch(error => {
      //   console.error('Error:', error);
      //   alert('Error submitting request. Please try again.');
      // });
    });
  }

  // Accessibility: close modal with Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalBackdrop.style.display === 'flex') {
      closeModal();
    }
  });
});

// --- Smooth Scrolling for Anchor Links ---
document.addEventListener('DOMContentLoaded', function() {
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  
  anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      
      // Only process internal anchor links, not external URLs
      if (href === '#' || href.startsWith('#!')) return;
      
      const targetId = href.substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        e.preventDefault();
        
        // Calculate offset for fixed header
        const headerHeight = document.querySelector('.topbar')?.offsetHeight || 0;
        const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
        
        // Update URL without jumping
        history.pushState(null, null, href);
      }
    });
  });
});

// --- Form Validation Helper ---
document.addEventListener('DOMContentLoaded', function() {
  // Add basic validation to all forms
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      const requiredFields = this.querySelectorAll('[required]');
      let isValid = true;
      
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          // Add visual feedback
          field.style.borderColor = '#ff4444';
          
          // Remove error style when user starts typing
          field.addEventListener('input', function() {
            if (this.value.trim()) {
              this.style.borderColor = '';
            }
          });
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        alert('Please fill in all required fields.');
      }
    });
  });
});

// --- Image Loading Error Handler ---
document.addEventListener('DOMContentLoaded', function() {
  const images = document.querySelectorAll('img');
  
  images.forEach(img => {
    img.addEventListener('error', function() {
      console.warn('Image failed to load:', this.src);
      // Optionally set a placeholder image
      // this.src = '/static/images/placeholder.jpg';
    });
  });
});

// --- Initialize All Functionality ---
document.addEventListener('DOMContentLoaded', function() {
  console.log('ResiReach - Community Portal initialized');
  
  // Set current year in footer if needed
  const yearElement = document.querySelector('footer .current-year');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }
});

// --- Responsive Helpers ---
function isMobile() {
  return window.innerWidth <= 768;
}

function isTablet() {
  return window.innerWidth > 768 && window.innerWidth <= 1024;
}

function isDesktop() {
  return window.innerWidth > 1024;
}

// Export functions for potential use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { isMobile, isTablet, isDesktop };
}

