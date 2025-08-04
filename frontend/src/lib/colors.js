/**
 * Paleta de cores moderna inspirada no macOS
 * Suporte completo a tema claro e escuro
 */

export const colors = {
  // Cores primárias - Azul macOS
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    950: '#172554',
  },

  // Cores secundárias - Verde saúde
  secondary: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
    950: '#052e16',
  },

  // Cores de sucesso - Verde
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },

  // Cores de aviso - Amarelo
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
  },

  // Cores de erro - Vermelho
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },

  // Cores neutras - Cinza macOS
  neutral: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#e5e5e5',
    300: '#d4d4d4',
    400: '#a3a3a3',
    500: '#737373',
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717',
    950: '#0a0a0a',
  },

  // Cores de fundo - Branco/Cinza claro
  background: {
    light: '#ffffff',
    dark: '#0a0a0a',
  },

  // Cores de superfície - Cinza muito claro/Escuro
  surface: {
    light: '#fafafa',
    dark: '#171717',
  },

  // Cores de borda
  border: {
    light: '#e5e5e5',
    dark: '#262626',
  },

  // Cores de texto
  text: {
    primary: {
      light: '#171717',
      dark: '#fafafa',
    },
    secondary: {
      light: '#525252',
      dark: '#a3a3a3',
    },
    tertiary: {
      light: '#737373',
      dark: '#737373',
    },
  },

  // Cores especiais para saúde
  health: {
    // IMC - Cores para diferentes classificações
    imc: {
      underweight: '#3b82f6', // Azul
      normal: '#22c55e',      // Verde
      overweight: '#f59e0b',  // Amarelo
      obese: '#ef4444',       // Vermelho
    },
    
    // Macronutrientes
    macros: {
      protein: '#ef4444',     // Vermelho
      carbs: '#22c55e',       // Verde
      fat: '#f59e0b',         // Amarelo
      fiber: '#8b5cf6',       // Roxo
    },

    // Atividade física
    activity: {
      low: '#ef4444',         // Vermelho
      moderate: '#f59e0b',    // Amarelo
      high: '#22c55e',        // Verde
      very_high: '#16a34a',   // Verde escuro
    },
  },

  // Gradientes modernos
  gradients: {
    primary: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    secondary: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
    health: 'linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%)',
    premium: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
    sunset: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
  },

  // Sombras modernas
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  },
};

// Função para obter cores baseadas no tema
export const getThemeColors = (theme = 'light') => {
  return {
    background: colors.background[theme],
    surface: colors.surface[theme],
    border: colors.border[theme],
    text: {
      primary: colors.text.primary[theme],
      secondary: colors.text.secondary[theme],
      tertiary: colors.text.tertiary[theme],
    },
  };
};

// Função para obter cores de saúde
export const getHealthColors = (type, value) => {
  switch (type) {
    case 'imc':
      if (value < 18.5) return colors.health.imc.underweight;
      if (value < 25) return colors.health.imc.normal;
      if (value < 30) return colors.health.imc.overweight;
      return colors.health.imc.obese;
    
    case 'macros':
      return colors.health.macros[value] || colors.primary[500];
    
    case 'activity':
      if (value === 'low') return colors.health.activity.low;
      if (value === 'moderate') return colors.health.activity.moderate;
      if (value === 'high') return colors.health.activity.high;
      return colors.health.activity.very_high;
    
    default:
      return colors.primary[500];
  }
};

export default colors;