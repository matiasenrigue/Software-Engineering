/**
 * Update the theme icon based on the current theme.
 * @param {string} theme - The current theme, either 'dark' or 'light'.
 * @param {HTMLElement} iconEl - The HTML element that shows the icon.
 */
export function updateThemeIcon(theme, iconEl) {
    iconEl.textContent = theme === 'dark' ? '☀️' : '🌙';
  }
  
  /**
   * Apply the saved theme or use system preferences if none is saved.
   * @returns {string} - The applied theme ('dark' or 'light').
   */
  export function applySavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      document.documentElement.setAttribute('data-theme', savedTheme);
      return savedTheme;
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-theme', 'dark');
      return 'dark';
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
      return 'light';
    }
  }
  
  /**
   * Set up the theme toggle button.
   * @param {HTMLElement} toggleEl - The theme toggle button element.
   * @param {HTMLElement} iconEl - The element that displays the theme icon.
   */
  export function setupThemeToggle(toggleEl, iconEl) {
    toggleEl.addEventListener('click', function () {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme, iconEl);
    });
  }
  
  /**
   * Watch for system theme changes if no preference is saved.
   * @param {HTMLElement} iconEl - The element that displays the theme icon.
   */
  export function watchSystemTheme(iconEl) {
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
        if (!localStorage.getItem('theme')) {
          const newTheme = event.matches ? 'dark' : 'light';
          document.documentElement.setAttribute('data-theme', newTheme);
          updateThemeIcon(newTheme, iconEl);
        }
      });
    }
  }
  
  /**
   * Automatically dismiss flash messages after a delay.
   * @param {number} delay - Delay in milliseconds before dismissing messages (default 6000).
   */
  export function autoDismissFlashMessages(delay = 6000) {
    setTimeout(() => {
      document.querySelectorAll('.flash-message').forEach((message) => {
        message.style.opacity = '0';
        message.style.transform = 'translateY(-10px)';
        setTimeout(() => {
          message.remove();
        }, 300);
      });
    }, delay);
  }
  
  /**
   * Initializes the styling behaviors:
   * - Applies saved theme (or detects system theme),
   * - Sets up the theme toggle button,
   * - Watches for system theme changes, and
   * - Sets up auto-dismiss for flash messages.
   */
  export function initStyling() {
    const themeToggleEl = document.getElementById('theme-toggle');
    const themeIconEl = document.getElementById('theme-icon');
  
    if (themeToggleEl && themeIconEl) {
      // Apply the saved or default theme and update the icon.
      const appliedTheme = applySavedTheme();
      updateThemeIcon(appliedTheme, themeIconEl);
  
      // Set up the toggle button and the system theme watcher.
      setupThemeToggle(themeToggleEl, themeIconEl);
      watchSystemTheme(themeIconEl);
    }
  
    // Set up auto-dismiss for flash messages.
    autoDismissFlashMessages();
  }
  
  // Automatically initialize after the DOM loads.
  document.addEventListener('DOMContentLoaded', initStyling);
  