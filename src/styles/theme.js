export const theme = {
  colors: {
    background: {
      primary: {
        dark: '#180c2e',
        light: '#FFFFFF'
      },
      secondary: {
        dark: '#2d1b4e', 
        light: '#F8F9FA'
      },
      card: {
        dark: '#1a0f33',
        light: '#FFFFFF'
      },
      chat: {
        dark: '#2d1b4e',
        light: '#F1F5F9'
      }
    },
    
    text: {
      primary: {
        dark: '#FFFFFF',
        light: '#180c2e'
      },
      secondary: {
        dark: '#f5f5f5',
        light: '#333333'
      },
      muted: {
        dark: '#CCCCCC',
        light: '#6B7280'
      },
      inverse: {
        dark: '#180c2e',
        light: '#FFFFFF'
      }
    },
    
    border: {
      dark: '#4a3b6b',
      light: '#E5E7EB'
    },
    
    shadow: {
      dark: 'rgba(0, 0, 0, 0.5)',
      light: 'rgba(0, 0, 0, 0.1)'
    },
    
    primary: {
      blue: '#006da6',
      blueHover: '#0080c7',
      blueDark: '#005a8a',
      blueLight: '#4da6d9',
      indigo: '#180c2e',
      indigoLight: '#2d1b4e',
      indigoHover: '#3d2b5e',
      blueGlow: {
        dark: 'radial-gradient(circle, #005a8a 0%, #180c2e 100%)',
        light: 'radial-gradient(circle, #006da6 0%, #FFFFFF 100%)'
      }
    },
    
    button: {
      blue: '#006da6',
      blueHover: '#0080c7',
      indigo: '#180c2e',
      text: '#FFFFFF'
    },
    
    chat: {
      sent: {
        dark: '#1a0f33',
        light: '#e6f3ff'
      },
      received: {
        dark: '#2d1b4e',
        light: '#F5F5F5'
      }
    },
    
    inputBorder: '#006da6'
  },
  
  typography: {
    fontFamily: {
      base: 'Inter, system-ui, -apple-system, sans-serif'
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '2rem',
      '4xl': '3rem',
      '5xl': '4rem',
      '6xl': '4.5rem'
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
      black: '900'
    },
    lineHeight: {
      tight: '1.1',
      normal: '1.2',
      relaxed: '1.4',
      loose: '1.6'
    }
  },
  
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '2rem',
    xl: '4rem',
    '2xl': '6rem',
    '3xl': '7.5rem'
  },
  
  layout: {
    containerMaxWidth: '71.25rem',
    containerPadding: '0 1.5rem',
    sectionPadding: '4rem 0',
    chatBubblePadding: '0.75rem 1rem'
  },
  
  borderRadius: {
    none: '0',
    sm: '0.25rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    '2xl': '1.5rem',
    '3xl': '2rem',
    full: '9999px',
    circle: '50%'
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: {
      dark: '0 4px 12px rgba(0, 0, 0, 0.5)',
      light: '0 4px 12px rgba(0, 0, 0, 0.1)'
    },
    lg: {
      dark: '0 10px 25px rgba(0, 0, 0, 0.6)',
      light: '0 10px 25px rgba(0, 0, 0, 0.15)'
    },
    xl: {
      dark: '0 20px 40px rgba(0, 0, 0, 0.7)',
      light: '0 20px 40px rgba(0, 0, 0, 0.2)'
    },
    glow: {
      blue: '0 0 20px rgba(0, 109, 166, 0.3)',
      blueStrong: '0 0 40px rgba(0, 109, 166, 0.5)',
      indigo: '0 0 20px rgba(24, 12, 46, 0.3)',
      indigoStrong: '0 0 40px rgba(24, 12, 46, 0.5)'
    }
  },
  
  components: {
    avatar: {
      sm: '2rem',
      md: '2.5rem',
      lg: '3rem',
      xl: '4rem'
    },
    button: {
      padding: {
        sm: '0.5rem 1rem',
        md: '0.75rem 1.5rem',
        lg: '1rem 2rem'
      },
      radius: '9999px',
      height: {
        sm: '2rem',
        md: '2.5rem',
        lg: '3rem'
      }
    },
    card: {
      padding: {
        sm: '1rem',
        md: '1.5rem',
        lg: '2rem'
      },
      radius: '1rem'
    },
    input: {
      height: '2.5rem',
      padding: '0.75rem',
      radius: '0.5rem'
    }
  },
  
  breakpoints: {
    sm: '40rem',
    md: '48rem',
    lg: '64rem',
    xl: '80rem',
    '2xl': '96rem'
  },
  
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    normal: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: '600ms cubic-bezier(0.68, -0.55, 0.265, 1.55)'
  },
  
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modal: 1040,
    popover: 1050,
    tooltip: 1060,
    toast: 1070
  }
};

export const getThemeValue = (path, isDark = true) => {
  const keys = path.split('.');
  let value = theme;
  
  for (const key of keys) {
    value = value[key];
  }
  
  if (typeof value === 'object' && value.dark && value.light) {
    return isDark ? value.dark : value.light;
  }
  
  return value;
};

export const generateCSSVariables = (isDark = true) => {
  return {
    '--color-bg-primary': getThemeValue('colors.background.primary', isDark),
    '--color-bg-secondary': getThemeValue('colors.background.secondary', isDark),
    '--color-bg-card': getThemeValue('colors.background.card', isDark),
    '--color-text-primary': getThemeValue('colors.text.primary', isDark),
    '--color-text-secondary': getThemeValue('colors.text.secondary', isDark),
    '--color-text-muted': getThemeValue('colors.text.muted', isDark),
    '--color-border': getThemeValue('colors.border', isDark),
    '--color-shadow': getThemeValue('colors.shadow', isDark),
    '--color-blue': theme.colors.primary.blue,
    '--color-blue-hover': theme.colors.primary.blueHover,
    '--color-blue-dark': theme.colors.primary.blueDark,
    '--color-indigo': theme.colors.primary.indigo,
    '--color-indigo-light': theme.colors.primary.indigoLight,
    '--font-family-base': theme.typography.fontFamily.base,
    '--border-radius-md': theme.borderRadius.md,
    '--border-radius-lg': theme.borderRadius.lg,
    '--border-radius-xl': theme.borderRadius.xl,
    '--transition-normal': theme.transitions.normal,
    '--shadow-md': getThemeValue('shadows.md', isDark),
    '--shadow-lg': getThemeValue('shadows.lg', isDark),
    '--shadow-xl': getThemeValue('shadows.xl', isDark)
  };
};

export const getBrandColors = () => {
  return {
    blue: theme.colors.primary.blue,
    blueHover: theme.colors.primary.blueHover,
    blueDark: theme.colors.primary.blueDark,
    blueLight: theme.colors.primary.blueLight,
    indigo: theme.colors.primary.indigo,
    indigoLight: theme.colors.primary.indigoLight,
    indigoHover: theme.colors.primary.indigoHover
  };
};

export const getComponentStyles = (component, variant = 'md') => {
  const componentConfig = theme.components[component];
  if (!componentConfig) return {};
  
  const styles = {};
  Object.keys(componentConfig).forEach(key => {
    if (typeof componentConfig[key] === 'object' && componentConfig[key][variant]) {
      styles[key] = componentConfig[key][variant];
    } else if (typeof componentConfig[key] === 'string') {
      styles[key] = componentConfig[key];
    }
  });
  
  return styles;
};
