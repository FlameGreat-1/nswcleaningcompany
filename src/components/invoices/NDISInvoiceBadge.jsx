import { memo } from 'react';
import { ShieldCheckIcon } from '@heroicons/react/24/outline';

const NDISInvoiceBadge = memo(({ className = '', size = 'sm' }) => {
  const getSizeClasses = (size) => {
    const sizes = {
      xs: 'px-1.5 py-0.5 text-xs',
      sm: 'px-2 py-1 text-xs',
      md: 'px-2.5 py-1 text-sm',
      lg: 'px-3 py-1.5 text-sm'
    };
    return sizes[size] || sizes.sm;
  };

  const getIconSize = (size) => {
    const iconSizes = {
      xs: 'w-3 h-3',
      sm: 'w-3 h-3',
      md: 'w-4 h-4',
      lg: 'w-4 h-4'
    };
    return iconSizes[size] || iconSizes.sm;
  };

  return (
    <span 
      className={`
        inline-flex items-center gap-1 rounded-full font-medium border
        bg-blue-50 text-blue-700 border-blue-200
        ${getSizeClasses(size)}
        ${className}
      `}
      title="NDIS Invoice"
    >
      <ShieldCheckIcon className={getIconSize(size)} />
      <span>NDIS</span>
    </span>
  );
});

NDISInvoiceBadge.displayName = 'NDISInvoiceBadge';

export default NDISInvoiceBadge;
