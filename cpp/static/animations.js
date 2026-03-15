// Smooth scroll animations - fade-in slide-up scale
// Beginner-friendly IntersectionObserver

document.addEventListener('DOMContentLoaded', () => {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-fade-slide');
        observer.unobserve(entry.target); // one-time anim
      }
    });
  }, observerOptions);

  // Observe all animate elements
  document.querySelectorAll('.animate-hero, .animate-card, .animate-section').forEach(el => {
    observer.observe(el);
  });
});

