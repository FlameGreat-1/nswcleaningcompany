import { useState, useCallback, useEffect } from 'react';
import { CLEANING_TYPES, ROOM_TYPES, EXTRAS, URGENCY_MULTIPLIERS, STORAGE_KEYS, API_ENDPOINTS } from '../utils/constants.js';
import { validateQuoteForm, sanitizeFormData } from '../utils/validation.js';
import { calculateQuoteTotal, getStorageItem, setStorageItem } from '../utils/helpers.js';

const useQuoteCalculator = () => {
  const [quoteData, setQuoteData] = useState({
    cleaningType: '',
    rooms: {
      bedrooms: 0,
      bathrooms: 0,
      kitchens: 0,
      livingRooms: 0,
      diningRooms: 0
    },
    extras: [],
    urgency: 'standard',
    location: {
      suburb: '',
      postcode: ''
    },
    customerInfo: {
      name: '',
      email: '',
      phone: '',
      ndisNumber: '',
      isNDISParticipant: false
    },
    specialRequests: '',
    preferredDate: '',
    preferredTime: ''
  });

  const [pricing, setPricing] = useState({
    basePrice: 0,
    roomsTotal: 0,
    extrasTotal: 0,
    urgencyMultiplier: 1,
    subtotal: 0,
    gst: 0,
    total: 0
  });

  const [errors, setErrors] = useState({});
  const [isCalculating, setIsCalculating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const loadSavedData = useCallback(() => {
    const savedData = getStorageItem(STORAGE_KEYS.quoteData);
    if (savedData) {
      setQuoteData(prev => ({ ...prev, ...savedData }));
    }
  }, []);

  const saveData = useCallback(() => {
    setStorageItem(STORAGE_KEYS.quoteData, quoteData);
  }, [quoteData]);

  useEffect(() => {
    loadSavedData();
  }, [loadSavedData]);

  useEffect(() => {
    saveData();
  }, [saveData]);

  const updateCleaningType = useCallback((type) => {
    const service = CLEANING_TYPES.find(s => s.id === type);
    setQuoteData(prev => ({
      ...prev,
      cleaningType: type
    }));
    
    if (service) {
      setPricing(prev => ({
        ...prev,
        basePrice: service.basePrice
      }));
    }
    
    if (errors.cleaningType) {
      setErrors(prev => ({ ...prev, cleaningType: null }));
    }
  }, [errors.cleaningType]);

  const updateRoomCount = useCallback((roomType, count) => {
    setQuoteData(prev => ({
      ...prev,
      rooms: {
        ...prev.rooms,
        [roomType]: Math.max(0, count)
      }
    }));
    
    if (errors.rooms) {
      setErrors(prev => ({ ...prev, rooms: null }));
    }
  }, [errors.rooms]);

  const toggleExtra = useCallback((extraId) => {
    const extra = EXTRAS[extraId];
    if (!extra) return;

    setQuoteData(prev => {
      const currentExtras = prev.extras;
      const existingIndex = currentExtras.findIndex(e => e.id === extraId);
      
      let newExtras;
      if (existingIndex >= 0) {
        newExtras = currentExtras.filter((_, index) => index !== existingIndex);
      } else {
        newExtras = [...currentExtras, { id: extraId, ...extra }];
      }
      
      return {
        ...prev,
        extras: newExtras
      };
    });
  }, []);

  const updateUrgency = useCallback((urgencyLevel) => {
    const multiplier = URGENCY_MULTIPLIERS[urgencyLevel.toUpperCase()];
    setQuoteData(prev => ({
      ...prev,
      urgency: urgencyLevel
    }));
    
    if (multiplier) {
      setPricing(prev => ({
        ...prev,
        urgencyMultiplier: multiplier.multiplier
      }));
    }
  }, []);

  const updateCustomerInfo = useCallback((field, value) => {
    setQuoteData(prev => ({
      ...prev,
      customerInfo: {
        ...prev.customerInfo,
        [field]: value
      }
    }));
    
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  }, [errors]);

  const updateLocation = useCallback((field, value) => {
    setQuoteData(prev => ({
      ...prev,
      location: {
        ...prev.location,
        [field]: value
      }
    }));
  }, []);

  const calculatePricing = useCallback(() => {
    setIsCalculating(true);
    
    const basePrice = pricing.basePrice;
    const roomsTotal = Object.entries(quoteData.rooms).reduce((sum, [roomType, count]) => {
      const roomPrice = ROOM_TYPES[roomType.toUpperCase()]?.price || 0;
      return sum + (roomPrice * count);
    }, 0);
    
    const extrasTotal = quoteData.extras.reduce((sum, extra) => sum + extra.price, 0);
    const subtotal = basePrice + roomsTotal + extrasTotal;
    const total = Math.round(subtotal * pricing.urgencyMultiplier);
    const gst = Math.round(total * 0.1);
    
    setPricing(prev => ({
      ...prev,
      roomsTotal,
      extrasTotal,
      subtotal,
      gst,
      total
    }));
    
    setIsCalculating(false);
  }, [quoteData, pricing.basePrice, pricing.urgencyMultiplier]);

  const validateQuote = useCallback(() => {
    const flattenedData = {
      ...quoteData.customerInfo,
      ...quoteData.location,
      cleaningType: quoteData.cleaningType,
      rooms: quoteData.rooms,
      urgency: quoteData.urgency
    };
    
    const validationErrors = validateQuoteForm(flattenedData);
    setErrors(validationErrors || {});
    return !validationErrors;
  }, [quoteData]);

  const submitQuote = useCallback(async () => {
    if (!validateQuote()) {
      return { success: false, errors };
    }

    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const sanitizedData = sanitizeFormData({
        ...quoteData,
        pricing,
        timestamp: new Date().toISOString()
      });

      const response = await fetch(API_ENDPOINTS.quote, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sanitizedData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setSubmitStatus('success');
      setIsSubmitting(false);
      
      return { 
        success: true, 
        data: result,
        quoteId: result.quoteId,
        message: 'Quote submitted successfully! We will contact you within 2 hours.'
      };
      
    } catch (error) {
      setSubmitStatus('error');
      setIsSubmitting(false);
      
      return { 
        success: false, 
        error: error.message,
        message: 'Error submitting quote. Please try again or call us directly.'
      };
    }
  }, [quoteData, pricing, validateQuote, errors]);

  const resetQuote = useCallback(() => {
    setQuoteData({
      cleaningType: '',
      rooms: {
        bedrooms: 0,
        bathrooms: 0,
        kitchens: 0,
        livingRooms: 0,
        diningRooms: 0
      },
      extras: [],
      urgency: 'standard',
      location: { suburb: '', postcode: '' },
      customerInfo: {
        name: '',
        email: '',
        phone: '',
        ndisNumber: '',
        isNDISParticipant: false
      },
      specialRequests: '',
      preferredDate: '',
      preferredTime: ''
    });
    
    setPricing({
      basePrice: 0,
      roomsTotal: 0,
      extrasTotal: 0,
      urgencyMultiplier: 1,
      subtotal: 0,
      gst: 0,
      total: 0
    });
    
    setErrors({});
    setSubmitStatus(null);
  }, []);

  useEffect(() => {
    calculatePricing();
  }, [calculatePricing]);

  return {
    quoteData,
    pricing,
    errors,
    isCalculating,
    isSubmitting,
    submitStatus,
    updateCleaningType,
    updateRoomCount,
    toggleExtra,
    updateUrgency,
    updateCustomerInfo,
    updateLocation,
    calculatePricing,
    validateQuote,
    submitQuote,
    resetQuote,
    isValid: Object.keys(errors).length === 0,
    hasRooms: Object.values(quoteData.rooms).some(count => count > 0),
    totalRooms: Object.values(quoteData.rooms).reduce((sum, count) => sum + count, 0)
  };
};

export default useQuoteCalculator;


