import { useTheme } from '../../contexts/ThemeContext.jsx';

const ThemeToggle = ({ className = '' }) => {
  // We still import useTheme but we'll ignore the toggleTheme function
  const { isDark } = useTheme();
  
  // Always show light theme UI regardless of context state
  const forcedLightTheme = false; // false means light theme in your implementation

  return (
    <button
      // Remove onClick to disable toggling
      className={`relative group perspective-1000 ${className}`}
      aria-label="Light mode enabled"
    >
      <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6] to-[#180c2e] rounded-2xl blur opacity-0 group-hover:opacity-40 transition-all duration-700"></div>
      <div className="relative w-12 h-12 app-bg-glass backdrop-blur-xl border-2 app-border-glass rounded-2xl flex items-center justify-center hover:app-bg-card hover:border-[#006da6]/50 transition-all duration-700 hover:-translate-y-2 hover:scale-110 hover:rotate-12 transform-gpu shadow-xl hover:shadow-2xl overflow-hidden"
           style={{ transformStyle: 'preserve-3d' }}>
        <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/10 via-transparent to-[#180c2e]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-2xl"></div>
        
        <div className="relative z-10 text-2xl transition-all duration-500 group-hover:scale-110">
          {/* Always show moon emoji for light theme */}
          <span className="animate-pulse">🌙</span>
        </div>
        
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#006da6] rounded-full opacity-0 group-hover:opacity-100 animate-ping transition-opacity duration-700"></div>
      </div>
    </button>
  );
};

export default ThemeToggle;
