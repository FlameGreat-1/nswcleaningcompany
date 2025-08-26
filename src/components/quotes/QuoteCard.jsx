import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useQuoteActions from '../../hooks/useQuoteActions.js';

const QuoteCard = ({ 
  quote, 
  onUpdate, 
  showActions = true, 
  variant = 'default',
  className = '' 
}) => {
  const navigate = useNavigate();
  const [isExpanded, setIsExpanded] = useState(false);
  const { 
    loading, 
    submitQuote, 
    cancelQuote, 
    downloadPDF, 
    duplicateQuote 
  } = useQuoteActions();

  const handleCardClick = (e) => {
    if (e.target.closest('button') || e.target.closest('.expandable-content')) {
      return;
    }
    
    const isInPortal = window.location.pathname.includes('/clients/');
    const prefix = isInPortal ? '/clients' : '';
    navigate(`${prefix}/quotes/${quote.id}`);
  };

  const getStatusConfig = (status) => {
    const configs = {
      draft: {
        bg: 'app-bg-secondary app-text-primary'
      },
      submitted: {
        bg: 'bg-blue-100 text-blue-800'
      },
      under_review: {
        bg: 'bg-yellow-100 text-yellow-800'
      },
      approved: {
        bg: 'bg-green-100 text-green-800'
      },
      rejected: {
        bg: 'bg-red-100 text-red-800'
      },
      expired: {
        bg: 'bg-orange-100 text-orange-800'
      },
      converted: {
        bg: 'bg-purple-100 text-purple-800'
      },
      cancelled: {
        bg: 'app-bg-secondary app-text-muted'
      }
    };
    return configs[status] || configs.draft;
  };

  const getUrgencyConfig = (level) => {
    const configs = {
      1: { color: 'text-green-600', label: 'Flexible' },
      2: { color: 'app-blue', label: 'Standard' },
      3: { color: 'text-yellow-600', label: 'Priority' },
      4: { color: 'text-orange-600', label: 'Urgent' },
      5: { color: 'text-red-600', label: 'Emergency' }
    };
    return configs[level] || configs[2];
  };

  const handleAction = async (actionFn, successMessage) => {
    try {
      await actionFn(quote.id);
      onUpdate?.();
      if (successMessage) {
        console.log(successMessage);
      }
    } catch (error) {
      console.error('Action failed:', error.message);
    }
  };

  const handleDownloadPDF = async (e) => {
    e.stopPropagation();
    try {
      await downloadPDF(quote.id, `quote-${quote.quote_number}.pdf`);
    } catch (error) {
      console.error('PDF download failed:', error.message);
    }
  };

  const handleDuplicate = async (e) => {
    e.stopPropagation();
    try {
      const newQuote = await duplicateQuote(quote.id, {
        status: 'draft'
      });
      onUpdate?.();
      console.log('Quote duplicated successfully');
    } catch (error) {
      console.error('Duplicate failed:', error.message);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const isExpired = quote.expires_at && new Date(quote.expires_at) < new Date();
  const statusConfig = getStatusConfig(quote.status);
  const urgencyConfig = getUrgencyConfig(quote.urgency_level);

  const cardVariants = {
    default: 'theme-card',
    compact: 'theme-card p-4',
    minimal: 'theme-card'
  };

  return (
    <div className={`${cardVariants[variant]} ${className} ${isExpired ? 'opacity-75' : ''} relative cursor-pointer`} onClick={handleCardClick}>
      {isExpired && (
        <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
          Expired
        </div>
      )}

      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <h3 className="text-lg font-bold app-text-primary">
              {quote.quote_number}
            </h3>
            {quote.is_ndis_client && (
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                NDIS
              </span>
            )}
            {quote.deposit_required && (
              <span className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">
                Deposit: {formatCurrency(quote.deposit_amount)}
              </span>
            )}
          </div>
          <p className="app-text-secondary text-sm font-medium">
            {quote.cleaning_type.replace('_', ' ').toUpperCase()}
          </p>
        </div>

        <div className="flex flex-col items-end gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusConfig.bg}`}>
            {quote.status.replace('_', ' ').toUpperCase()}
          </span>
          <span className={`text-xs ${urgencyConfig.color} font-medium`}>
            {urgencyConfig.label}
          </span>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex items-start gap-2">
          <div className="flex-1">
            <p className="app-text-primary text-sm font-medium">
              {quote.property_address}
            </p>
            <p className="app-text-muted text-xs">
              {quote.suburb}, {quote.state} {quote.postcode}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="app-text-secondary font-medium">
              Rooms: {quote.number_of_rooms}
            </span>
          </div>
          {quote.square_meters && (
            <div className="flex items-center gap-2">
              <span className="app-text-secondary font-medium">
                Area: {quote.square_meters}m²
              </span>
            </div>
          )}
        </div>

        <div className="flex justify-between items-center pt-2 border-t app-border">
          <div className="text-sm app-text-muted">
            Created: {formatDate(quote.created_at)}
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold app-text-primary">
              {formatCurrency(quote.final_price)}
            </div>
            {quote.estimated_total !== quote.final_price && (
              <div className="text-xs app-text-muted line-through">
                {formatCurrency(quote.estimated_total)}
              </div>
            )}
          </div>
        </div>

        {quote.deposit_required && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold text-orange-800">
                  Deposit Required
                </div>
                <div className="text-xs text-orange-600">
                  {quote.deposit_percentage}% of total price
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-orange-800">
                  {formatCurrency(quote.deposit_amount)}
                </div>
                <div className="text-xs text-orange-600">
                  Due before service
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {quote.special_requirements && (
        <div className="mb-4 expandable-content">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="text-xs app-text-muted hover:app-text-primary font-medium transition-colors"
          >
            {isExpanded ? '▼' : '▶'} Special Requirements
          </button>
          {isExpanded && (
            <p className="text-xs app-text-secondary mt-2 p-2 app-bg-secondary rounded">
              {quote.special_requirements}
            </p>
          )}
        </div>
      )}

      {showActions && (
        <div className="flex flex-wrap gap-2 expandable-content">
          {quote.status === 'draft' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleAction(submitQuote, 'Quote submitted successfully');
              }}
              disabled={loading}
              className="px-3 py-1 theme-button text-xs disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Submitting...' : 'Submit'}
            </button>
          )}

          {quote.status === 'approved' && !isExpired && (
            <button
              onClick={handleDownloadPDF}
              disabled={loading}
              className="px-3 py-1 bg-transparent border-2 app-border-blue app-text-primary rounded-full text-xs font-medium transition-all hover:app-bg-blue hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Downloading...' : 'Download PDF'}
            </button>
          )}

          {['draft', 'submitted'].includes(quote.status) && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleAction(cancelQuote, 'Quote cancelled successfully');
              }}
              disabled={loading}
              className="px-3 py-1 bg-red-100 text-red-800 hover:bg-red-200 rounded-full text-xs font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Cancelling...' : 'Cancel'}
            </button>
          )}

          <button
            onClick={handleDuplicate}
            disabled={loading}
            className="px-3 py-1 app-bg-secondary app-text-primary hover:opacity-80 rounded-full text-xs font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Duplicating...' : 'Duplicate'}
          </button>

          {quote.preferred_date && (
            <div className="text-xs app-text-muted flex items-center gap-1 px-2 py-1">
              Preferred: {formatDate(quote.preferred_date)}
              {quote.preferred_time && (
                <span>at {quote.preferred_time}</span>
              )}
            </div>
          )}
        </div>
      )}

      {quote.expires_at && quote.status === 'approved' && (
        <div className="mt-3 text-xs app-text-muted flex items-center gap-1">
          Expires: {formatDate(quote.expires_at)}
        </div>
      )}
    </div>
  );
};

export default QuoteCard;
