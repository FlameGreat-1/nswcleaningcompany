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
  // Force light theme by setting isDark to false and not using localStorage or system preference
  const [isDark, setIsDark] = useState(false);

  // Keep the toggleTheme function but make it do nothing
  const toggleTheme = () => {
    console.log('Theme toggling is currently disabled');
    // No state change happens
  };

  // Keep setTheme but make it do nothing
  const setTheme = (dark) => {
    console.log('Theme setting is currently disabled');
    // No state change happens
  };

  useEffect(() => {
    const root = document.documentElement;
    
    // Always apply light theme classes
    root.classList.add('light', 'app-light');
    root.classList.remove('dark', 'app-dark');

    // Set all CSS variables for light theme
    root.style.setProperty('--bg-primary', '#FFFFFF');
    root.style.setProperty('--bg-secondary', '#F8F9FA');
    root.style.setProperty('--bg-card', '#FFFFFF');
    root.style.setProperty('--text-primary', '#180c2e');
    root.style.setProperty('--text-secondary', '#333333');
    root.style.setProperty('--text-muted', '#6B7280');
    root.style.setProperty('--border-color', '#E5E7EB');
    root.style.setProperty('--shadow-color', 'rgba(0, 0, 0, 0.1)');
    
    root.style.setProperty('--blue-primary', '#006da6');
    root.style.setProperty('--blue-hover', '#0080c7');
    root.style.setProperty('--blue-dark', '#005a8a');
    root.style.setProperty('--indigo-primary', '#180c2e');
    root.style.setProperty('--indigo-light', '#2d1b4e');
    
    root.style.setProperty('--app-bg-primary', '#FFFFFF');
    root.style.setProperty('--app-bg-secondary', '#F8F9FA');
    root.style.setProperty('--app-bg-card', '#FFFFFF');
    root.style.setProperty('--app-bg-glass', 'rgba(255, 255, 255, 0.9)');
    root.style.setProperty('--app-text-primary', '#180c2e');
    root.style.setProperty('--app-text-secondary', '#333333');
    root.style.setProperty('--app-text-muted', '#6B7280');
    root.style.setProperty('--app-border', '#E5E7EB');
    root.style.setProperty('--app-border-glass', 'rgba(255, 255, 255, 0.4)');
    root.style.setProperty('--app-shadow', 'rgba(0, 0, 0, 0.1)');
    root.style.setProperty('--app-shadow-lg', 'rgba(0, 0, 0, 0.15)');
    root.style.setProperty('--app-shadow-xl', 'rgba(0, 0, 0, 0.2)');
    root.style.setProperty('--app-blue', '#006da6');
    root.style.setProperty('--app-blue-hover', '#0080c7');
    root.style.setProperty('--app-blue-dark', '#005a8a');
    root.style.setProperty('--app-indigo', '#180c2e');
    root.style.setProperty('--app-backdrop-blur', 'blur(12px)');
    root.style.setProperty('--app-glass-bg', 'rgba(255, 255, 255, 0.8)');
  }, []); // No dependency on isDark since it never changes

  // Remove the system preference listener since we're forcing light mode
  // useEffect for media query listener removed

  const themeConfig = {
    isDark: false, // Always light mode
    isLight: true, // Always light mode
    toggleTheme, // No-op function
    setTheme, // No-op function
    colors: {
      background: {
        primary: '#FFFFFF',
        secondary: '#F8F9FA',
        card: '#FFFFFF',
        chat: '#F1F5F9'
      },
      text: {
        primary: '#180c2e',
        secondary: '#333333',
        muted: '#6B7280',
        inverse: '#FFFFFF'
      },
      border: '#E5E7EB',
      shadow: 'rgba(0, 0, 0, 0.1)',
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
        primary: 'bg-white',
        secondary: 'bg-gray-50',
        card: 'bg-white'
      },
      text: {
        primary: 'text-[#180c2e]',
        secondary: 'text-[#333333]',
        muted: 'text-gray-400'
      },
      border: 'border-gray-200'
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
