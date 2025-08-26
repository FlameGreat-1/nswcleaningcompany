import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext.jsx';
import QuoteForm from '../../components/quotes/QuoteForm.jsx';
import QuoteAddonsAttachments from '../../components/quotes/QuoteAddonsAttachments.jsx';
import SEO from '../../components/common/SEO.jsx';
import quotesService from '../../services/quotesService.js';

const CreateQuote = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [services, setServices] = useState([]);
  const [initialFormData, setInitialFormData] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [quoteData, setQuoteData] = useState(null);

  useEffect(() => {
    initializePage();
  }, []);

  useEffect(() => {
    const templateId = searchParams.get('template');
    const serviceId = searchParams.get('service');
    const clientId = searchParams.get('client');
    
    if (templateId) {
      loadTemplate(templateId);
    } else if (serviceId || clientId) {
      setInitialFormData({
        service_type: serviceId || '',
        client: clientId || ''
      });
    }
  }, [searchParams]);

  const initializePage = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadServices(),
        loadTemplates()
      ]);
    } catch (err) {
      setError('Failed to initialize page data');
    } finally {
      setLoading(false);
    }
  };

  const loadServices = async () => {
    try {
      const response = await quotesService.getServices(); 
      console.log('🔍 Services structure:', response.results?.[0] || response[0]);
      console.log('🔍 Full services response:', response);
      setServices(response.results || response);
    } catch (err) {
      console.error('Failed to load services:', err);
    }
  };
  
  const loadTemplates = async () => {
    try {
      const response = await quotesService.getQuoteTemplates({ limit: 10 });
      setTemplates(response.results || response);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  };

  const loadTemplate = async (templateId) => {
    setLoading(true);
    try {
      const template = await quotesService.getQuoteTemplate(templateId);
      setSelectedTemplate(template);
      setInitialFormData({
        service_type: template.service || '',
        cleaning_type: template.cleaning_type || 'general',
        number_of_rooms: template.number_of_rooms || 1,
        square_meters: template.square_meters || '',
        urgency_level: template.urgency_level || 2,
        special_requirements: template.special_requirements || '',
        access_instructions: template.access_instructions || '',
        is_ndis_client: template.is_ndis_client || false
      });
    } catch (err) {
      setError('Failed to load template');
    } finally {
      setLoading(false);
    }
  };

  const handleUseTemplate = async (templateId) => {
    await loadTemplate(templateId);
    setShowTemplates(false);
  };

  const handleQuoteFormComplete = (formData) => {
    setQuoteData(formData);
    setCurrentStep(2);
  };

  const handleQuoteSuccess = (newQuote) => {
    if (newQuote?.id) {
      // Invalidate quotes queries to trigger a refetch
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      
      setTimeout(() => {
        navigate(`/clients/quotes/${newQuote.id}`, {
          state: { message: 'Quote created successfully!' }
        });
      }, 1000);
    } else {
      setError('Quote created but unable to redirect. Please check your quotes list.');
      // Still invalidate queries even if we don't have the ID
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      
      setTimeout(() => {
        navigate('/clients/quotes', {
          state: { message: 'Quote created successfully! Check your quotes list.' }
        });
      }, 1000);
    }
  };
  
  const handleCancel = () => {
    navigate('/quotes');
  };

  const clearTemplate = () => {
    setSelectedTemplate(null);
    setInitialFormData(null);
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.delete('template');
    navigate(`${window.location.pathname}?${newSearchParams}`, { replace: true });
  };

  const getQuickStartOptions = () => [
    {
      title: 'General Cleaning',
      description: 'Standard house cleaning service',
      data: {
        cleaning_type: 'general',
        urgency_level: 2
      }
    },
    {
      title: 'Deep Cleaning',
      description: 'Comprehensive deep cleaning service',
      data: {
        cleaning_type: 'deep',
        urgency_level: 2
      }
    },
    {
      title: 'End of Lease',
      description: 'Move-out cleaning service',
      data: {
        cleaning_type: 'end_of_lease',
        urgency_level: 3
      }
    },
    {
      title: 'NDIS Cleaning',
      description: 'NDIS participant cleaning service',
      data: {
        cleaning_type: 'ndis',
        is_ndis_client: true,
        urgency_level: 2
      }
    }
  ];

  const handleQuickStart = (optionData) => {
    setInitialFormData({
      ...initialFormData,
      ...optionData
    });
    setShowTemplates(false);
  };

  const handleShowTemplates = () => {
    setShowTemplates(true);
  };

  if (loading && !initialFormData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO 
        title="Create New Quote" 
        description="Create a new cleaning service quote with our easy-to-use form"
      />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Create New Quote</h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Create a new cleaning service quote with our easy-to-use form
            </p>
            {templates.length > 0 && !selectedTemplate && !showTemplates && currentStep === 1 && (
              <div className="mt-6">
                <button
                  onClick={handleShowTemplates}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500"
                >
                  Use Template
                </button>
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg mb-6 max-w-2xl mx-auto">
              <p className="font-medium">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {currentStep === 1 && showTemplates && templates.length > 0 && !selectedTemplate && (
            <div className="mb-8">
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6 max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Quick Start Options</h2>
                  <button
                    onClick={() => setShowTemplates(false)}
                    className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 text-sm font-medium"
                  >
                    Skip and create from scratch
                  </button>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                  {getQuickStartOptions().map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleQuickStart(option.data)}
                      className="text-left p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                        {option.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {option.description}
                      </p>
                    </button>
                  ))}
                </div>
                {templates.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                      Or choose from your saved templates
                    </h3>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {templates.map((template) => (
                        <div
                          key={template.id}
                          className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-white dark:bg-gray-800"
                        >
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                                {template.name}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                {template.cleaning_type.replace('_', ' ').toUpperCase()}
                              </p>
                            </div>
                            <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-1 rounded">
                              {template.number_of_rooms} rooms
                            </span>
                          </div>

                          {template.description && (
                            <p className="text-sm text-gray-700 dark:text-gray-300 mb-3 line-clamp-2">
                              {template.description}
                            </p>
                          )}

                          <div className="flex gap-2">
                            <button
                              onClick={() => handleUseTemplate(template.id)}
                              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500"
                            >
                              Use Template
                            </button>
                            <button
                              onClick={() => {
                                navigate(`/templates/${template.id}`);
                              }}
                              className="px-4 py-2 border border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400 rounded-lg font-medium hover:bg-blue-50 dark:hover:bg-blue-900/20 focus:ring-2 focus:ring-blue-500"
                            >
                              View
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {currentStep === 1 && selectedTemplate && (
            <div className="mb-6">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 max-w-2xl mx-auto">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-1">
                      Using Template: {selectedTemplate.name}
                    </h3>
                    <p className="text-sm text-blue-600 dark:text-blue-300">
                      Pre-filled with template data. You can modify any field below.
                    </p>
                  </div>
                  <button
                    onClick={clearTemplate}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
                  >
                    Clear Template
                  </button>
                </div>
              </div>
            </div>
          )}
          
          <div className="max-w-6xl mx-auto">
            {currentStep === 1 ? (
              <QuoteForm
                mode="create"
                initialData={initialFormData}
                services={services}
                onSuccess={handleQuoteFormComplete}
                onCancel={handleCancel}
                buttonText="Next"
              />
            ) : (
              <QuoteAddonsAttachments
                quoteData={quoteData}
                serviceId={quoteData?.service_type}
                onComplete={handleQuoteSuccess}
                onBack={() => setCurrentStep(1)}
              />
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default CreateQuote;
