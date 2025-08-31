import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useQuoteActions from '../../hooks/useQuoteActions.js';

const QuoteForm = ({ 
  initialData = null, 
  mode = 'create',
  quoteId = null,
  services = [],
  onSuccess,
  onCancel,
  className = '',
  buttonText = null
}) => {
  const navigate = useNavigate();
  const { createQuote, updateQuote, calculateQuote, loading, error, clearError } = useQuoteActions();

  const [formData, setFormData] = useState({
    service_type: '',
    cleaning_type: 'general',
    property_address: '',
    suburb: '',
    postcode: '',
    state: 'NSW',
    number_of_rooms: 1,
    square_meters: '',
    urgency_level: 2,
    preferred_date: '',
    preferred_time: '',
    special_requirements: '',
    access_instructions: '',
    is_ndis_client: false,
    ndis_participant_number: '',
    plan_manager_name: '',
    plan_manager_contact: '',
    support_coordinator_name: '',
    support_coordinator_contact: ''
  });

  const [calculation, setCalculation] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [showNDISFields, setShowNDISFields] = useState(false);

  const cleaningTypeOptions = [
    { value: 'general', label: 'General Cleaning' },
    { value: 'deep', label: 'Deep Cleaning' },
    { value: 'end_of_lease', label: 'End of Lease Cleaning' },
    { value: 'ndis', label: 'NDIS Cleaning' },
    { value: 'commercial', label: 'Commercial Cleaning' },
    { value: 'carpet', label: 'Carpet Cleaning' },
    { value: 'window', label: 'Window Cleaning' },
    { value: 'pressure_washing', label: 'Pressure Washing' }
  ];

  const stateOptions = [
    { value: 'NSW', label: 'New South Wales (NSW)' },
    { value: 'VIC', label: 'Victoria (VIC)' },
    { value: 'QLD', label: 'Queensland (QLD)' },
    { value: 'WA', label: 'Western Australia (WA)' },
    { value: 'SA', label: 'South Australia (SA)' },
    { value: 'TAS', label: 'Tasmania (TAS)' },
    { value: 'ACT', label: 'Australian Capital Territory (ACT)' },
    { value: 'NT', label: 'Northern Territory (NT)' }
  ];

  const urgencyOptions = [
    { value: 1, label: 'Flexible (7+ days)' },
    { value: 2, label: 'Standard (3-7 days)' },
    { value: 3, label: 'Priority (1-3 days)' },
    { value: 4, label: 'Urgent (Same day)' },
    { value: 5, label: 'Emergency (ASAP)' }
  ];

  useEffect(() => {
    if (initialData) {
      setFormData({
        ...formData,
        ...initialData,
        preferred_date: initialData.preferred_date || '',
        preferred_time: initialData.preferred_time || ''
      });
      setShowNDISFields(initialData.is_ndis_client || false);
    }
  }, [initialData]);

  useEffect(() => {
    if (formData.cleaning_type === 'ndis') {
      setFormData(prev => ({ ...prev, is_ndis_client: true }));
      setShowNDISFields(true);
    }
  }, [formData.cleaning_type]);

  const validateForm = () => {
    const errors = {};
    if (!formData.service_type) errors.service_type = 'Service is required';
    if (!formData.property_address.trim()) errors.property_address = 'Property address is required';
    if (!formData.suburb.trim()) errors.suburb = 'Suburb is required';
    if (!formData.postcode.trim()) errors.postcode = 'Postcode is required';
    if (!/^\d{4}$/.test(formData.postcode)) errors.postcode = 'Postcode must be 4 digits';
    if (formData.number_of_rooms < 1) errors.number_of_rooms = 'Number of rooms must be at least 1';
    if (formData.square_meters && formData.square_meters < 1) errors.square_meters = 'Square meters must be positive';
    if (formData.is_ndis_client && !formData.ndis_participant_number.trim()) {
      errors.ndis_participant_number = 'NDIS participant number is required';
    }
    if (formData.preferred_date) {
      const selectedDate = new Date(formData.preferred_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (selectedDate < today) {
        errors.preferred_date = 'Preferred date cannot be in the past';
      }
    }
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
    clearError();
  };

  const handleNDISToggle = (checked) => {
    setShowNDISFields(checked);
    setFormData(prev => ({
      ...prev,
      is_ndis_client: checked,
      ndis_participant_number: checked ? prev.ndis_participant_number : '',
      plan_manager_name: checked ? prev.plan_manager_name : '',
      plan_manager_contact: checked ? prev.plan_manager_contact : '',
      support_coordinator_name: checked ? prev.support_coordinator_name : '',
      support_coordinator_contact: checked ? prev.support_coordinator_contact : ''
    }));
  };

  const handleCalculate = async () => {
    if (!formData.service_type || !formData.postcode || !formData.number_of_rooms) {
      setValidationErrors({
        service_type: !formData.service_type ? 'Service is required for calculation' : '',
        postcode: !formData.postcode ? 'Postcode is required for calculation' : '',
        number_of_rooms: !formData.number_of_rooms ? 'Number of rooms is required for calculation' : ''
      });
      return;
    }
    setIsCalculating(true);
    try {
      const calculationData = {
        service_id: formData.service_type,
        cleaning_type: formData.cleaning_type,
        number_of_rooms: parseInt(formData.number_of_rooms),
        square_meters: formData.square_meters ? parseFloat(formData.square_meters) : null,
        urgency_level: parseInt(formData.urgency_level),
        postcode: formData.postcode,
        addon_ids: []
      };
      const result = await calculateQuote(calculationData);
      setCalculation(result);
    } catch (err) {
      console.error('Calculation failed:', err.message);
    } finally {
      setIsCalculating(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    const submitData = {
      ...formData,
      number_of_rooms: parseInt(formData.number_of_rooms),
      urgency_level: parseInt(formData.urgency_level),
      square_meters: formData.square_meters ? parseFloat(formData.square_meters) : null,
      preferred_time: formData.preferred_time ? `${formData.preferred_time}:00` : null,
    };
    
    console.log('🚀 Submitting data:', JSON.stringify(submitData, null, 2));
    
    if (mode === 'create' && onSuccess) {
      onSuccess(submitData);
      return;
    }
    
    try {
      let result;
      if (mode === 'create') {
        result = await createQuote(submitData);
      } else {
        const updateId = quoteId || initialData.id;
        result = await updateQuote(updateId, submitData);
        
        if (!result?.id) {
          result = { ...result, id: updateId };
        }
      }
      
      if (onSuccess) {
        onSuccess(result);
      } else {
        setTimeout(() => {
          navigate(`/quotes/${result.id}`);
        }, 1000);
      }
    } catch (err) {
      console.error('Form submission failed:', err.message);
      console.error('Full error:', err);
    }
  };
  
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD'
    }).format(amount);
  };

  return (
    <div className={`theme-card ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold app-text-primary mb-2">
          {mode === 'create' ? 'Create New Quote' : 'Edit Quote'}
        </h2>
        <p className="app-text-muted">
          Fill in the details below to {mode === 'create' ? 'create' : 'update'} your cleaning quote.
        </p>
      </div>
  
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}
  
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Service Type *</label>
            <select
              value={formData.service_type} 
              onChange={(e) => handleInputChange('service_type', e.target.value)}
              className={`theme-input ${validationErrors.service_type ? 'border-red-500' : ''}`}
              required
            >
              <option value="">Select a service</option>
              {services && Array.isArray(services) && services.length > 0 ? (
                services.map(service => (
                  <option key={service.id} value={service.service_type || service.type || service.name.toLowerCase().replace(' ', '_')}>
                    {service.name}
                  </option>
                ))
              ) : (
                <option value="" disabled>Loading services...</option>
              )}
            </select>
            {validationErrors.service_type && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.service_type}</p>
            )}
          </div>
  
          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Cleaning Type *</label>
            <select
              value={formData.cleaning_type}
              onChange={(e) => handleInputChange('cleaning_type', e.target.value)}
              className="theme-input"
              required
            >
              {cleaningTypeOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold app-text-primary mb-2">Property Address *</label>
          <textarea
            value={formData.property_address}
            onChange={(e) => handleInputChange('property_address', e.target.value)}
            className={`theme-input h-20 resize-none ${validationErrors.property_address ? 'border-red-500' : ''}`}
            placeholder="Enter the full property address"
            required
          />
          {validationErrors.property_address && (
            <p className="text-red-500 text-xs mt-1">{validationErrors.property_address}</p>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Suburb *</label>
            <input
              type="text"
              value={formData.suburb}
              onChange={(e) => handleInputChange('suburb', e.target.value)}
              className={`theme-input ${validationErrors.suburb ? 'border-red-500' : ''}`}
              required
            />
            {validationErrors.suburb && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.suburb}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Postcode *</label>
            <input
              type="text"
              value={formData.postcode}
              onChange={(e) => handleInputChange('postcode', e.target.value)}
              className={`theme-input ${validationErrors.postcode ? 'border-red-500' : ''}`}
              maxLength="4"
              pattern="\d{4}"
              required
            />
            {validationErrors.postcode && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.postcode}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">State *</label>
            <select
              value={formData.state}
              onChange={(e) => handleInputChange('state', e.target.value)}
              className="theme-input"
              required
            >
              {stateOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Number of Rooms *</label>
            <input
              type="number"
              value={formData.number_of_rooms}
              onChange={(e) => handleInputChange('number_of_rooms', parseInt(e.target.value) || 1)}
              className={`theme-input ${validationErrors.number_of_rooms ? 'border-red-500' : ''}`}
              min="1"
              required
            />
            {validationErrors.number_of_rooms && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.number_of_rooms}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Square Meters</label>
            <input
              type="number"
              value={formData.square_meters}
              onChange={(e) => handleInputChange('square_meters', e.target.value)}
              className={`theme-input ${validationErrors.square_meters ? 'border-red-500' : ''}`}
              min="1"
              step="0.1"
              placeholder="Optional"
            />
            {validationErrors.square_meters && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.square_meters}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Urgency Level *</label>
            <select
              value={formData.urgency_level}
              onChange={(e) => handleInputChange('urgency_level', parseInt(e.target.value))}
              className="theme-input"
              required
            >
              {urgencyOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Preferred Date</label>
            <input
              type="date"
              value={formData.preferred_date}
              onChange={(e) => handleInputChange('preferred_date', e.target.value)}
              className={`theme-input ${validationErrors.preferred_date ? 'border-red-500' : ''}`}
              min={new Date().toISOString().split('T')[0]}
            />
            {validationErrors.preferred_date && (
              <p className="text-red-500 text-xs mt-1">{validationErrors.preferred_date}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold app-text-primary mb-2">Preferred Time</label>
            <input
              type="time"
              value={formData.preferred_time}
              onChange={(e) => handleInputChange('preferred_time', e.target.value)}
              className="theme-input"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold app-text-primary mb-2">Special Requirements</label>
          <textarea
            value={formData.special_requirements}
            onChange={(e) => handleInputChange('special_requirements', e.target.value)}
            className="theme-input h-24 resize-none"
            placeholder="Any special cleaning requirements or instructions..."
          />
        </div>

        <div>
          <label className="block text-sm font-semibold app-text-primary mb-2">Access Instructions</label>
          <textarea
            value={formData.access_instructions}
            onChange={(e) => handleInputChange('access_instructions', e.target.value)}
            className="theme-input h-20 resize-none"
            placeholder="Property access instructions (keys, codes, etc.)"
          />
        </div>

        <div className="border-t app-border pt-6">
          <div className="flex items-center gap-3 mb-4">
            <input
              type="checkbox"
              id="ndis-client"
              checked={formData.is_ndis_client}
              onChange={(e) => handleNDISToggle(e.target.checked)}
              className="w-4 h-4 app-blue app-bg-secondary app-border rounded focus:ring-2 focus:ring-blue-500"
            />
            <label htmlFor="ndis-client" className="text-sm font-semibold app-text-primary">
              This is an NDIS client
            </label>
          </div>

          {showNDISFields && (
            <div className="space-y-4 app-bg-secondary app-border p-4 rounded-lg">
              <div>
                <label className="block text-sm font-semibold app-text-primary mb-2">NDIS Participant Number *</label>
                <input
                  type="text"
                  value={formData.ndis_participant_number}
                  onChange={(e) => handleInputChange('ndis_participant_number', e.target.value)}
                  className={`theme-input ${validationErrors.ndis_participant_number ? 'border-red-500' : ''}`}
                  maxLength="9"
                  required={formData.is_ndis_client}
                />
                {validationErrors.ndis_participant_number && (
                  <p className="text-red-500 text-xs mt-1">{validationErrors.ndis_participant_number}</p>
                )}
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold app-text-primary mb-2">Plan Manager Name</label>
                  <input
                    type="text"
                    value={formData.plan_manager_name}
                    onChange={(e) => handleInputChange('plan_manager_name', e.target.value)}
                    className="theme-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold app-text-primary mb-2">Plan Manager Contact</label>
                  <input
                    type="text"
                    value={formData.plan_manager_contact}
                    onChange={(e) => handleInputChange('plan_manager_contact', e.target.value)}
                    className="theme-input"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold app-text-primary mb-2">Support Coordinator Name</label>
                  <input
                    type="text"
                    value={formData.support_coordinator_name}
                    onChange={(e) => handleInputChange('support_coordinator_name', e.target.value)}
                    className="theme-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold app-text-primary mb-2">Support Coordinator Contact</label>
                  <input
                    type="text"
                    value={formData.support_coordinator_contact}
                    onChange={(e) => handleInputChange('support_coordinator_contact', e.target.value)}
                    className="theme-input"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {calculation && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-2">Price Calculation</h3>
            <div className="space-y-2 text-sm text-green-700">
              <div className="flex justify-between">
                <span>Base Price:</span>
                <span>{formatCurrency(calculation.base_price)}</span>
              </div>
              {calculation.travel_cost > 0 && (
                <div className="flex justify-between">
                  <span>Travel Cost:</span>
                  <span>{formatCurrency(calculation.travel_cost)}</span>
                </div>
              )}
              {calculation.urgency_surcharge > 0 && (
                <div className="flex justify-between">
                  <span>Urgency Downpayment:</span>
                  <span>{formatCurrency(calculation.urgency_surcharge)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>GST:</span>
                <span>{formatCurrency(calculation.gst_amount)}</span>
              </div>
              <div className="flex justify-between font-bold text-lg border-t border-green-300 pt-2">
                <span>Total:</span>
                <span>{formatCurrency(calculation.final_price)}</span>
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t app-border">
          <button
            type="button"
            onClick={handleCalculate}
            disabled={loading || isCalculating}
            className="flex-1 px-6 py-2 bg-transparent border-2 app-border-blue app-text-primary rounded-lg font-medium transition-all hover:app-bg-blue hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCalculating ? 'Calculating...' : 'Calculate Price'}
          </button>

          <div className="flex gap-4 flex-1">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={loading}
                className="flex-1 px-6 py-2 app-bg-secondary app-text-primary rounded-lg font-medium hover:opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex-1 theme-button disabled:opacity-50 disabled:cursor-not-allowed"
            > 
              {loading ? 'Processing...' : buttonText || (mode === 'create' ? 'Create Quote' : 'Update Quote')}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default QuoteForm;

