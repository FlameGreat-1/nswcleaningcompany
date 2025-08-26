import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext.jsx';
import QuoteForm from '../../components/quotes/QuoteForm.jsx';
import SEO from '../../components/common/SEO.jsx';
import quotesService from '../../services/quotesService.js';

const EditQuote = ({ quoteId }) => {
  const id = quoteId;
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [quote, setQuote] = useState(null);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [canEdit, setCanEdit] = useState(false);

  useEffect(() => {
    loadServices();
    fetchQuote();
  }, [id]);

  const loadServices = async () => {
    try {
      const response = await quotesService.getServices(); 
      setServices(response.results || response);
    } catch (err) {
      console.error('Failed to load services:', err);
    }
  };

  const fetchQuote = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await quotesService.getQuote(id);
      setQuote(response);
      
      const editableStatuses = ['draft', 'rejected'];
      const userCanEdit = editableStatuses.includes(response.status) && 
                         (user?.id === response.client.id || user?.is_staff);
      
      setCanEdit(userCanEdit);
      
      if (!userCanEdit) {
        setError('You do not have permission to edit this quote or it cannot be edited in its current status.');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load quote for editing');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSuccess = (updatedQuote) => {
    const targetId = id || quoteId || quote?.id;
    
    if (targetId) {
      navigate(`/clients/quotes/${targetId}`, {
        state: { message: 'Quote updated successfully!' }
      });
    } else {
      navigate('/clients/quotes', {
        state: { message: 'Quote updated successfully! Please find your quote in the list.' }
      });
    }
  };
  
  const handleCancel = () => {
    navigate(`/clients/quotes/${id}`);
  };

  const prepareFormData = (quote) => {
    return {
      id: quote.id,
      service_type: quote.service?.toString() || '',
      cleaning_type: quote.cleaning_type || 'general',
      property_address: quote.property_address || '',
      suburb: quote.suburb || '',
      postcode: quote.postcode || '',
      state: quote.state || 'NSW',
      number_of_rooms: quote.number_of_rooms || 1,
      square_meters: quote.square_meters || '',
      urgency_level: quote.urgency_level || 2,
      preferred_date: quote.preferred_date || '',
      preferred_time: quote.preferred_time || '',
      special_requirements: quote.special_requirements || '',
      access_instructions: quote.access_instructions || '',
      is_ndis_client: quote.is_ndis_client || false,
      ndis_participant_number: quote.ndis_participant_number || '',
      plan_manager_name: quote.plan_manager_name || '',
      plan_manager_contact: quote.plan_manager_contact || '',
      support_coordinator_name: quote.support_coordinator_name || '',
      support_coordinator_contact: quote.support_coordinator_contact || ''
    };
  };

  if (loading) {
    return (
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center min-h-96">
          <div className="w-8 h-8 border-4 app-border rounded-full border-t-transparent animate-spin"></div>
        </div>
      </div>
    );
  }

  if (error || !quote) {
    return (
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="theme-card text-center py-12">
          <div className="text-red-600 mb-4">
            <h3 className="text-lg font-semibold mb-2">Cannot Edit Quote</h3>
            <p className="app-text-muted">{error || 'Quote not found or cannot be edited.'}</p>
          </div>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => navigate('/clients/quotes')}
              className="px-6 py-3 bg-transparent border-2 app-border-blue app-text-primary rounded-full font-medium transition-all hover:app-bg-blue hover:text-white"
            >
              Back to Quotes
            </button>
            {quote && (
              <button
                onClick={() => navigate(`/clients/quotes/${quote.id}`)}
                className="theme-button"
              >
                View Quote
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!canEdit) {
    return (
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="theme-card text-center py-12">
          <div className="text-yellow-600 mb-4">
            <h3 className="text-lg font-semibold mb-2">Quote Cannot Be Edited</h3>
            <p className="app-text-muted">
              This quote is in "{quote.status.replace('_', ' ')}" status and cannot be modified.
              Only draft and rejected quotes can be edited.
            </p>
          </div>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => navigate('/clients/quotes')}
              className="px-6 py-3 bg-transparent border-2 app-border-blue app-text-primary rounded-full font-medium transition-all hover:app-bg-blue hover:text-white"
            >
              Back to Quotes
            </button>
            <button
              onClick={() => navigate(`/clients/quotes/${quote.id}`)}
              className="theme-button"
            >
              View Quote Details
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO 
        title={`Edit Quote ${quote.quote_number}`}
        description={`Edit quote ${quote.quote_number} for ${quote.cleaning_type} cleaning service`}
      />
      
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-black app-text-primary mb-4">
              Edit Quote {quote.quote_number}
            </h1>
            <p className="text-lg app-text-muted max-w-3xl mx-auto">
              Update your quote details below. Changes will be saved as a new revision.
            </p>
          </div>

          <div className="app-bg-secondary app-border rounded-lg p-4 max-w-3xl mx-auto mb-8">
            <div className="flex items-start gap-3">
              <div className="app-blue text-xl">ℹ️</div>
              <div>
                <h3 className="font-semibold app-text-primary mb-1">
                  Editing Quote in {quote.status.replace('_', ' ').toUpperCase()} Status
                </h3>
                <p className="text-sm app-text-secondary">
                  {quote.status === 'draft' 
                    ? 'You can modify all fields since this quote is still in draft status.'
                    : 'This quote was rejected and can now be edited and resubmitted.'
                  }
                </p>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-8">
            <div className="theme-card text-center">
              <h3 className="font-semibold app-text-primary mb-2">Current Status</h3>
              <span className={`
                inline-block px-3 py-1 rounded-full text-sm font-medium
                ${quote.status === 'draft' ? 'app-bg-secondary app-text-primary' : 'bg-red-100 text-red-800'}
              `}>
                {quote.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            <div className="theme-card text-center">
              <h3 className="font-semibold app-text-primary mb-2">Service Type</h3>
              <p className="app-text-secondary text-sm">
                {quote.cleaning_type.replace('_', ' ').toUpperCase()}
              </p>
            </div>

            <div className="theme-card text-center">
              <h3 className="font-semibold app-text-primary mb-2">Current Total</h3>
              <p className="text-lg font-bold app-text-primary">
                {new Intl.NumberFormat('en-AU', {
                  style: 'currency',
                  currency: 'AUD'
                }).format(quote.final_price)}
              </p>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto">
          <QuoteForm
            mode="edit"
            quoteId={quote.id} 
            initialData={prepareFormData(quote)}
            services={services}
            onSuccess={handleUpdateSuccess}
            onCancel={handleCancel}
          />
        </div>

        <div className="max-w-6xl mx-auto mt-8">
          <div className="app-bg-secondary rounded-lg p-6 text-center">
            <h3 className="text-lg font-semibold app-text-primary mb-2">
              Need to Start Over?
            </h3>
            <p className="app-text-muted text-sm mb-4">
              If you need to make major changes, you might want to create a new quote instead
            </p>
            <button
              onClick={() => navigate('/clients/quotes/create', { 
                state: { duplicateFrom: quote.id } 
              })}
              className="px-4 py-2 bg-transparent border-2 app-border-blue app-text-primary rounded-full font-medium transition-all hover:app-bg-blue hover:text-white"
            >
              Create New Quote
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default EditQuote;
