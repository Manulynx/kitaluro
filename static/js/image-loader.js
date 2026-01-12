/**
 * Optimized Image Loader for Product Images
 * Handles progressive loading, lazy loading, and quality optimization
 */

document.addEventListener('DOMContentLoaded', function() {
  initializeImageLoading();
});

function initializeImageLoading() {
  const imageWrappers = document.querySelectorAll('.product-image-wrapper');
  
  imageWrappers.forEach(wrapper => {
    const img = wrapper.querySelector('.product-image');
    
    if (img) {
      // Add loading class
      wrapper.classList.add('loading');
      
      // Create a new image to preload
      const preloadImg = new Image();
      
      preloadImg.onload = function() {
        // Image loaded successfully
        img.src = preloadImg.src;
        img.classList.add('loaded');
        wrapper.classList.remove('loading');
        wrapper.classList.add('image-loaded');
        
        // Add quality badge
        addQualityBadge(wrapper);
      };
      
      preloadImg.onerror = function() {
        // Handle error
        wrapper.classList.remove('loading');
        wrapper.classList.add('error-loading');
        console.error('Error loading image:', img.dataset.src || img.src);
      };
      
      // Start loading
      preloadImg.src = img.dataset.src || img.src;
      
      // Set up lazy loading for images not in viewport
      setupLazyLoading(img, wrapper);
    }
  });
}

function setupLazyLoading(img, wrapper) {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const lazyImage = entry.target;
          if (lazyImage.dataset.src) {
            lazyImage.src = lazyImage.dataset.src;
            lazyImage.classList.add('loaded');
            wrapper.classList.remove('loading');
            wrapper.classList.add('image-loaded');
          }
          imageObserver.unobserve(lazyImage);
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.01
    });
    
    imageObserver.observe(img);
  }
}

function addQualityBadge(wrapper) {
  if (!wrapper.querySelector('.product-image-quality-badge')) {
    const badge = document.createElement('span');
    badge.className = 'product-image-quality-badge';
    badge.textContent = 'HD';
    wrapper.appendChild(badge);
  }
}

// Export for use in other scripts
window.ImageLoader = {
  initialize: initializeImageLoading,
  setupLazy: setupLazyLoading
};