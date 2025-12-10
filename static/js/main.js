// ==========================================================================
// KITALURO - Premium JavaScript
// Scroll Reveal & Interactive Animations
// ==========================================================================

/*
 * USO DEL SCROLL REVEAL:
 * 
 * 1. Clases disponibles:
 *    - .reveal        → Aparece desde abajo (translateY)
 *    - .reveal-left   → Aparece desde la izquierda (translateX)
 *    - .reveal-right  → Aparece desde la derecha (translateX)
 *    - .reveal-scale  → Aparece con efecto de escala (scale)
 * 
 * 2. Delays personalizados:
 *    data-delay="200"  → Espera 200ms antes de animar
 * 
 * 3. Efecto cascada automático:
 *    <div data-stagger="100">  → Cada hijo se anima 100ms después del anterior
 *      <div class="reveal"></div>
 *      <div class="reveal"></div>
 *    </div>
 * 
 * 4. Ejemplo completo:
 *    <h1 class="reveal" data-delay="200">Título</h1>
 *    <div data-stagger="150">
 *      <div class="reveal-scale">Card 1</div>
 *      <div class="reveal-scale">Card 2</div>
 *      <div class="reveal-scale">Card 3</div>
 *    </div>
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================================================
    // STAGGER ANIMATION HELPER - SE EJECUTA PRIMERO
    // Aplica delays automáticos a elementos hijos para efecto cascada
    // ==========================================================================
    
    const staggerContainers = document.querySelectorAll('[data-stagger]');
    
    staggerContainers.forEach(container => {
        const children = container.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
        const staggerDelay = parseInt(container.dataset.stagger) || 100; // delay en ms
        
        children.forEach((child, index) => {
            // Solo asignar delay si el elemento no tiene uno ya definido
            if (!child.dataset.delay) {
                child.dataset.delay = index * staggerDelay;
            }
        });
    });
    
    // ==========================================================================
    // SCROLL REVEAL ANIMATION - SE EJECUTA DESPUÉS
    // ==========================================================================
    
    const revealElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
    
    if (revealElements.length > 0) {
        // Crear el observer con opciones optimizadas
        const observerOptions = {
            root: null, // viewport
            rootMargin: '0px 0px -100px 0px', // Activa 100px antes de que sea visible
            threshold: 0.15 // 15% del elemento visible
        };
        
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Añadir clase active con un pequeño delay para efecto escalonado
                    const delay = parseInt(entry.target.dataset.delay) || 0;
                    
                    setTimeout(() => {
                        entry.target.classList.add('active');
                    }, delay);
                    
                    // Opcional: dejar de observar después de animar (mejora performance)
                    // Descomentar la siguiente línea para animar solo una vez:
                    // observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        // Observar todos los elementos con clase reveal
        revealElements.forEach(element => {
            revealObserver.observe(element);
        });
        
        // Debug: Mostrar cuántos elementos están siendo observados
        console.log(`🎬 Scroll Reveal activado: ${revealElements.length} elementos observados`);
    }
    
    // =====================================================================
    // HERO VIDEO AUTOPLAY + INTERSECTION OBSERVER (RESPETA REDUCED MOTION)
    // =====================================================================
    const heroVideo = document.getElementById('heroVideo');
    if (heroVideo) {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (prefersReducedMotion) {
            heroVideo.pause();
            heroVideo.removeAttribute('autoplay');
        } else {
            const tryPlay = () => {
                heroVideo.play().catch(err => {
                    console.warn('Autoplay bloqueado, mostrando poster estático.', err && err.message);
                });
            };

            const observer = new IntersectionObserver(
                entries => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            tryPlay();
                        } else {
                            heroVideo.pause();
                        }
                    });
                },
                { threshold: 0.35 }
            );

            observer.observe(heroVideo);
        }
    }
});
