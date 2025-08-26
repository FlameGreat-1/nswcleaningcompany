const QuoteStatusBadge = ({ 
  status, 
  size = 'md', 
  className = '' 
}) => {
  const getStatusConfig = (status) => {
    const configs = {
      draft: {
        bg: 'app-bg-secondary app-text-primary',
        label: 'Draft'
      },
      submitted: {
        bg: 'bg-blue-100 text-blue-800',
        label: 'Submitted'
      },
      under_review: {
        bg: 'bg-yellow-100 text-yellow-800',
        label: 'Under Review'
      },
      approved: {
        bg: 'bg-green-100 text-green-800',
        label: 'Approved'
      },
      rejected: {
        bg: 'bg-red-100 text-red-800',
        label: 'Rejected'
      },
      expired: {
        bg: 'bg-orange-100 text-orange-800',
        label: 'Expired'
      },
      converted: {
        bg: 'bg-purple-100 text-purple-800',
        label: 'Converted'
      },
      cancelled: {
        bg: 'app-bg-secondary app-text-muted',
        label: 'Cancelled'
      }
    };
    return configs[status] || configs.draft;
  };

  const getSizeClasses = (size) => {
    const sizes = {
      xs: 'px-2 py-1 text-xs',
      sm: 'px-2.5 py-1 text-xs',
      md: 'px-3 py-1.5 text-sm',
      lg: 'px-4 py-2 text-base',
      xl: 'px-5 py-2.5 text-lg'
    };
    return sizes[size] || sizes.md;
  };

  const config = getStatusConfig(status);
  const sizeClasses = getSizeClasses(size);

  return (
    <span 
      className={`
        inline-flex items-center rounded-full font-semibold transition-all
        ${config.bg} 
        ${sizeClasses}
        ${className}
      `}
    >
      {config.label}
    </span>
  );
};

export default QuoteStatusBadge;
