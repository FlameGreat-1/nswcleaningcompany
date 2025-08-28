import { useState, useEffect } from 'react';

const LoadingSpinner = ({ 
  size = 'nano', 
  variant = 'branded',
  color = 'primary', 
  text = '',
  className = ''
}) => {
  const logoSizeClasses = {
    nano: { container: 'w-3 h-3', logo: 'w-2 h-2', ring: 'w-3 h-3' },
    micro: { container: 'w-4 h-4', logo: 'w-2.5 h-2.5', ring: 'w-4 h-4' },
    tiny: { container: 'w-5 h-5', logo: 'w-3 h-3', ring: 'w-5 h-5' },
    xxs: { container: 'w-6 h-6', logo: 'w-4 h-4', ring: 'w-6 h-6' },
    xs: { container: 'w-8 h-8', logo: 'w-5 h-5', ring: 'w-8 h-8' },
    sm: { container: 'w-12 h-12', logo: 'w-8 h-8', ring: 'w-12 h-12' },
    md: { container: 'w-16 h-16', logo: 'w-10 h-10', ring: 'w-16 h-16' },
    lg: { container: 'w-20 h-20', logo: 'w-12 h-12', ring: 'w-20 h-20' },
    xl: { container: 'w-28 h-28', logo: 'w-16 h-16', ring: 'w-28 h-28' },
    '2xl': { container: 'w-32 h-32', logo: 'w-20 h-20', ring: 'w-32 h-32' }
  };

  const sizeClasses = {
    nano: 'w-0.5 h-0.5',
    micro: 'w-1 h-1',
    tiny: 'w-1.5 h-1.5',
    xxs: 'w-2 h-2',
    xs: 'w-2.5 h-2.5',
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8',
    '2xl': 'w-12 h-12'
  };
  
  const colorClasses = {
    primary: 'border-[#006da6]',
    white: 'border-white',
    gray: 'border-gray-400',
    black: 'border-black',
    gradient: 'border-transparent'
  };

  const BrandedSpinner = () => {
    const sizes = logoSizeClasses[size];
    
    return (
      <div className="flex flex-col items-center justify-center">
        <div className={`relative flex items-center justify-center ${sizes.container}`}>
          <img
            src="/static/logo.svg"
            alt="NSWCC Logo"
            className={`${sizes.logo} object-contain z-10`}
          />
          <div 
            className={`absolute top-0 left-0 ${sizes.ring} border-[0.25px] border-transparent border-t-[#006da6] border-r-[#0080c7] rounded-full animate-spin`}
            style={{ animationDuration: '2s' }}
          ></div>
          <div 
            className={`absolute top-0 left-0 ${sizes.ring} border-[0.25px] border-transparent border-b-[#180c2e] border-l-[#2d1b4e] rounded-full animate-spin`}
            style={{ animationDuration: '3s', animationDirection: 'reverse' }}
          ></div>
        </div>
        {text && (
          <p className="text-[8px] font-medium text-gray-600 dark:text-gray-300 animate-pulse mt-0.5">
            {text}
          </p>
        )}
      </div>
    );
  };

  const ClassicSpinner = () => (
    <div className="flex flex-col items-center justify-center">
      <div className={`animate-spin rounded-full border-[0.25px] border-transparent ${sizeClasses[size]} ${
        color === 'gradient' 
          ? 'border-t-[#006da6] border-r-[#0080c7] border-b-[#180c2e]' 
          : `border-t-current ${colorClasses[color]}`
      }`}></div>
      {text && (
        <p className="text-[8px] font-medium text-gray-600 dark:text-gray-300 mt-0.5">
          {text}
        </p>
      )}
    </div>
  );

  const PulseSpinner = () => (
    <div className="flex flex-col items-center justify-center">
      <div className={`${sizeClasses[size]} rounded-full bg-gradient-to-r from-[#006da6] to-[#180c2e] animate-pulse`}></div>
      {text && (
        <p className="text-[8px] font-medium text-gray-600 dark:text-gray-300 mt-0.5">
          {text}
        </p>
      )}
    </div>
  );

  const DotsSpinner = () => (
    <div className="flex flex-col items-center justify-center">
      <div className="flex space-x-0.5">
        <div className="w-0.5 h-0.5 bg-[#006da6] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-0.5 h-0.5 bg-[#0080c7] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-0.5 h-0.5 bg-[#180c2e] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
      {text && (
        <p className="text-[8px] font-medium text-gray-600 dark:text-gray-300 mt-0.5">
          {text}
        </p>
      )}
    </div>
  );

  const renderSpinner = () => {
    switch (variant) {
      case 'branded':
        return <BrandedSpinner />;
      case 'classic':
        return <ClassicSpinner />;
      case 'pulse':
        return <PulseSpinner />;
      case 'dots':
        return <DotsSpinner />;
      default:
        return <BrandedSpinner />;
    }
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      {renderSpinner()}
    </div>
  );
};

export default LoadingSpinner;
