// ========================================
// SINGLE-ITEM CAROUSEL WITH CROSSFADE
// Professional Slide + Fade Transitions
// ========================================
(function () {
  const carousel = document.getElementById("product-carousel");
  const prevBtn = document.getElementById("carousel-prev");
  const nextBtn = document.getElementById("carousel-next");
  const playPauseBtn = document.getElementById("carousel-playpause");

  if (!carousel || !prevBtn || !nextBtn || !playPauseBtn) {
    return;
  }

  const items = Array.from(carousel.querySelectorAll(".carousel-item"));
  if (!items.length) return;

  let currentIndex = 0;
  let isPlaying = true;
  let autoPlayInterval = null;
  const AUTO_PLAY_DELAY = 3500;
  let isTransitioning = false;

  // ========================================
  // CROSSFADE TRANSITION ANIMATION
  // ========================================
  function transitionToIndex(newIndex, direction = "next") {
    if (isTransitioning || newIndex === currentIndex) return;
    if (newIndex < 0) newIndex = items.length - 1;
    if (newIndex >= items.length) newIndex = 0;

    isTransitioning = true;

    const currentItem = items[currentIndex];
    const newItem = items[newIndex];

    // Remove all state classes first
    items.forEach(item => {
      item.classList.remove("is-active", "is-exiting", "is-entering", "is-playing");
    });

    // OUTGOING: Slide left & fade out
    currentItem.classList.add("is-exiting");

    // INCOMING: Start from right, slide in & fade in
    newItem.classList.add("is-entering");
    
    // Trigger reflow to ensure transitions work
    void newItem.offsetWidth;

    // Apply active state to new item (triggers transition)
    requestAnimationFrame(() => {
      newItem.classList.remove("is-entering");
      newItem.classList.add("is-active");
      
      if (isPlaying) {
        newItem.classList.add("is-playing");
      }
    });

    // Cleanup after transition
    setTimeout(() => {
      currentItem.classList.remove("is-exiting");
      currentIndex = newIndex;
      isTransitioning = false;
    }, 500); // Match CSS transition duration
  }

  // ========================================
  // NAVIGATION FUNCTIONS
  // ========================================
  function goNext(fromAuto = false) {
    const nextIndex = (currentIndex + 1) % items.length;
    transitionToIndex(nextIndex, "next");
    
    if (!fromAuto) {
      pauseAutoPlay();
    }
  }

  function goPrev() {
    const prevIndex = (currentIndex - 1 + items.length) % items.length;
    transitionToIndex(prevIndex, "prev");
    pauseAutoPlay();
  }

  // ========================================
  // AUTOPLAY CONTROLS
  // ========================================
  function updatePlayPauseUI() {
    if (isPlaying) {
      playPauseBtn.classList.remove("is-paused");
      playPauseBtn.setAttribute("aria-label", "Pausar carrusel");
      items[currentIndex]?.classList.add("is-playing");
    } else {
      playPauseBtn.classList.add("is-paused");
      playPauseBtn.setAttribute("aria-label", "Reproducir carrusel");
      items.forEach(item => item.classList.remove("is-playing"));
    }
  }

  function pauseAutoPlay() {
    if (autoPlayInterval) {
      clearInterval(autoPlayInterval);
      autoPlayInterval = null;
    }
    if (isPlaying) {
      isPlaying = false;
      updatePlayPauseUI();
    }
  }

  function startAutoPlay() {
    if (autoPlayInterval) {
      clearInterval(autoPlayInterval);
    }
    isPlaying = true;
    updatePlayPauseUI();

    autoPlayInterval = setInterval(() => {
      goNext(true);
    }, AUTO_PLAY_DELAY);
  }

  // ========================================
  // BUTTON EVENT LISTENERS
  // ========================================
  prevBtn.addEventListener("click", (e) => {
    e.preventDefault();
    goPrev();
  });

  nextBtn.addEventListener("click", (e) => {
    e.preventDefault();
    goNext();
  });

  playPauseBtn.addEventListener("click", (e) => {
    e.preventDefault();
    if (isPlaying) {
      pauseAutoPlay();
    } else {
      startAutoPlay();
    }
  });

  // ========================================
  // KEYBOARD NAVIGATION (Accessibility)
  // ========================================
  carousel.setAttribute("tabindex", "0");
  carousel.setAttribute("role", "region");
  carousel.setAttribute("aria-label", "Carrusel de productos");

  carousel.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      goPrev();
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      goNext();
    }
  });

  // ========================================
  // TOUCH/SWIPE SUPPORT
  // ========================================
  let touchStartX = 0;
  let touchEndX = 0;

  carousel.addEventListener("touchstart", (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  carousel.addEventListener("touchend", (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, { passive: true });

  function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchStartX - touchEndX;

    if (Math.abs(swipeDistance) > swipeThreshold) {
      if (swipeDistance > 0) {
        // Swiped left -> next
        goNext();
      } else {
        // Swiped right -> prev
        goPrev();
      }
    }
  }

  // ========================================
  // INTERSECTION OBSERVER (Performance)
  // Pause autoplay when carousel is not visible
  // ========================================
  const visibilityObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting && isPlaying) {
          pauseAutoPlay();
        }
      });
    },
    { threshold: 0.3 }
  );
  visibilityObserver.observe(carousel);

  // ========================================
  // INITIALIZATION
  // ========================================
  // Show first item
  items[0].classList.add("is-active", "is-playing");
  startAutoPlay();

  // Cleanup on page unload
  window.addEventListener("beforeunload", () => {
    if (autoPlayInterval) {
      clearInterval(autoPlayInterval);
    }
  });
})();
