import { memo } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  DocumentArrowDownIcon, 
  CalendarIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import NDISInvoiceBadge from './NDISInvoiceBadge';
import invoicesService from '../../services/invoicesService';

const InvoiceCard = memo(({ 
  invoice, 
  onDownload, 
  onInvoiceClick,
  className = '' 
}) => {
  const navigate = useNavigate();
  const summary = invoicesService.getInvoiceSummary(invoice);

  const handleCardClick = (e) => {
    if (e.target.closest('button')) {
      return;
    }
    
    if (onInvoiceClick) {
      onInvoiceClick(invoice.id);
    } else {
      const isInPortal = window.location.pathname.includes('/clients/');
      const prefix = isInPortal ? '/clients' : '';
      navigate(`${prefix}/invoices/${invoice.id}`);
    }
  };
  
  const handleDownload = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (onDownload && summary.canDownload) {
      await onDownload(invoice.id);
    }
  };

  const formatServicePeriod = () => {
    const period = invoicesService.getServicePeriod(invoice);
    return period || 'N/A';
  };

  return (
    <div 
      className={`card-modern group cursor-pointer ${className}`}
      onClick={handleCardClick}
    >
      <div className="block">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-bold app-text-primary">
                {invoice.invoice_number}
              </h3>
              {summary.isNDIS && <NDISInvoiceBadge />}
            </div>
            
            <p className="app-text-secondary text-sm font-medium">
              {summary.clientName}
            </p>
          </div>

          <div className="text-right">
            <p className="text-xl font-black text-gradient">
              {summary.totalAmount}
            </p>
            {summary.isOverdue && (
              <div className="flex items-center gap-1 text-red-600 text-xs mt-1">
                <ExclamationTriangleIcon className="w-3 h-3" />
                <span>{summary.daysOverdue} days overdue</span>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-2 app-text-muted text-sm">
            <CalendarIcon className="w-4 h-4" />
            <span>Due: {summary.dueDate}</span>
          </div>
          
          <div className="flex items-center gap-2 app-text-muted text-sm">
            <CurrencyDollarIcon className="w-4 h-4" />
            <span>Service: {formatServicePeriod()}</span>
          </div>
        </div>

        {summary.isNDIS && (
          <div className="mb-4 p-3 app-bg-secondary rounded-lg">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs app-text-secondary">
              <div>
                <span className="font-medium">Participant:</span>
                <span className="ml-1">{invoice.participant_name || 'N/A'}</span>
              </div>
              <div>
                <span className="font-medium">NDIS:</span>
                <span className="ml-1">{invoice.ndis_number || 'N/A'}</span>
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center justify-end pt-4 border-t app-border">
          {summary.canDownload && (
            <button
              onClick={handleDownload}
              className="btn-xs btn-modern-secondary opacity-0 group-hover:opacity-100 transition-opacity duration-300"
              title="Download PDF"
            >
              <DocumentArrowDownIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
});

InvoiceCard.displayName = 'InvoiceCard';

export default InvoiceCard;
