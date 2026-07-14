/**
 * Luxury Timers - LogerTogo
 * Gestion anti-drift et affichage premium des chronomètres (Travail, Pause, Séjours)
 */

document.addEventListener("DOMContentLoaded", function() {
    // Helper: format total seconds into HH:MM:SS with elegant badges
    function renderElegantTime(totalSeconds, themeClass = "bg-dark") {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = Math.floor(totalSeconds % 60);
        
        const hStr = String(hours).padStart(2, '0');
        const mStr = String(minutes).padStart(2, '0');
        const sStr = String(seconds).padStart(2, '0');
        
        return `
            <div class="d-flex align-items-center gap-1 font-monospace" style="font-size: 1.1rem; font-weight: 700;">
                <div class="${themeClass} text-white rounded px-2 py-1 shadow-sm d-flex align-items-baseline">
                    ${hStr}<span class="text-white-50 ms-1" style="font-size: 0.65rem;">h</span>
                </div>
                <span class="text-muted">:</span>
                <div class="${themeClass} text-white rounded px-2 py-1 shadow-sm d-flex align-items-baseline">
                    ${mStr}<span class="text-white-50 ms-1" style="font-size: 0.65rem;">m</span>
                </div>
                <span class="text-muted">:</span>
                <div class="bg-danger text-white rounded px-2 py-1 shadow-sm d-flex align-items-baseline">
                    ${sStr}<span class="text-white-50 ms-1" style="font-size: 0.65rem;">s</span>
                </div>
            </div>
        `;
    }

    function renderElegantCountdown(diffMs, type) {
        if (diffMs <= 0) {
            if (type === 'checkin') {
                return `<i class="fa-solid fa-triangle-exclamation text-danger me-1"></i> <span class="text-danger fw-bold">Arrivée dépassée !</span>`;
            } else {
                return `<i class="fa-solid fa-triangle-exclamation text-danger me-1"></i> <span class="text-danger fw-bold">Séjour dépassé !</span>`;
            }
        }

        const d = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        const h = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const m = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((diffMs % (1000 * 60)) / 1000);
        
        let html = `<div class="d-flex align-items-center gap-1 font-monospace mt-1" style="font-size: 0.85rem; font-weight: 700;">`;
        
        if (type === 'checkin') {
            html += `<i class="fa-solid fa-plane-arrival text-primary me-1"></i>`;
        } else {
            html += `<i class="fa-solid fa-plane-departure text-danger me-1"></i>`;
        }
        
        const theme = type === 'checkin' ? 'bg-primary' : 'bg-danger';

        if (d > 0) {
            html += `<div class="bg-dark text-white rounded px-1 py-0 shadow-sm d-flex align-items-baseline">${d}<span class="text-white-50 ms-1" style="font-size: 0.55rem;">j</span></div><span class="text-muted"> </span>`;
        }
        if (h > 0 || d > 0) {
            html += `<div class="bg-dark text-white rounded px-1 py-0 shadow-sm d-flex align-items-baseline">${String(h).padStart(2, '0')}<span class="text-white-50 ms-1" style="font-size: 0.55rem;">h</span></div><span class="text-muted">:</span>`;
        }
        
        html += `<div class="bg-dark text-white rounded px-1 py-0 shadow-sm d-flex align-items-baseline">${String(m).padStart(2, '0')}<span class="text-white-50 ms-1" style="font-size: 0.55rem;">m</span></div><span class="text-muted">:</span>`;
        html += `<div class="${theme} text-white rounded px-1 py-0 shadow-sm d-flex align-items-baseline">${String(s).padStart(2, '0')}<span class="text-white-50 ms-1" style="font-size: 0.55rem;">s</span></div>`;
        html += `</div>`;
        
        return html;
    }

    // --- 1. Live Work Timers (Anti-Drift) ---
    const workTimers = document.querySelectorAll('.luxury-work-timer');
    workTimers.forEach(el => {
        // Initial seconds loaded from server
        let initialSeconds = parseFloat((el.getAttribute('data-seconds') || '0').replace(',', '.'));
        // Local start time to calculate true elapsed time (anti-drift)
        const localStartTime = Date.now();

        function updateWorkTimer() {
            const elapsedSeconds = (Date.now() - localStartTime) / 1000;
            const currentSeconds = Math.max(0, initialSeconds + elapsedSeconds);
            el.innerHTML = renderElegantTime(currentSeconds, "bg-success");
        }
        
        updateWorkTimer();
        setInterval(updateWorkTimer, 1000);
    });

    // --- 2. Live Break Timers (Anti-Drift) ---
    const breakTimers = document.querySelectorAll('.luxury-break-timer');
    breakTimers.forEach(el => {
        const startStr = el.getAttribute('data-start');
        if (startStr) {
            const serverStartTime = new Date(startStr).getTime();
            
            function updateBreakTimer() {
                const diffSeconds = Math.max(0, (Date.now() - serverStartTime) / 1000);
                el.innerHTML = renderElegantTime(diffSeconds, "bg-info");
            }
            
            updateBreakTimer();
            setInterval(updateBreakTimer, 1000);
        }
    });

    // --- 3. Bookings Countdowns (Anti-Drift) ---
    const countdowns = document.querySelectorAll('.luxury-live-countdown');
    countdowns.forEach(el => {
        const targetStr = el.getAttribute('data-target');
        const type = el.getAttribute('data-type'); // 'checkin' or 'checkout'
        if (targetStr) {
            const targetTime = new Date(targetStr).getTime();
            
            function updateCountdown() {
                const diffMs = targetTime - Date.now();
                el.innerHTML = renderElegantCountdown(diffMs, type);
            }
            
            updateCountdown();
            setInterval(updateCountdown, 1000);
        }
    });
});
