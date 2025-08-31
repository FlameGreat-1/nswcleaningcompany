import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext.jsx';
import quotesService from '../../services/quotesService.js';
import useQuoteActions from '../../hooks/useQuoteActions.js';
import QuoteStatusBadge from '../../components/quotes/QuoteStatusBadge.jsx';
import SEO from '../../components/common/SEO.jsx';

const QuoteDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [showFullAddress, setShowFullAddress] = useState(false);
  const [activeTab, setActiveTab] = useState('details');

  const {
    submitQuote,
    cancelQuote,
    downloadPDF,
    duplicateQuote,
    loading: actionLoading,
    error: actionError
  } = useQuoteActions();

  const { 
    data: quote, 
    isLoading: quoteLoading, 
    error: quoteError,
    refetch: refetchQuote
  } = useQuery({
    queryKey: ['quote', id],
    queryFn: () => quotesService.getQuote(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const { 
    data: quoteItems = [],
    isLoading: itemsLoading
  } = useQuery({
    queryKey: ['quote-items', id],
    queryFn: () => quotesService.getQuoteItems(id).then(res => res.results || res),
    enabled: activeTab === 'items' && !!quote,
    staleTime: 5 * 60 * 1000,
  });

  const { 
    data: quoteAddons = [],
    isLoading: addonsLoading
  } = useQuery({
    queryKey: ['quote-addons', id],
    queryFn: () => quotesService.getQuoteAddons(id).then(res => res.results || res),
    enabled: activeTab === 'addons' && !!quote,
    staleTime: 5 * 60 * 1000,
  });

  const { 
    data: quoteAttachments = [],
    isLoading: attachmentsLoading
  } = useQuery({
    queryKey: ['quote-attachments', id],
    queryFn: () => quotesService.getQuoteAttachments(id).then(res => res.results || res),
    enabled: activeTab === 'attachments' && !!quote,
    staleTime: 5 * 60 * 1000,
  });

  const { 
    data: quoteRevisions = [],
    isLoading: revisionsLoading
  } = useQuery({
    queryKey: ['quote-revisions', id],
    queryFn: () => quotesService.getQuoteRevisions(id).then(res => res.results || res),
    enabled: activeTab === 'history' && !!quote,
    staleTime: 5 * 60 * 1000,
  });

  const tabs = [
    { key: 'details', label: 'Quote Details' },
    { key: 'items', label: 'Items' },
    { key: 'addons', label: 'Add-ons' },
    { key: 'attachments', label: 'Attachments' },
    { key: 'history', label: 'History' }
  ];

  const handleAction = async (actionFn, successMessage) => {
    try {
      await actionFn(quote.id);
      refetchQuote();
      console.log(successMessage);
    } catch (err) {
      console.error('Action failed:', err.message);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      await downloadPDF(quote.id, `quote-${quote.quote_number}.pdf`);
    } catch (err) {
      console.error('PDF download failed:', err.message);
    }
  };

  const handleDuplicate = async () => {
    try {
      const newQuote = await duplicateQuote(quote.id, { status: 'draft' });
      console.log('New quote:', newQuote); 
      
      const isInPortal = window.location.pathname.includes('/clients/');
      const prefix = isInPortal ? '/clients' : '';
      
      if (newQuote && newQuote.id) {
        navigate(`${prefix}/quotes/${newQuote.id}`);
      } else {
        console.error('Invalid response from duplicate quote:', newQuote);
        navigate(`${prefix}/quotes`);
      }
    } catch (err) {
      console.error('Duplicate failed:', err.message);
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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDateOnly = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getUrgencyConfig = (level) => {
    const configs = {
      1: { color: 'text-green-600', label: 'Flexible', bg: 'bg-green-100' },
      2: { color: 'app-blue', label: 'Standard', bg: 'bg-blue-100' },
      3: { color: 'text-yellow-600', label: 'Priority', bg: 'bg-yellow-100' },
      4: { color: 'text-orange-600', label: 'Urgent', bg: 'bg-orange-100' },
      5: { color: 'text-red-600', label: 'Emergency', bg: 'bg-red-100' }
    };
    return configs[level] || configs[2];
  };

  const canEdit = () => {
    if (!quote || !user) return false;
    
    const editableStatuses = ['draft', 'rejected'];
    const isOwner = user.id === quote.client?.id || user.id === quote.client;
    const isStaff = user.is_staff;
    
    return editableStatuses.includes(quote.status) && (isOwner || isStaff);
  };
  
  const canSubmit = () => {
    return quote && quote.status === 'draft' && user?.id === quote.client;
  };

  const canCancel = () => {
    return quote && ['draft', 'submitted'].includes(quote.status) && 
           (user?.id === quote.client || user?.is_staff);
  };

  const canDownloadPDF = () => {
    return quote && quote.status === 'approved';
  };

  const isExpired = quote?.expires_at && new Date(quote.expires_at) < new Date();
  const urgencyConfig = quote ? getUrgencyConfig(quote.urgency_level) : null;

  if (quoteLoading) {
    return (
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center min-h-96">
          <div className="w-8 h-8 border-4 app-border rounded-full border-t-transparent animate-spin"></div>
        </div>
      </div>
    );
  }

  if (quoteError || !quote) {
    return (
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="theme-card text-center py-12">
          <div className="text-red-600 mb-4">
            <h3 className="text-lg font-semibold mb-2">Quote Not Found</h3>
            <p className="app-text-muted">{quoteError?.message || 'The requested quote could not be found.'}</p>
          </div>
          <div className="flex gap-4 justify-center">
            <button onClick={refetchQuote} className="theme-button">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO 
        title={`Quote ${quote.quote_number}`}
        description={`Quote details for ${quote.cleaning_type} cleaning service`}
      />
      
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
            <div>
              <div className="flex items-center gap-4 mb-2">
                <h1 className="text-3xl font-black app-text-primary">
                  {quote.quote_number}
                </h1>
                <QuoteStatusBadge status={quote.status} size="lg" />
                {isExpired && (
                  <span className="bg-red-500 text-white text-sm px-3 py-1 rounded-full">
                    Expired
                  </span>
                )}
              </div>
              <p className="app-text-secondary text-lg font-medium">
                {quote.cleaning_type.replace('_', ' ').toUpperCase()} Cleaning
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {quote.is_ndis_client && (
                  <span className="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                    NDIS Client
                  </span>
                )}
                {quote.deposit_required && (
                  <span className="inline-block bg-orange-100 text-orange-800 text-sm px-3 py-1 rounded-full">
                    Deposit Required: {formatCurrency(quote.deposit_amount)} ({quote.deposit_percentage}%)
                  </span>
                )}
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              {canEdit() && (
                <Link
                  to={`/clients/quotes/${quote.id}/edit`}
                  className="px-6 py-3 bg-transparent border-2 app-border-blue app-text-primary rounded-full font-medium transition-all hover:app-bg-blue hover:text-white"
                >
                  Edit Quote
                </Link>
              )}

              {canSubmit() && (
                <button
                  onClick={() => handleAction(submitQuote, 'Quote submitted successfully')}
                  disabled={actionLoading}
                  className="theme-button"
                >
                  {actionLoading ? (
                    <div className="w-4 h-4 border-2 border-white rounded-full border-t-transparent animate-spin"></div>
                  ) : 'Submit Quote'}
                </button>
              )}

              {canDownloadPDF() && (
                <button
                  onClick={handleDownloadPDF}
                  disabled={actionLoading}
                  className="theme-button"
                >
                  {actionLoading ? (
                    <div className="w-4 h-4 border-2 border-white rounded-full border-t-transparent animate-spin"></div>
                  ) : 'Download PDF'}
                </button>
              )}

              <button
                onClick={handleDuplicate}
                disabled={actionLoading}
                className="px-6 py-3 bg-transparent border-2 app-border-blue app-text-primary rounded-full font-medium transition-all hover:app-bg-blue hover:text-white"
              >
                {actionLoading ? (
                  <div className="w-4 h-4 border-2 app-border rounded-full border-t-transparent animate-spin"></div>
                ) : 'Duplicate'}
              </button>

              {canCancel() && (
                <button
                  onClick={() => handleAction(cancelQuote, 'Quote cancelled successfully')}
                  disabled={actionLoading}
                  className="bg-red-100 text-red-800 hover:bg-red-200 rounded-full px-4 py-2 text-sm font-medium transition-all"
                >
                  {actionLoading ? (
                    <div className="w-4 h-4 border-2 border-red-800 rounded-full border-t-transparent animate-spin"></div>
                  ) : 'Cancel Quote'}
                </button>
              )}
            </div>
          </div>

          {actionError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              <p className="text-sm">{actionError}</p>
            </div>
          )}

          <div className="theme-card mb-6">
            <div className="flex flex-wrap gap-2">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`
                    px-4 py-2 rounded-full text-sm font-medium transition-all
                    ${activeTab === tab.key
                      ? 'app-bg-blue text-white'
                      : 'app-bg-secondary app-text-primary hover:app-bg-blue hover:text-white'
                    }
                  `}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {quote.deposit_required && quote.status === 'approved' && (
            <div className="theme-card mb-6 border-l-4 border-orange-500">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                    <span className="text-orange-600 font-bold">$</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-orange-800">Deposit Required</h3>
                    <p className="text-sm text-orange-600">Payment required before work begins</p>
                  </div>
                </div>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-800">{formatCurrency(quote.deposit_amount)}</div>
                    <div className="text-sm text-orange-600">Deposit Amount</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-800">{quote.deposit_percentage}%</div>
                    <div className="text-sm text-orange-600">Of Total Price</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-800">{urgencyConfig?.label}</div>
                    <div className="text-sm text-orange-600">Urgency Level</div>
                  </div>
                </div>
                <div className="mt-4 p-4 bg-orange-50 rounded-lg">
                  <p className="text-sm text-orange-700">
                    <strong>Payment Instructions:</strong> Please contact us to arrange deposit payment before your scheduled service date.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
        <div>
          {activeTab === 'details' && (
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <div className="theme-card">
                  <h3 className="text-xl font-bold app-text-primary mb-4">Property Information</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold app-text-secondary mb-1">
                        Property Address
                      </label>
                      <div className="app-text-primary">
                        {showFullAddress ? (
                          <div>
                            <p>{quote.property_address}</p>
                            <p>{quote.suburb}, {quote.state} {quote.postcode}</p>
                            <button
                              onClick={() => setShowFullAddress(false)}
                              className="app-blue text-sm hover:underline mt-1"
                            >
                              Show less
                            </button>
                          </div>
                        ) : (
                          <div>
                            <p>{quote.property_address.length > 50 
                              ? `${quote.property_address.substring(0, 50)}...` 
                              : quote.property_address}
                            </p>
                            <p>{quote.suburb}, {quote.state} {quote.postcode}</p>
                            {quote.property_address.length > 50 && (
                              <button
                                onClick={() => setShowFullAddress(true)}
                                className="app-blue text-sm hover:underline mt-1"
                              >
                                Show more
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold app-text-secondary mb-1">
                          Number of Rooms
                        </label>
                        <p className="app-text-primary font-medium">{quote.number_of_rooms}</p>
                      </div>

                      {quote.square_meters && (
                        <div>
                          <label className="block text-sm font-semibold app-text-secondary mb-1">
                            Square Meters
                          </label>
                          <p className="app-text-primary font-medium">{quote.square_meters}m²</p>
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-semibold app-text-secondary mb-1">
                        Urgency Level
                      </label>
                      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${urgencyConfig.bg} ${urgencyConfig.color}`}>
                        {urgencyConfig.label}
                      </span>
                    </div>

                    {(quote.preferred_date || quote.preferred_time) && (
                      <div className="grid md:grid-cols-2 gap-4">
                        {quote.preferred_date && (
                          <div>
                            <label className="block text-sm font-semibold app-text-secondary mb-1">
                              Preferred Date
                            </label>
                            <p className="app-text-primary font-medium">{formatDateOnly(quote.preferred_date)}</p>
                          </div>
                        )}

                        {quote.preferred_time && (
                          <div>
                            <label className="block text-sm font-semibold app-text-secondary mb-1">
                              Preferred Time
                            </label>
                            <p className="app-text-primary font-medium">{quote.preferred_time}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {(quote.special_requirements || quote.access_instructions) && (
                  <div className="theme-card">
                    <h3 className="text-xl font-bold app-text-primary mb-4">Additional Information</h3>
                    <div className="space-y-4">
                      {quote.special_requirements && (
                        <div>
                          <label className="block text-sm font-semibold app-text-secondary mb-2">
                            Special Requirements
                          </label>
                          <p className="app-text-primary app-bg-secondary p-3 rounded-lg">
                            {quote.special_requirements}
                          </p>
                        </div>
                      )}

                      {quote.access_instructions && (
                        <div>
                          <label className="block text-sm font-semibold app-text-secondary mb-2">
                            Access Instructions
                          </label>
                          <p className="app-text-primary app-bg-secondary p-3 rounded-lg">
                            {quote.access_instructions}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {quote.is_ndis_client && (
                  <div className="theme-card">
                    <h3 className="text-xl font-bold app-text-primary mb-4">NDIS Information</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-semibold app-text-secondary mb-1">
                          Participant Number
                        </label>
                        <p className="app-text-primary font-medium">{quote.ndis_participant_number}</p>
                      </div>

                      {(quote.plan_manager_name || quote.support_coordinator_name) && (
                        <div className="grid md:grid-cols-2 gap-4">
                          {quote.plan_manager_name && (
                            <div>
                              <label className="block text-sm font-semibold app-text-secondary mb-1">
                                Plan Manager
                              </label>
                              <p className="app-text-primary">{quote.plan_manager_name}</p>
                              {quote.plan_manager_contact && (
                                <p className="app-text-muted text-sm">{quote.plan_manager_contact}</p>
                              )}
                            </div>
                          )}

                          {quote.support_coordinator_name && (
                            <div>
                              <label className="block text-sm font-semibold app-text-secondary mb-1">
                                Support Coordinator
                              </label>
                              <p className="app-text-primary">{quote.support_coordinator_name}</p>
                              {quote.support_coordinator_contact && (
                                <p className="app-text-muted text-sm">{quote.support_coordinator_contact}</p>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-6">
                <div className="theme-card">
                  <h3 className="text-xl font-bold app-text-primary mb-4">Pricing Breakdown</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="app-text-secondary">Base Price:</span>
                      <span className="font-medium">{formatCurrency(quote.base_price)}</span>
                    </div>

                    {quote.extras_cost > 0 && (
                      <div className="flex justify-between">
                        <span className="app-text-secondary">Extras:</span>
                        <span className="font-medium">{formatCurrency(quote.extras_cost)}</span>
                      </div>
                    )}

                    {quote.travel_cost > 0 && (
                      <div className="flex justify-between">
                        <span className="app-text-secondary">Travel Cost:</span>
                        <span className="font-medium">{formatCurrency(quote.travel_cost)}</span>
                      </div>
                    )}

                    {quote.urgency_surcharge > 0 && (
                      <div className="flex justify-between">
                        <span className="app-text-secondary">Urgency Downpayment:</span>
                        <span className="font-medium">{formatCurrency(quote.urgency_surcharge)}</span>
                      </div>
                    )}

                    <div className="flex justify-between">
                      <span className="app-text-secondary">GST:</span>
                      <span className="font-medium">{formatCurrency(quote.gst_amount)}</span>
                    </div>

                    <hr className="app-border" />
                    
                    <div className="flex justify-between text-lg font-bold">
                      <span className="app-text-primary">Total:</span>
                      <span className="app-text-primary">{formatCurrency(quote.final_price)}</span>
                    </div>

                    {quote.deposit_required && (
                      <>
                        <hr className="app-border" />
                        <div className="bg-orange-50 p-4 rounded-lg">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-orange-800 font-semibold">Deposit Required:</span>
                            <span className="text-orange-800 font-bold text-lg">{formatCurrency(quote.deposit_amount)}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-orange-600">Percentage of total:</span>
                            <span className="text-orange-600 font-medium">{quote.deposit_percentage}%</span>
                          </div>
                          <div className="mt-3 text-xs text-orange-700">
                            <p><strong>Note:</strong> Deposit payment is required before work begins due to the {urgencyConfig?.label.toLowerCase()} nature of this booking.</p>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                <div className="theme-card">
                  <h3 className="text-xl font-bold app-text-primary mb-4">Quote Timeline</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="app-text-secondary">Created:</span>
                      <span className="font-medium">{formatDate(quote.created_at)}</span>
                    </div>

                    {quote.submitted_at && (
                      <div className="flex justify-between">
                        <span className="app-text-secondary">Submitted:</span>
                        <span className="font-medium">{formatDate(quote.submitted_at)}</span>
                      </div>
                    )}

                    {quote.approved_at && (
                      <div className="flex justify-between">
                        <span className="app-text-secondary">Approved:</span>
                        <span className="font-medium">{formatDate(quote.approved_at)}</span>
                      </div>
                    )}

                    {quote.expires_at && (
                      <div className="flex justify-between">
                        <span className="app-text-secondary">Expires:</span>
                        <span className={`font-medium ${isExpired ? 'text-red-600' : ''}`}>
                          {formatDate(quote.expires_at)}
                        </span>
                      </div>
                    )}

                    <div className="flex justify-between">
                      <span className="app-text-secondary">Last Updated:</span>
                      <span className="font-medium">{formatDate(quote.updated_at)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
                    {activeTab === 'items' && (
            <div className="theme-card">
              <h3 className="text-xl font-bold app-text-primary mb-4">Quote Items</h3>
              {itemsLoading ? (
                <div className="flex justify-center py-8">
                  <div className="w-6 h-6 border-2 app-border rounded-full border-t-transparent animate-spin"></div>
                </div>
              ) : quoteItems.length === 0 ? (
                <p className="app-text-muted text-center py-8">No items found for this quote.</p>
              ) : (
                <div className="space-y-4">
                  {quoteItems.map((item, index) => (
                    <div key={item.id || index} className="border app-border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold app-text-primary">{item.description}</h4>
                          <p className="app-text-muted text-sm">Quantity: {item.quantity}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{formatCurrency(item.unit_price)}</p>
                          <p className="text-sm app-text-muted">per unit</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'addons' && (
            <div className="theme-card">
              <h3 className="text-xl font-bold app-text-primary mb-4">Quote Add-ons</h3>
              {addonsLoading ? (
                <div className="flex justify-center py-8">
                  <div className="w-6 h-6 border-2 app-border rounded-full border-t-transparent animate-spin"></div>
                </div>
              ) : quoteAddons.length === 0 ? (
                <p className="app-text-muted text-center py-8">No add-ons found for this quote.</p>
              ) : (
                <div className="grid md:grid-cols-2 gap-4">
                  {quoteAddons.map((addon, index) => (
                    <div key={addon.id || index} className="border app-border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-semibold app-text-primary">{addon.name}</h4>
                          <p className="app-text-muted text-sm">{addon.description}</p>
                          {addon.addon_name && (
                            <p className="app-text-secondary text-sm mt-2">
                              <span className="font-medium">Add-on:</span> {addon.addon_name}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{formatCurrency(addon.unit_price)}</p>
                          <p className="text-sm app-text-muted">
                            Quantity: {addon.quantity}
                          </p>
                          <p className="text-sm font-medium app-text-primary mt-1">
                            Total: {formatCurrency(addon.total_price)}
                          </p>
                          <p className="text-xs app-text-muted">
                            {addon.is_optional ? 'Optional' : 'Required'}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
  
          {activeTab === 'attachments' && (
            <div className="theme-card">
              <h3 className="text-xl font-bold app-text-primary mb-4">Attachments</h3>
              {attachmentsLoading ? (
                <div className="flex justify-center py-8">
                  <div className="w-6 h-6 border-2 app-border rounded-full border-t-transparent animate-spin"></div>
                </div>
              ) : quoteAttachments.length === 0 ? (
                <p className="app-text-muted text-center py-8">No attachments found for this quote.</p>
              ) : (
                <div className="grid md:grid-cols-2 gap-4">
                  {quoteAttachments.map((attachment, index) => (
                    <div key={attachment.id || index} className="border app-border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold app-text-primary">{attachment.title || 'Attachment'}</h4>
                          <p className="app-text-muted text-sm">{attachment.file_type}</p>
                        </div>
                        <button
                          onClick={() => window.open(attachment.file_url, '_blank')}
                          className="px-4 py-2 bg-transparent border-2 app-border-blue app-text-primary rounded-full font-medium transition-all hover:app-bg-blue hover:text-white"
                        >
                          View
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="theme-card">
              <h3 className="text-xl font-bold app-text-primary mb-4">Quote History</h3>
              {revisionsLoading ? (
                <div className="flex justify-center py-8">
                  <div className="w-6 h-6 border-2 app-border rounded-full border-t-transparent animate-spin"></div>
                </div>
              ) : quoteRevisions.length === 0 ? (
                <p className="app-text-muted text-center py-8">No revision history found for this quote.</p>
              ) : (
                <div className="space-y-4">
                  {quoteRevisions.map((revision, index) => (
                    <div key={revision.id || index} className="border app-border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold app-text-primary">Revision {revision.version}</h4>
                        <span className="text-sm app-text-muted">{formatDate(revision.created_at)}</span>
                      </div>
                      <p className="app-text-secondary text-sm">{revision.changes_summary}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default QuoteDetail;


