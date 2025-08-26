import { useState, useEffect, useMemo } from 'react';
import { Helmet } from 'react-helmet-async';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { 
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline';
import { useInvoices } from '../../hooks/useInvoices';
import { useAuth } from '../../hooks/useAuth';
import InvoicesList from '../../components/invoices/InvoicesList';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const MyInvoices = () => {
  const { user } = useAuth();
  const [selectedTab, setSelectedTab] = useState('all');
  const navigate = useNavigate();

  const {
    invoices,
    loading,
    error,
    filters,
    invoiceStats,
    overdueInvoices,
    hasOverdueInvoices,
    hasPendingDeposits,
    pendingDepositInvoices,
    updateFilters,
    downloadInvoice,
    refreshInvoices
  } = useInvoices({
    ordering: '-created_at'
  });
  
  if (!invoiceStats) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold app-text-primary mb-2">
            Failed to Load Invoice Data
          </h3>
          <p className="app-text-muted mb-4">Unable to initialize invoice system</p>
          <button onClick={() => window.location.reload()} className="btn-md btn-modern-primary">
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'all', label: 'All Invoices', count: invoiceStats?.total || 0 },
    { id: 'ndis', label: 'NDIS Invoices', count: invoiceStats?.ndis || 0 },
    { id: 'deposits', label: 'Deposits Required', count: invoiceStats?.depositsRequired || 0 },
    { id: 'overdue', label: 'Overdue', count: invoiceStats?.overdue || 0 }
  ];

  const handleTabChange = (tabId) => {
    setSelectedTab(tabId);
    if (tabId === 'ndis') {
      updateFilters({ 
        ...filters, 
        is_ndis_invoice: true,
        deposit_required: null,
        deposit_paid: null,
        overdue_only: false
      });
    } else if (tabId === 'deposits') {
      updateFilters({ 
        ...filters, 
        is_ndis_invoice: null,
        deposit_required: true,
        deposit_paid: null,
        overdue_only: false
      });
    } else if (tabId === 'overdue') {
      updateFilters({ 
        ...filters, 
        is_ndis_invoice: null,
        deposit_required: null,
        deposit_paid: null,
        overdue_only: true 
      });
    } else {
      updateFilters({ 
        ...filters, 
        is_ndis_invoice: null,
        deposit_required: null,
        deposit_paid: null,
        overdue_only: false 
      });
    }
  };

  const handleDownloadInvoice = async (invoiceId) => {
    const result = await downloadInvoice(invoiceId);
    if (result.success) {
      toast.success('Invoice downloaded successfully');
    } else {
      toast.error(result.error || 'Failed to download invoice');
    }
  };

  const handleFiltersChange = (newFilters) => {
    updateFilters(newFilters);
  };

  const handleInvoiceClick = (invoiceId) => {
    const isInPortal = window.location.pathname.includes('/clients/');
    const prefix = isInPortal ? '/clients' : '';
    navigate(`${prefix}/invoices/${invoiceId}`);
  };  

  const statsCards = useMemo(() => {
    const safeStats = {
      total: invoiceStats?.total || 0,
      totalAmount: invoiceStats?.totalAmount || 0,
      overdueAmount: invoiceStats?.overdueAmount || 0,
      ndis: invoiceStats?.ndis || 0,
      depositsRequired: invoiceStats?.depositsRequired || 0,
      totalDepositAmount: invoiceStats?.totalDepositAmount || 0
    };
  
    return [
      {
        title: 'Total Invoices',
        value: safeStats.total,
        icon: DocumentTextIcon,
        color: 'blue',
        bgColor: 'bg-blue-50',
        textColor: 'text-blue-600',
        borderColor: 'border-blue-200'
      },
      {
        title: 'Total Amount',
        value: new Intl.NumberFormat('en-AU', {
          style: 'currency',
          currency: 'AUD'
        }).format(safeStats.totalAmount),
        icon: CurrencyDollarIcon,
        color: 'green',
        bgColor: 'bg-green-50',
        textColor: 'text-green-600',
        borderColor: 'border-green-200'
      },
      {
        title: 'Deposits Required',
        value: new Intl.NumberFormat('en-AU', {
          style: 'currency',
          currency: 'AUD'
        }).format(safeStats.totalDepositAmount),
        icon: BanknotesIcon,
        color: 'orange',
        bgColor: 'bg-orange-50',
        textColor: 'text-orange-600',
        borderColor: 'border-orange-200'
      },
      {
        title: 'Overdue Amount',
        value: new Intl.NumberFormat('en-AU', {
          style: 'currency',
          currency: 'AUD'
        }).format(safeStats.overdueAmount),
        icon: ExclamationTriangleIcon,
        color: 'red',
        bgColor: 'bg-red-50',
        textColor: 'text-red-600',
        borderColor: 'border-red-200'
      }
    ];
  }, [invoiceStats]);

  useEffect(() => {
    document.title = 'My Invoices - Client Portal';
  }, []);

  if (loading && invoices.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>My Invoices - Client Portal</title>
        <meta name="description" content="View and manage your invoices" />
      </Helmet>

      <div className="min-h-screen app-bg-primary">
        <div className="container section-padding">
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <div>
                <h1 className="text-3xl font-black text-gradient mb-2">
                  My Invoices
                </h1>
                <p className="app-text-secondary">
                  View and manage your invoices
                </p>
              </div>
              
              <button
                onClick={refreshInvoices}
                disabled={loading}
                className="btn-md btn-modern-secondary"
              >
                {loading ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <ClockIcon className="w-4 h-4" />
                )}
                <span>Refresh</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {statsCards.map((stat, index) => (
                <div
                  key={stat.title}
                  className={`
                    ${stat.bgColor} ${stat.borderColor} border rounded-xl p-4
                    animate-fade-in-up delay-${index * 100}
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className={`text-sm font-medium ${stat.textColor}`}>
                        {stat.title}
                      </p>
                      <p className={`text-2xl font-bold ${stat.textColor} mt-1`}>
                        {stat.value}
                      </p>
                    </div>
                    <stat.icon className={`w-8 h-8 ${stat.textColor}`} />
                  </div>
                </div>
              ))}
            </div>

            {hasOverdueInvoices && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 animate-fade-in-up">
                <div className="flex items-start gap-3">
                  <ExclamationTriangleIcon className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-red-800 mb-1">
                      Attention Required
                    </h3>
                    <p className="text-red-700 text-sm mb-2">
                      You have {overdueInvoices.length} overdue invoice{overdueInvoices.length !== 1 ? 's' : ''} 
                      totaling {new Intl.NumberFormat('en-AU', {
                        style: 'currency',
                        currency: 'AUD'
                      }).format(invoiceStats.overdueAmount)}.
                    </p>
                    <button
                      onClick={() => handleTabChange('overdue')}
                      className="text-red-800 text-sm font-medium hover:text-red-900 underline"
                    >
                      View overdue invoices →
                    </button>
                  </div>
                </div>
              </div>
            )}

            {hasPendingDeposits && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6 animate-fade-in-up">
                <div className="flex items-start gap-3">
                  <BanknotesIcon className="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-orange-800 mb-1">
                      Deposits Required
                    </h3>
                    <p className="text-orange-700 text-sm mb-2">
                      You have {pendingDepositInvoices.length} invoice{pendingDepositInvoices.length !== 1 ? 's' : ''} 
                      requiring deposits totaling {new Intl.NumberFormat('en-AU', {
                        style: 'currency',
                        currency: 'AUD'
                      }).format(invoiceStats.totalDepositAmount)}.
                    </p>
                    <button
                      onClick={() => handleTabChange('deposits')}
                      className="text-orange-800 text-sm font-medium hover:text-orange-900 underline"
                    >
                      View deposit invoices →
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="glass-card mb-6">
              <div className="flex flex-wrap gap-1 p-1 app-bg-secondary rounded-lg">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => handleTabChange(tab.id)}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200
                      ${selectedTab === tab.id
                        ? 'app-bg-card app-text-primary shadow-sm'
                        : 'app-text-secondary hover:app-text-primary hover:app-bg-card/50'
                      }
                    `}
                  >
                    <span>{tab.label}</span>
                    {tab.count > 0 && (
                      <span className={`
                        px-2 py-0.5 rounded-full text-xs font-bold
                        ${selectedTab === tab.id
                          ? 'bg-blue-100 text-blue-800'
                          : 'app-bg-secondary app-text-muted'
                        }
                      `}>
                        {tab.count}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-2">
                <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
                <h3 className="font-semibold text-red-800">Error Loading Invoices</h3>
              </div>
              <p className="text-red-700 text-sm mt-1">{error}</p>
              <button
                onClick={refreshInvoices}
                className="mt-3 btn-sm btn-modern-secondary text-red-600 border-red-300 hover:bg-red-50"
              >
                Try Again
              </button>
            </div>
          )}

          <InvoicesList
            invoices={invoices}
            loading={loading}
            error={null}
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onDownloadInvoice={handleDownloadInvoice}
            onInvoiceClick={handleInvoiceClick}
            className="animate-fade-in-up delay-300"
          />

          {invoices.length === 0 && !loading && !error && (
            <div className="text-center py-16">
              <DocumentTextIcon className="w-16 h-16 app-text-muted mx-auto mb-4" />
              <h3 className="text-xl font-bold app-text-primary mb-2">
                No Invoices Yet
              </h3>
              <p className="app-text-muted mb-6 max-w-md mx-auto">
                Your invoices will appear here once they are created from approved quotes. 
                Contact us if you have any questions.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={refreshInvoices}
                  className="btn-md btn-modern-secondary"
                >
                  <ClockIcon className="w-4 h-4" />
                  <span>Refresh</span>
                </button>
              </div>
            </div>
          )}

          {user?.is_ndis_client && invoiceStats.ndis > 0 && (
            <div className="mt-8 glass-card">
              <div className="flex items-center gap-3 mb-4">
                <ShieldCheckIcon className="w-6 h-6 text-blue-600" />
                <h2 className="text-lg font-bold app-text-primary">
                  NDIS Invoice Summary
                </h2>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="text-center p-4 app-bg-secondary rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">
                    {invoiceStats.ndis}
                  </p>
                  <p className="text-sm app-text-muted">NDIS Invoices</p>
                </div>
                
                <div className="text-center p-4 app-bg-secondary rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                  {invoiceStats?.total > 0 ? Math.round((invoiceStats.ndis / invoiceStats.total) * 100) : 0}%
                  </p>
                  <p className="text-sm app-text-muted">of Total Invoices</p>
                </div>
                
                <div className="text-center p-4 app-bg-secondary rounded-lg">
                  <p className="text-2xl font-bold app-blue">
                    {invoiceStats.total - invoiceStats.ndis}
                  </p>
                  <p className="text-sm app-text-muted">Regular Invoices</p>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-blue-800 text-sm">
                  <strong>NDIS Compliance:</strong> All your NDIS invoices include participant details 
                  and service information as required by NDIS guidelines.
                </p>
              </div>
            </div>
          )}

          {invoiceStats.depositsRequired > 0 && (
            <div className="mt-8 glass-card">
              <div className="flex items-center gap-3 mb-4">
                <BanknotesIcon className="w-6 h-6 text-orange-600" />
                <h2 className="text-lg font-bold app-text-primary">
                  Deposit Summary
                </h2>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="text-center p-4 app-bg-secondary rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">
                    {invoiceStats.depositsRequired}
                  </p>
                  <p className="text-sm app-text-muted">Deposits Required</p>
                </div>
                
                <div className="text-center p-4 app-bg-secondary rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {invoiceStats.depositsPaid}
                  </p>
                  <p className="text-sm app-text-muted">Deposits Paid</p>
                </div>
                
                <div className="text-center p-4 app-bg-secondary rounded-lg">
                  <p className="text-2xl font-bold text-yellow-600">
                    {invoiceStats.depositsPending}
                  </p>
                  <p className="text-sm app-text-muted">Deposits Pending</p>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <p className="text-orange-800 text-sm">
                  <strong>Deposit Information:</strong> Deposits are required for high-priority services 
                  and must be paid before service commencement.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default MyInvoices;
