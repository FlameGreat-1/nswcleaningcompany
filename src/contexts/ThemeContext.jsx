import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme-preference');
    if (saved) {
      return JSON.parse(saved);
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const toggleTheme = () => {
    setIsDark(prev => {
      const newTheme = !prev;
      localStorage.setItem('theme-preference', JSON.stringify(newTheme));
      return newTheme;
    });
  };

  const setTheme = (dark) => {
    setIsDark(dark);
    localStorage.setItem('theme-preference', JSON.stringify(dark));
  };

  useEffect(() => {
    const root = document.documentElement;
    
    if (isDark) {
      root.classList.add('dark', 'app-dark');
      root.classList.remove('light', 'app-light');
    } else {
      root.classList.add('light', 'app-light');
      root.classList.remove('dark', 'app-dark');
    }

    root.style.setProperty('--bg-primary', isDark ? '#180c2e' : '#FFFFFF');
    root.style.setProperty('--bg-secondary', isDark ? '#2d1b4e' : '#F8F9FA');
    root.style.setProperty('--bg-card', isDark ? '#1a0f33' : '#FFFFFF');
    root.style.setProperty('--text-primary', isDark ? '#FFFFFF' : '#180c2e');
    root.style.setProperty('--text-secondary', isDark ? '#f5f5f5' : '#333333');
    root.style.setProperty('--text-muted', isDark ? '#CCCCCC' : '#6B7280');
    root.style.setProperty('--border-color', isDark ? '#4a3b6b' : '#E5E7EB');
    root.style.setProperty('--shadow-color', isDark ? 'rgba(0, 0, 0, 0.5)' : 'rgba(0, 0, 0, 0.1)');
    
    root.style.setProperty('--blue-primary', '#006da6');
    root.style.setProperty('--blue-hover', '#0080c7');
    root.style.setProperty('--blue-dark', '#005a8a');
    root.style.setProperty('--indigo-primary', '#180c2e');
    root.style.setProperty('--indigo-light', '#2d1b4e');
    
    root.style.setProperty('--app-bg-primary', isDark ? '#180c2e' : '#FFFFFF');
    root.style.setProperty('--app-bg-secondary', isDark ? '#2d1b4e' : '#F8F9FA');
    root.style.setProperty('--app-bg-card', isDark ? '#1a0f33' : '#FFFFFF');
    root.style.setProperty('--app-bg-glass', isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.9)');
    root.style.setProperty('--app-text-primary', isDark ? '#FFFFFF' : '#180c2e');
    root.style.setProperty('--app-text-secondary', isDark ? '#f5f5f5' : '#333333');
    root.style.setProperty('--app-text-muted', isDark ? '#CCCCCC' : '#6B7280');
    root.style.setProperty('--app-border', isDark ? '#4a3b6b' : '#E5E7EB');
    root.style.setProperty('--app-border-glass', isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.4)');
    root.style.setProperty('--app-shadow', isDark ? 'rgba(0, 0, 0, 0.5)' : 'rgba(0, 0, 0, 0.1)');
    root.style.setProperty('--app-shadow-lg', isDark ? 'rgba(0, 0, 0, 0.6)' : 'rgba(0, 0, 0, 0.15)');
    root.style.setProperty('--app-shadow-xl', isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(0, 0, 0, 0.2)');
    root.style.setProperty('--app-blue', '#006da6');
    root.style.setProperty('--app-blue-hover', '#0080c7');
    root.style.setProperty('--app-blue-dark', '#005a8a');
    root.style.setProperty('--app-indigo', '#180c2e');
    root.style.setProperty('--app-backdrop-blur', 'blur(12px)');
    root.style.setProperty('--app-glass-bg', isDark ? 'rgba(26, 15, 51, 0.8)' : 'rgba(255, 255, 255, 0.8)');
  }, [isDark]);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => {
      const saved = localStorage.getItem('theme-preference');
      if (!saved) {
        setIsDark(e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const themeConfig = {
    isDark,
    isLight: !isDark,
    toggleTheme,
    setTheme,
    colors: {
      background: {
        primary: isDark ? '#180c2e' : '#FFFFFF',
        secondary: isDark ? '#2d1b4e' : '#F8F9FA',
        card: isDark ? '#1a0f33' : '#FFFFFF',
        chat: isDark ? '#2d1b4e' : '#F1F5F9'
      },
      text: {
        primary: isDark ? '#FFFFFF' : '#180c2e',
        secondary: isDark ? '#f5f5f5' : '#333333',
        muted: isDark ? '#CCCCCC' : '#6B7280',
        inverse: isDark ? '#180c2e' : '#FFFFFF'
      },
      border: isDark ? '#4a3b6b' : '#E5E7EB',
      shadow: isDark ? 'rgba(0, 0, 0, 0.5)' : 'rgba(0, 0, 0, 0.1)',
      blue: {
        primary: '#006da6',
        hover: '#0080c7',
        dark: '#005a8a',
        light: '#4da6d9'
      },
      indigo: {
        primary: '#180c2e',
        light: '#2d1b4e',
        hover: '#3d2b5e'
      }
    },
    classes: {
      background: {
        primary: isDark ? 'bg-[#180c2e]' : 'bg-white',
        secondary: isDark ? 'bg-[#2d1b4e]' : 'bg-gray-50',
        card: isDark ? 'bg-[#1a0f33]' : 'bg-white'
      },
      text: {
        primary: isDark ? 'text-white' : 'text-[#180c2e]',
        secondary: isDark ? 'text-[#f5f5f5]' : 'text-[#333333]',
        muted: isDark ? 'text-[#CCCCCC]' : 'text-gray-400'
      },
      border: isDark ? 'border-[#4a3b6b]' : 'border-gray-200'
    },
    brand: {
      blue: '#006da6',
      blueHover: '#0080c7',
      blueDark: '#005a8a',
      blueLight: '#4da6d9',
      indigo: '#180c2e',
      indigoLight: '#2d1b4e',
      indigoHover: '#3d2b5e'
    }
  };

  return (
    <ThemeContext.Provider value={themeConfig}>
      {children}
    </ThemeContext.Provider>
  );
};
