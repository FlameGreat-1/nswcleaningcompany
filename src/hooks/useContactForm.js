import { useState, useCallback } from 'react';
import { validateContactForm, sanitizeFormData } from '../utils/validation.js';
import { API_ENDPOINTS } from '../utils/constants.js';

const useContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    suburb: '',
    message: '',
    serviceType: '',
    preferredContact: 'email'
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const updateField = useCallback((field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  }, [errors]);

  const updateFormData = useCallback((data) => {
    setFormData(prev => ({
      ...prev,
      ...data
    }));
  }, []);

  const validateForm = useCallback(() => {
    const sanitizedData = sanitizeFormData(formData);
    const validationErrors = validateContactForm(sanitizedData);
    
    setErrors(validationErrors || {});
    return !validationErrors;
  }, [formData]);

  const resetForm = useCallback(() => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      suburb: '',
      message: '',
      serviceType: '',
      preferredContact: 'email'
    });
    setErrors({});
    setSubmitStatus(null);
  }, []);

  const submitForm = useCallback(async () => {
    if (!validateForm()) {
      return { success: false, errors };
    }

    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const sanitizedData = sanitizeFormData(formData);
      
      const response = await fetch(API_ENDPOINTS.contact, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...sanitizedData,
          timestamp: new Date().toISOString(),
          source: 'website_contact_form'
        })
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
        message: 'Thank you for your message. We will get back to you within 24 hours.'
      };
      
    } catch (error) {
      setSubmitStatus('error');
      setIsSubmitting(false);
      
      return { 
        success: false, 
        error: error.message,
        message: 'Sorry, there was an error sending your message. Please try again or call us directly.'
      };
    }
  }, [formData, validateForm, errors]);

  const hasErrors = useCallback(() => {
    return Object.keys(errors).length > 0;
  }, [errors]);

  const isFormValid = useCallback(() => {
    const requiredFields = ['name', 'email', 'phone', 'message'];
    return requiredFields.every(field => formData[field]?.trim()) && !hasErrors();
  }, [formData, hasErrors]);

  const getFieldError = useCallback((field) => {
    return errors[field] || null;
  }, [errors]);

  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  const setFieldError = useCallback((field, error) => {
    setErrors(prev => ({
      ...prev,
      [field]: error
    }));
  }, []);

  return {
    formData,
    errors,
    isSubmitting,
    submitStatus,
    updateField,
    updateFormData,
    validateForm,
    resetForm,
    submitForm,
    hasErrors,
    isFormValid,
    getFieldError,
    clearErrors,
    setFieldError,
    isSuccess: submitStatus === 'success',
    isError: submitStatus === 'error'
  };
};

export default useContactForm;
