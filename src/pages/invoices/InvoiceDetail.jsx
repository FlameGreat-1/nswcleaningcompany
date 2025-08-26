import { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { 
  ArrowLeftIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { useInvoiceDetail } from '../../hooks/useInvoices';
import { useAuth } from '../../hooks/useAuth';
import InvoiceDetails from '../../components/invoices/InvoiceDetails';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { toast } from 'react-hot-toast';

const InvoiceDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  if (!id) {
    navigate('/clients/invoices');
    return null;
  }
  
  const {
    invoice,
    loading,
    error,
    invoiceSummary,
    downloadInvoice
  } = useInvoiceDetail(id);

  if (!downloadInvoice) {
    return (
      <div className="min-h-screen app-bg-primary">
        <div className="container section-padding">
          <div className="text-center py-16">
            <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold app-text-primary mb-2">
              System Error
            </h1>
            <p className="app-text-muted mb-6">
              Unable to initialize invoice system. Please try again.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="btn-md btn-modern-primary"
            >
              Reload Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handleDownloadInvoice = async () => {
    const result = await downloadInvoice();
    if (result.success) {
      toast.success('Invoice downloaded successfully');
    } else {
      toast.error(result.error || 'Failed to download invoice');
    }
  };

  const handleGoBack = () => {
    navigate('/clients/invoices');
  };

  useEffect(() => {
    if (!user?.is_client) {
      navigate('/clients/portal');
      return;
    }
  }, [user, navigate]);

  useEffect(() => {
    if (invoice) {
      document.title = `Invoice ${invoice.invoice_number} - Client Portal`;
    }
  }, [invoice]);

  if (loading) {
    return (
      <div className="min-h-screen app-bg-primary">
        <div className="container section-padding">
          <div className="flex items-center gap-4 mb-8">
            <button
              onClick={handleGoBack}
              className="btn-md btn-modern-secondary"
            >
              <ArrowLeftIcon className="w-4 h-4" />
              <span>Back to Invoices</span>
            </button>
          </div>
          
          <div className="flex items-center justify-center py-16">
            <LoadingSpinner size="lg" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <>
        <Helmet>
          <title>Invoice Not Found - Client Portal</title>
        </Helmet>
        
        <div className="min-h-screen app-bg-primary">
          <div className="container section-padding">
            <div className="flex items-center gap-4 mb-8">
              <button
                onClick={handleGoBack}
                className="btn-md btn-modern-secondary"
              >
                <ArrowLeftIcon className="w-4 h-4" />
                <span>Back to Invoices</span>
              </button>
            </div>

            <div className="text-center py-16">
              <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h1 className="text-2xl font-bold app-text-primary mb-2">
                Invoice Not Found
              </h1>
              <p className="app-text-muted mb-6 max-w-md mx-auto">
                {error || 'The invoice you are looking for could not be found or you do not have permission to view it.'}
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={handleGoBack}
                  className="btn-md btn-modern-primary"
                >
                  <ArrowLeftIcon className="w-4 h-4" />
                  <span>Back to Invoices</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  if (!invoice) {
    return (
      <>
        <Helmet>
          <title>Invoice Not Found - Client Portal</title>
        </Helmet>
        
        <div className="min-h-screen app-bg-primary">
          <div className="container section-padding">
            <div className="flex items-center gap-4 mb-8">
              <button
                onClick={handleGoBack}
                className="btn-md btn-modern-secondary"
              >
                <ArrowLeftIcon className="w-4 h-4" />
                <span>Back to Invoices</span>
              </button>
            </div>

            <div className="text-center py-16">
              <DocumentTextIcon className="w-16 h-16 app-text-muted mx-auto mb-4" />
              <h1 className="text-2xl font-bold app-text-primary mb-2">
                Invoice Not Found
              </h1>
              <p className="app-text-muted mb-6 max-w-md mx-auto">
                The invoice you are looking for does not exist or has been removed.
              </p>
              <button
                onClick={handleGoBack}
                className="btn-md btn-modern-primary"
              >
                <ArrowLeftIcon className="w-4 h-4" />
                <span>Back to Invoices</span>
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Helmet>
        <title>{`Invoice ${invoice.invoice_number} - Client Portal`}</title>
        <meta name="description" content={`View details for invoice ${invoice.invoice_number}`} />
      </Helmet>

      <div className="min-h-screen app-bg-primary">
        <div className="container section-padding">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            <div className="flex items-center gap-4">
              <button
                onClick={handleGoBack}
                className="btn-md btn-modern-secondary"
              >
                <ArrowLeftIcon className="w-4 h-4" />
                <span>Back to Invoices</span>
              </button>
              
              <div className="hidden sm:block w-px h-6 app-border"></div>
              
              <nav className="hidden sm:flex items-center gap-2 text-sm app-text-muted">
                <Link 
                  to="/clients/invoices" 
                  className="hover:app-text-primary transition-colors"
                >
                  My Invoices
                </Link>
                <span>/</span>
                <span className="app-text-primary font-medium">
                  {invoice.invoice_number}
                </span>
              </nav>
            </div>

            {invoice.is_overdue && (
              <div className="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg">
                <ExclamationTriangleIcon className="w-4 h-4 text-red-600" />
                <span className="text-red-800 text-sm font-medium">
                  {invoice.days_overdue} days overdue
                </span>
              </div>
            )}
          </div>

          <div className="animate-fade-in-up">
            <InvoiceDetails
              invoice={invoice}
              loading={false}
              error={null}
              onDownload={handleDownloadInvoice}
            />
          </div>

          {invoice.quote?.id && (
            <div className="mt-8 glass-card animate-fade-in-up delay-200">
              <h3 className="font-semibold app-text-primary mb-3">
                Related Quote
              </h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium app-text-primary">
                    Quote #{invoice.quote.quote_number}
                  </p>
                  <p className="text-sm app-text-muted">
                    Created: {new Date(invoice.quote.created_at).toLocaleDateString('en-AU')}
                  </p>
                </div>
                <Link
                  to={`/clients/quotes/${invoice.quote.id}`}
                  className="btn-sm btn-modern-secondary"
                >
                  View Quote
                </Link>
              </div>
            </div>
          )}

          <div className="mt-8 text-center">
            <p className="app-text-muted text-sm">
              Need help with this invoice? 
              <Link 
                to="/contact" 
                className="app-blue hover:underline ml-1"
              >
                Contact our support team
              </Link>
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default InvoiceDetail;
