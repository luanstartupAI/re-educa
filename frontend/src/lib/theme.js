/**
 * Sistema de tema com suporte a claro/escuro
 * Inspirado no macOS
 */

import { colors, getThemeColors } from './colors.js';

export const theme = {
  // Configurações de tema
  config: {
    defaultTheme: 'system',
    storageKey: 're-educa-theme',
    themes: ['light', 'dark', 'system'],
  },

  // Tokens de design
  tokens: {
    // Espaçamentos
    spacing: {
      xs: '0.25rem',    // 4px
      sm: '0.5rem',     // 8px
      md: '1rem',       // 16px
      lg: '1.5rem',     // 24px
      xl: '2rem',       // 32px
      '2xl': '3rem',    // 48px
      '3xl': '4rem',    // 64px
      '4xl': '6rem',    // 96px
    },

    // Bordas arredondadas
    borderRadius: {
      none: '0',
      sm: '0.125rem',   // 2px
      md: '0.375rem',   // 6px
      lg: '0.5rem',     // 8px
      xl: '0.75rem',    // 12px
      '2xl': '1rem',    // 16px
      '3xl': '1.5rem',  // 24px
      full: '9999px',
    },

    // Tipografia
    typography: {
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        mono: [
          'SF Mono',
          'Monaco',
          'Inconsolata',
          'Roboto Mono',
          'monospace',
        ],
      },
      fontSize: {
        xs: '0.75rem',    // 12px
        sm: '0.875rem',   // 14px
        base: '1rem',     // 16px
        lg: '1.125rem',   // 18px
        xl: '1.25rem',    // 20px
        '2xl': '1.5rem',  // 24px
        '3xl': '1.875rem', // 30px
        '4xl': '2.25rem',  // 36px
        '5xl': '3rem',     // 48px
        '6xl': '3.75rem',  // 60px
      },
      fontWeight: {
        thin: '100',
        extralight: '200',
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
        black: '900',
      },
      lineHeight: {
        none: '1',
        tight: '1.25',
        snug: '1.375',
        normal: '1.5',
        relaxed: '1.625',
        loose: '2',
      },
    },

    // Animações
    animation: {
      duration: {
        fast: '150ms',
        normal: '300ms',
        slow: '500ms',
      },
      easing: {
        linear: 'linear',
        ease: 'ease',
        easeIn: 'ease-in',
        easeOut: 'ease-out',
        easeInOut: 'ease-in-out',
        spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
    },

    // Z-index
    zIndex: {
      hide: '-1',
      auto: 'auto',
      base: '0',
      docked: '10',
      dropdown: '1000',
      sticky: '1100',
      banner: '1200',
      overlay: '1300',
      modal: '1400',
      popover: '1500',
      skipLink: '1600',
      toast: '1700',
      tooltip: '1800',
    },
  },

  // Cores dinâmicas baseadas no tema
  getColors: (theme = 'light') => {
    const themeColors = getThemeColors(theme);
    
    return {
      // Cores base
      ...colors,
      ...themeColors,
      
      // Cores específicas do tema
      brand: {
        primary: colors.primary[500],
        secondary: colors.secondary[500],
        accent: colors.primary[400],
      },
      
      // Estados
      state: {
        hover: theme === 'dark' ? colors.neutral[800] : colors.neutral[100],
        active: theme === 'dark' ? colors.neutral[700] : colors.neutral[200],
        disabled: theme === 'dark' ? colors.neutral[800] : colors.neutral[100],
        focus: colors.primary[500],
      },
      
      // Feedback
      feedback: {
        success: colors.success[500],
        warning: colors.warning[500],
        error: colors.error[500],
        info: colors.primary[500],
      },
    };
  },

  // Utilitários de tema
  utils: {
    // Verifica se o sistema prefere tema escuro
    isSystemDark: () => {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    },

    // Obtém tema atual
    getCurrentTheme: () => {
      const stored = localStorage.getItem(theme.config.storageKey);
      if (stored === 'system') {
        return theme.utils.isSystemDark() ? 'dark' : 'light';
      }
      return stored || theme.config.defaultTheme;
    },

    // Define tema
    setTheme: (newTheme) => {
      if (theme.config.themes.includes(newTheme)) {
        localStorage.setItem(theme.config.storageKey, newTheme);
        theme.utils.applyTheme(newTheme);
      }
    },

    // Aplica tema ao DOM
    applyTheme: (themeName) => {
      const currentTheme = themeName === 'system' 
        ? (theme.utils.isSystemDark() ? 'dark' : 'light')
        : themeName;
      
      document.documentElement.setAttribute('data-theme', currentTheme);
      document.documentElement.classList.remove('light', 'dark');
      document.documentElement.classList.add(currentTheme);
    },

    // Inicializa tema
    init: () => {
      const currentTheme = theme.utils.getCurrentTheme();
      theme.utils.applyTheme(currentTheme);
      
          // Listener para mudanças do sistema
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      const stored = localStorage.getItem(theme.config.storageKey);
      if (stored === 'system') {
        theme.utils.applyTheme('system');
      }
    });
    },
  },
};

import React from 'react';

// Hook para React
export const useTheme = () => {
  const [currentTheme, setCurrentTheme] = React.useState(theme.utils.getCurrentTheme());
  
  React.useEffect(() => {
    const handleStorageChange = () => {
      setCurrentTheme(theme.utils.getCurrentTheme());
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);
  
  const toggleTheme = () => {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    theme.utils.setTheme(newTheme);
    setCurrentTheme(newTheme);
  };
  
  const setTheme = (newTheme) => {
    theme.utils.setTheme(newTheme);
    setCurrentTheme(newTheme);
  };
  
  return {
    theme: currentTheme,
    setTheme,
    toggleTheme,
    colors: theme.getColors(currentTheme),
  };
};

export default theme;