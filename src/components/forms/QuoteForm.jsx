import { useState } from 'react';
import useQuoteCalculator from '../../hooks/useQuoteCalculator.js';
import Button from '../common/Button.jsx';
import LoadingSpinner from '../common/LoadingSpinner.jsx';
import { CLEANING_TYPES, ROOM_TYPES, EXTRAS, URGENCY_MULTIPLIERS } from '../../utils/constants.js';
import { formatCurrency } from '../../utils/helpers.js';

const QuoteForm = ({ 
  className = '',
  onQuoteComplete,
  showPricing = true,
  embedded = false
}) => {
  const {
    quoteData,
    pricing,
    errors,
    isSubmitting,
    submitStatus,
    updateCleaningType,
    updateRoomCount,
    toggleExtra,
    updateUrgency,
    updateCustomerInfo,
    updateLocation,
    submitQuote,
    resetQuote,
    isValid,
    hasRooms,
    totalRooms
  } = useQuoteCalculator();

  const [currentStep, setCurrentStep] = useState(1);
  const [focusedField, setFocusedField] = useState('');
  const [showQuoteModal, setShowQuoteModal] = useState(false);

  const steps = [
    { id: 1, title: 'Service Type', icon: '🏠' },
    { id: 2, title: 'Rooms & Extras', icon: '🛏️' },
    { id: 3, title: 'Details', icon: '📋' },
    { id: 4, title: 'Contact Info', icon: '👤' }
  ];

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    } else if (currentStep === steps.length && isValid) {
      setShowQuoteModal(true);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (currentStep === steps.length && isValid) {
      setShowQuoteModal(true);
    } else {
      const result = await submitQuote();
      
      if (result.success) {
        onQuoteComplete?.(result);
        setCurrentStep(steps.length + 1);
      }
    }
  };

  const finalizeQuote = async () => {
    const result = await submitQuote();
    
    if (result.success) {
      onQuoteComplete?.(result);
      setShowQuoteModal(false);
      setCurrentStep(steps.length + 1);
    }
  };

  const getInputClasses = (field, hasError = false) => {
    const baseClasses = 'w-full px-4 py-3 border rounded-lg transition-all duration-200 bg-white';
    const focusClasses = 'focus:outline-none focus:ring-2 focus:ring-[#006da6] focus:border-transparent';
    const errorClasses = hasError ? 'border-red-500' : 'border-gray-300';
    const hoverClasses = 'hover:border-gray-400';
    
    return `${baseClasses} ${focusClasses} ${errorClasses} ${hoverClasses}`;
  };

  const getLabelClasses = (field, hasError = false) => {
    const baseClasses = 'block text-sm font-medium mb-2 transition-colors duration-200';
    const focusedClasses = focusedField === field ? 'text-[#006da6]' : 'text-gray-700';
    const errorClasses = hasError ? 'text-red-600' : '';
    
    return `${baseClasses} ${focusedClasses} ${errorClasses}`;
  };

  const canProceedToNext = () => {
    switch (currentStep) {
      case 1:
        return quoteData.cleaningType;
      case 2:
        return hasRooms;
      case 3:
        return quoteData.location.suburb && quoteData.urgency;
      case 4:
        return quoteData.customerInfo.name && quoteData.customerInfo.email && quoteData.customerInfo.phone;
      default:
        return false;
    }
  };

  const QuoteModal = () => {
    if (!showQuoteModal) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-900">Your Quote Summary</h3>
            <button 
              onClick={() => setShowQuoteModal(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <div className="text-2xl font-bold text-[#006da6] mb-2">
              {formatCurrency(pricing.total)}
            </div>
            <p className="text-gray-600">Estimated Total (including GST)</p>
          </div>
          <div className="space-y-4 mb-6">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Service Type:</span>
              <span className="font-medium">{CLEANING_TYPES.find(type => type.id === quoteData.cleaningType)?.name}</span>
            </div>
            
            {totalRooms > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Rooms:</span>
                <span className="font-medium">{totalRooms} rooms</span>
              </div>
            )}
            
            {quoteData.extras.length > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Extras:</span>
                <span className="font-medium">{quoteData.extras.length} services</span>
              </div>
            )}
            
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Location:</span>
              <span className="font-medium">{quoteData.location.suburb}</span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Timing:</span>
              <span className="font-medium">
                {Object.entries(URGENCY_MULTIPLIERS).find(([key, urgency]) => 
                  key.toLowerCase() === quoteData.urgency
                )?.[1].name}
              </span>
            </div>
            
            {(quoteData.urgency === 'urgent' || quoteData.urgency === 'same_day') && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-sm text-orange-800">
                <p className="font-medium">30% Deposit Required</p>
                <p>This booking requires a 30% deposit to confirm your appointment.</p>
              </div>
            )}
          </div>
          
          <div className="border-t pt-4 mb-6">
            <p className="text-center font-medium text-gray-800 mb-2">Ready to proceed?</p>
            <p className="text-center text-gray-600 text-sm mb-4">
              Login to our portal to generate an official quote and book your service.
            </p>
          </div>
          
          <div className="flex space-x-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => setShowQuoteModal(false)}
            >
              Back to Form
            </Button>
            <Button
              variant="primary"
              className="flex-1"
              onClick={finalizeQuote}
            >
              LOGIN TO PORTAL
            </Button>
          </div>
        </div>
      </div>
    );
  };

  if (submitStatus === 'success') {
    return (
      <div className={`bg-blue-50 border border-blue-200 rounded-xl p-8 text-center ${className}`}>
        <div className="text-blue-600 text-6xl mb-6">✓</div>
        <h3 className="text-2xl font-bold text-blue-800 mb-4">
          Quote Submitted Successfully!
        </h3>
        <div className="bg-white rounded-lg p-6 mb-6">
          <div className="text-3xl font-bold text-[#006da6] mb-2">
            {formatCurrency(pricing.total)}
          </div>
          <p className="text-gray-600">Estimated Total (including GST)</p>
        </div>
        <p className="text-blue-700 mb-6">
          We'll contact you within 2 hours to confirm your booking and arrange the service.
        </p>
        <Button onClick={resetQuote} variant="primary">
          Get Another Quote
        </Button>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-lg overflow-hidden ${className}`}>
      {!embedded && (
        <div className="bg-gradient-to-r from-[#006da6] to-[#0080c7] p-6">
          <h2 className="text-2xl font-bold text-white mb-2">Get Your Instant Quote</h2>
          <p className="text-white/90">Professional cleaning services tailored to your needs</p>
        </div>
      )}

      <div className="p-6">
        <div className="flex justify-between items-center mb-8">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium transition-all duration-200 ${
                currentStep >= step.id 
                  ? 'bg-[#006da6] text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {currentStep > step.id ? '✓' : step.id}
              </div>
              <div className="ml-3 hidden sm:block">
                <p className={`text-sm font-medium ${
                  currentStep >= step.id ? 'text-[#006da6]' : 'text-gray-500'
                }`}>
                  {step.title}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div className={`w-8 h-0.5 mx-4 ${
                  currentStep > step.id ? 'bg-[#006da6]' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          {currentStep === 1 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  What type of cleaning do you need? <span className="text-red-500">*</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {CLEANING_TYPES.map((service) => (
                    <div
                      key={service.id}
                      onClick={() => updateCleaningType(service.id)}
                      className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md ${
                        quoteData.cleaningType === service.id
                          ? 'border-[#006da6] bg-[#006da6]/5'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900 mb-1">
                            {service.name}
                          </h4>
                          <p className="text-sm text-gray-600 mb-2">
                            Starting from {formatCurrency(service.basePrice)}
                          </p>
                          {service.popular && (
                            <span className="inline-block bg-[#006da6] text-white text-xs font-medium px-2 py-1 rounded-full">
                              Most Popular
                            </span>
                          )}
                        </div>
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          quoteData.cleaningType === service.id
                            ? 'border-[#006da6] bg-[#006da6]'
                            : 'border-gray-300'
                        }`}>
                          {quoteData.cleaningType === service.id && (
                            <div className="w-2 h-2 bg-white rounded-full" />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {errors.cleaningType && (
                  <p className="text-sm text-red-600 mt-2">{errors.cleaningType}</p>
                )}
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  How many rooms need cleaning? <span className="text-red-500">*</span>
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(ROOM_TYPES).map(([key, room]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        {room.name}
                      </label>
                      <div className="flex items-center justify-between">
                        <button
                          type="button"
                          onClick={() => updateRoomCount(key.toLowerCase(), Math.max(0, quoteData.rooms[key.toLowerCase()] - 1))}
                          className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors"
                        >
                          -
                        </button>
                        <span className="text-lg font-semibold text-gray-900 mx-4">
                          {quoteData.rooms[key.toLowerCase()] || 0}
                        </span>
                        <button
                          type="button"
                          onClick={() => updateRoomCount(key.toLowerCase(), (quoteData.rooms[key.toLowerCase()] || 0) + 1)}
                          className="w-8 h-8 rounded-full bg-[#006da6] hover:bg-[#0080c7] text-white flex items-center justify-center transition-colors"
                        >
                          +
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        +{formatCurrency(room.price)} each
                      </p>
                    </div>
                  ))}
                </div>
                {errors.rooms && (
                  <p className="text-sm text-red-600 mt-2">{errors.rooms}</p>
                )}
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Add extra services (optional)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(EXTRAS).map(([key, extra]) => (
                    <label
                      key={key}
                      className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={quoteData.extras.some(e => e.id === key)}
                        onChange={() => toggleExtra(key)}
                        className="mr-3 text-[#006da6] focus:ring-[#006da6] rounded"
                      />
                      <div className="flex-1">
                        <span className="font-medium text-gray-900">{extra.name}</span>
                        <span className="text-[#006da6] font-semibold ml-2">
                          +{formatCurrency(extra.price)}
                        </span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Service details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={getLabelClasses('suburb', errors.suburb)}>
                      Suburb <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={quoteData.location.suburb}
                      onChange={(e) => updateLocation('suburb', e.target.value)}
                      onFocus={() => setFocusedField('suburb')}
                      onBlur={() => setFocusedField('')}
                      className={getInputClasses('suburb', errors.suburb)}
                      placeholder="Enter your suburb"
                      required
                    />
                    {errors.suburb && (
                      <p className="text-sm text-red-600 mt-1">{errors.suburb}</p>
                    )}
                  </div>

                  <div>
                    <label className={getLabelClasses('postcode')}>
                      Postcode
                    </label>
                    <input
                      type="text"
                      value={quoteData.location.postcode}
                      onChange={(e) => updateLocation('postcode', e.target.value)}
                      onFocus={() => setFocusedField('postcode')}
                      onBlur={() => setFocusedField('')}
                      className={getInputClasses('postcode')}
                      placeholder="2000"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className={getLabelClasses('urgency')}>
                  When do you need this service? <span className="text-red-500">*</span>
                </label>
                <div className="space-y-2">
                  {Object.entries(URGENCY_MULTIPLIERS).map(([key, urgency]) => (
                    <label
                      key={key}
                      className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <input
                        type="radio"
                        name="urgency"
                        value={key.toLowerCase()}
                        checked={quoteData.urgency === key.toLowerCase()}
                        onChange={(e) => updateUrgency(e.target.value)}
                        className="mr-3 text-[#006da6] focus:ring-[#006da6]"
                        required
                      />
                      <div className="flex-1 flex justify-between items-center">
                        <span className="font-medium text-gray-900">{urgency.name}</span>
                        {urgency.multiplier > 1 && (
                          <span className="text-sm text-orange-600 font-medium">
                            30% Deposit Required
                          </span>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Contact information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={getLabelClasses('name', errors.name)}>
                      Full Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={quoteData.customerInfo.name}
                      onChange={(e) => updateCustomerInfo('name', e.target.value)}
                      onFocus={() => setFocusedField('name')}
                      onBlur={() => setFocusedField('')}
                      className={getInputClasses('name', errors.name)}
                      placeholder="Enter your full name"
                      required
                    />
                    {errors.name && (
                      <p className="text-sm text-red-600 mt-1">{errors.name}</p>
                    )}
                  </div>

                  <div>
                    <label className={getLabelClasses('email', errors.email)}>
                      Email Address <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="email"
                      value={quoteData.customerInfo.email}
                      onChange={(e) => updateCustomerInfo('email', e.target.value)}
                      onFocus={() => setFocusedField('email')}
                      onBlur={() => setFocusedField('')}
                      className={getInputClasses('email', errors.email)}
                      placeholder="info@nswcleaningcompany.com"
                      required
                    />
                    {errors.email && (
                      <p className="text-sm text-red-600 mt-1">{errors.email}</p>
                    )}
                  </div>

                  <div>
                    <label className={getLabelClasses('phone', errors.phone)}>
                      Phone Number <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      value={quoteData.customerInfo.phone}
                      onChange={(e) => updateCustomerInfo('phone', e.target.value)}
                      onFocus={() => setFocusedField('phone')}
                      onBlur={() => setFocusedField('')}
                      className={getInputClasses('phone', errors.phone)}
                      placeholder="0400 000 000"
                      required
                    />
                    {errors.phone && (
                      <p className="text-sm text-red-600 mt-1">{errors.phone}</p>
                    )}
                  </div>

                  <div>
                    <label className="flex items-center mt-6">
                      <input
                        type="checkbox"
                        checked={quoteData.customerInfo.isNDISParticipant}
                        onChange={(e) => updateCustomerInfo('isNDISParticipant', e.target.checked)}
                        className="mr-2 text-[#006da6] focus:ring-[#006da6] rounded"
                      />
                      <span className="text-sm text-gray-700">I am an NDIS participant</span>
                    </label>
                  </div>
                </div>

                {quoteData.customerInfo.isNDISParticipant && (
                  <div>
                    <label className={getLabelClasses('ndisNumber', errors.ndisNumber)}>
                      NDIS Number
                    </label>
                    <input
                      type="text"
                      value={quoteData.customerInfo.ndisNumber}
                      onChange={(e) => updateCustomerInfo('ndisNumber', e.target.value)}
                      onFocus={() => setFocusedField('ndisNumber')}
                      onBlur={() => setFocusedField('')}
                      className={getInputClasses('ndisNumber', errors.ndisNumber)}
                      placeholder="123456789"
                    />
                    {errors.ndisNumber && (
                      <p className="text-sm text-red-600 mt-1">{errors.ndisNumber}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {showPricing && pricing.total > 0 && (
            <div className="bg-gray-50 rounded-lg p-6 mt-6">
              <h4 className="font-semibold text-gray-900 mb-4">Quote Summary</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Base service</span>
                  <span>{formatCurrency(pricing.basePrice)}</span>
                </div>
                {pricing.roomsTotal > 0 && (
                  <div className="flex justify-between">
                    <span>Rooms ({totalRooms})</span>
                    <span>{formatCurrency(pricing.roomsTotal)}</span>
                  </div>
                )}
                {pricing.extrasTotal > 0 && (
                  <div className="flex justify-between">
                    <span>Extras</span>
                    <span>{formatCurrency(pricing.extrasTotal)}</span>
                  </div>
                )}
                {pricing.urgencyMultiplier > 1 && (
                  <div className="flex justify-between text-orange-600">
                    <span>30% Deposit Required</span>
                    <span>{formatCurrency(pricing.total * 0.3)}</span>
                  </div>
                )}
                <div className="border-t pt-2 flex justify-between font-semibold text-lg">
                  <span>Total (inc. GST)</span>
                  <span className="text-[#006da6]">{formatCurrency(pricing.total)}</span>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-between pt-6">
            {currentStep > 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={handlePrevious}
                disabled={isSubmitting}
              >
                Previous
              </Button>
            )}
            
            <div className="ml-auto">
              {currentStep < steps.length ? (
                <Button
                  type="button"
                  variant="primary"
                  onClick={handleNext}
                  disabled={!canProceedToNext()}
                >
                  Next Step
                </Button>
              ) : (
                <Button
                  type="submit"
                  variant="primary"
                  disabled={!isValid || isSubmitting}
                  loading={isSubmitting}
                >
                  {isSubmitting ? 'Submitting Quote...' : 'Get My Quote'}
                </Button>
              )}
            </div>
          </div>
        </form>
      </div>
      <QuoteModal />
    </div>
  );
};

export default QuoteForm;

