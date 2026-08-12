/**
 * Shared UI utilities for turtifications
 */
(function () {
    'use strict';

    // Toast notifications
    window.showToast = function (message, type) {
        type = type || 'info';
        var container = document.getElementById('toast-container');
        if (!container) return;

        var toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        toast.setAttribute('role', 'status');
        toast.textContent = message;
        container.appendChild(toast);

        requestAnimationFrame(function () {
            toast.classList.add('toast-visible');
        });

        setTimeout(function () {
            toast.classList.remove('toast-visible');
            setTimeout(function () {
                toast.remove();
            }, 300);
        }, 3500);
    };

    // Replace alert() calls with toasts when possible
    window.notify = function (message, type) {
        if (typeof window.showToast === 'function') {
            window.showToast(message, type || 'info');
        } else {
            alert(message);
        }
    };

    function initMobileNav() {
        var toggle = document.getElementById('mobile-menu-toggle');
        var nav = document.getElementById('main-nav');
        var overlay = document.getElementById('nav-overlay');
        if (!toggle || !nav) return;

        function closeNav() {
            nav.classList.remove('mobile-nav-open');
            document.body.classList.remove('nav-open');
            toggle.setAttribute('aria-expanded', 'false');
            if (overlay) overlay.classList.remove('visible');
        }

        function openNav() {
            nav.classList.add('mobile-nav-open');
            document.body.classList.add('nav-open');
            toggle.setAttribute('aria-expanded', 'true');
            if (overlay) overlay.classList.add('visible');
        }

        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            if (nav.classList.contains('mobile-nav-open')) {
                closeNav();
            } else {
                openNav();
            }
        });

        nav.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', closeNav);
        });

        if (overlay) {
            overlay.addEventListener('click', closeNav);
        }

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeNav();
        });
    }

    document.addEventListener('DOMContentLoaded', initMobileNav);
})();
