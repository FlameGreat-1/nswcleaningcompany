import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback } from 'react';
import quotesService from '../services/quotesService.js';

const useQuoteActions = () => {
  const [error, setError] = useState(null);
  const queryClient = useQueryClient();

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const createQuoteMutation = useMutation({
    mutationFn: (quoteData) => quotesService.createQuote(quoteData),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to create quote';
      setError(errorMessage);
    },
    onSuccess: (data) => {

      queryClient.invalidateQueries({ 
        predicate: (query) => query.queryKey[0] === 'quotes' 
      });
      
      if (data?.id) {
        queryClient.invalidateQueries({ queryKey: ['quote', data.id] });
      }
    }
  });  

  const updateQuoteMutation = useMutation({
    mutationFn: ({ quoteId, updateData }) => quotesService.updateQuote(quoteId, updateData),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to update quote';
      setError(errorMessage);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      if (data?.id) {
        queryClient.invalidateQueries({ queryKey: ['quote', data.id] });
      }
    }
  });

  const submitQuoteMutation = useMutation({
    mutationFn: (quoteId) => quotesService.submitQuote(quoteId),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to submit quote';
      setError(errorMessage);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      if (data?.id) {
        queryClient.invalidateQueries({ queryKey: ['quote', data.id] });
      }
    }
  });

  const cancelQuoteMutation = useMutation({
    mutationFn: (quoteId) => quotesService.cancelQuote(quoteId),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to cancel quote';
      setError(errorMessage);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      if (data?.id) {
        queryClient.invalidateQueries({ queryKey: ['quote', data.id] });
      }
    }
  });

  const duplicateQuoteMutation = useMutation({
    mutationFn: ({ quoteId, modifications }) => quotesService.duplicateQuote(quoteId, modifications),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to duplicate quote';
      setError(errorMessage);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] });
      return data; 
    }
  });
  
  const calculateQuoteMutation = useMutation({
    mutationFn: (calculationData) => quotesService.calculateQuote(calculationData),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to calculate quote';
      setError(errorMessage);
    }
  });

  const uploadAttachmentMutation = useMutation({
    mutationFn: (attachmentData) => quotesService.uploadQuoteAttachment(attachmentData),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to upload attachment';
      setError(errorMessage);
    },
    onSuccess: (data) => {
      if (data?.quote) {
        queryClient.invalidateQueries({ queryKey: ['quote', data.quote] });
        queryClient.invalidateQueries({ queryKey: ['quote-attachments', data.quote] });
      }
    }
  });

  const deleteAttachmentMutation = useMutation({
    mutationFn: (attachmentId) => quotesService.deleteQuoteAttachment(attachmentId),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to delete attachment';
      setError(errorMessage);
    },
    onSuccess: (_, variables, context) => {
      if (context?.quoteId) {
        queryClient.invalidateQueries({ queryKey: ['quote', context.quoteId] });
        queryClient.invalidateQueries({ queryKey: ['quote-attachments', context.quoteId] });
      }
    }
  });

  const createQuoteItemMutation = useMutation({
    mutationFn: (itemData) => quotesService.createQuoteItem(itemData),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to create quote item';
      setError(errorMessage);
    },
    onSuccess: (data) => {
      if (data?.quote) {
        queryClient.invalidateQueries({ queryKey: ['quote', data.quote] });
        queryClient.invalidateQueries({ queryKey: ['quote-items', data.quote] });
      }
    }
  });

  const updateQuoteItemMutation = useMutation({
    mutationFn: ({ itemId, itemData }) => quotesService.updateQuoteItem(itemId, itemData),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to update quote item';
      setError(errorMessage);
    },
    onSuccess: (data) => {
      if (data?.quote) {
        queryClient.invalidateQueries({ queryKey: ['quote', data.quote] });
        queryClient.invalidateQueries({ queryKey: ['quote-items', data.quote] });
      }
    }
  });

  const deleteQuoteItemMutation = useMutation({
    mutationFn: (itemId) => quotesService.deleteQuoteItem(itemId),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to delete quote item';
      setError(errorMessage);
    },
    onSuccess: (_, variables, context) => {
      if (context?.quoteId) {
        queryClient.invalidateQueries({ queryKey: ['quote', context.quoteId] });
        queryClient.invalidateQueries({ queryKey: ['quote-items', context.quoteId] });
      }
    }
  });

  const getServicesMutation = useMutation({
    mutationFn: (params) => quotesService.getServices(params),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to get services';
      setError(errorMessage);
    }
  });

  const getServiceMutation = useMutation({
    mutationFn: (serviceId) => quotesService.getService(serviceId),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to get service';
      setError(errorMessage);
    }
  });

  const getServiceAddonsMutation = useMutation({
    mutationFn: ({ serviceId, params }) => quotesService.getServiceAddons(serviceId, params),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to get service addons';
      setError(errorMessage);
    }
  });

  const searchQuotesMutation = useMutation({
    mutationFn: ({ searchTerm, filters }) => quotesService.searchQuotes(searchTerm, filters),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to search quotes';
      setError(errorMessage);
    }
  });

  const getQuotesByStatusMutation = useMutation({
    mutationFn: ({ status, params }) => quotesService.getQuotesByStatus(status, params),
    onError: (err) => {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to get quotes by status';
      setError(errorMessage);
    }
  });

  const createQuote = async (quoteData) => {
    clearError();
    try {
      return await createQuoteMutation.mutateAsync(quoteData);
    } catch (err) {
      throw err;
    }
  };

  const updateQuote = async (quoteId, updateData) => {
    clearError();
    try {
      return await updateQuoteMutation.mutateAsync({ quoteId, updateData });
    } catch (err) {
      throw err;
    }
  };

  const submitQuote = async (quoteId) => {
    clearError();
    try {
      return await submitQuoteMutation.mutateAsync(quoteId);
    } catch (err) {
      throw err;
    }
  };

  const cancelQuote = async (quoteId) => {
    clearError();
    try {
      return await cancelQuoteMutation.mutateAsync(quoteId);
    } catch (err) {
      throw err;
    }
  };

  const duplicateQuote = async (quoteId, modifications = {}) => {
    clearError();
    try {
      const result = await duplicateQuoteMutation.mutateAsync({ quoteId, modifications });
      console.log("Duplicate quote result:", result); 
      return result; 
    } catch (err) {
      throw err;
    }
  };

  const downloadPDF = async (quoteId, filename) => {
    clearError();
    try {
      const success = await quotesService.downloadQuotePDFWithFilename(quoteId, filename || `quote-${quoteId}.pdf`);
      if (!success) {
        throw new Error('Download failed');
      }
      return true;
    } catch (err) {
      setError('Failed to download PDF');
      throw err;
    }
  };

  const calculateQuote = async (calculationData) => {
    clearError();
    try {
      return await calculateQuoteMutation.mutateAsync(calculationData);
    } catch (err) {
      throw err;
    }
  };

  const uploadAttachment = async (quoteId, file, attachmentType = 'image', title = '', description = '') => {
    clearError();
    try {
      return await uploadAttachmentMutation.mutateAsync({
        quote: quoteId,
        file,
        attachment_type: attachmentType,
        title,
        description,
        is_public: true
      });
    } catch (err) {
      throw err;
    }
  };

  const deleteAttachment = async (attachmentId, quoteId) => {
    clearError();
    try {
      return await deleteAttachmentMutation.mutateAsync(attachmentId, {
        onMutate: () => {
          return { quoteId };
        }
      });
    } catch (err) {
      throw err;
    }
  };

  const downloadAttachment = async (attachmentId, filename) => {
    clearError();
    try {
      const success = await quotesService.downloadAttachmentWithFilename(attachmentId, filename);
      if (!success) {
        throw new Error('Download failed');
      }
      return true;
    } catch (err) {
      setError('Failed to download attachment');
      throw err;
    }
  };

  const createQuoteItem = async (quoteId, itemData) => {
    clearError();
    try {
      return await createQuoteItemMutation.mutateAsync({
        quote: quoteId,
        ...itemData
      });
    } catch (err) {
      throw err;
    }
  };

  const updateQuoteItem = async (itemId, itemData) => {
    clearError();
    try {
      return await updateQuoteItemMutation.mutateAsync({ itemId, itemData });
    } catch (err) {
      throw err;
    }
  };

  const deleteQuoteItem = async (itemId, quoteId) => {
    clearError();
    try {
      return await deleteQuoteItemMutation.mutateAsync(itemId, {
        onMutate: () => {
          return { quoteId };
        }
      });
    } catch (err) {
      throw err;
    }
  };

  const getServices = async (params = {}) => {
    clearError();
    try {
      return await getServicesMutation.mutateAsync(params);
    } catch (err) {
      throw err;
    }
  };

  const getService = async (serviceId) => {
    clearError();
    try {
      return await getServiceMutation.mutateAsync(serviceId);
    } catch (err) {
      throw err;
    }
  };

  const getServiceAddons = async (serviceId, params = {}) => {
    clearError();
    try {
      return await getServiceAddonsMutation.mutateAsync({ serviceId, params });
    } catch (err) {
      throw err;
    }
  };

  const searchQuotes = async (searchTerm, filters = {}) => {
    clearError();
    try {
      return await searchQuotesMutation.mutateAsync({ searchTerm, filters });
    } catch (err) {
      throw err;
    }
  };

  const getQuotesByStatus = async (status, params = {}) => {
    clearError();
    try {
      return await getQuotesByStatusMutation.mutateAsync({ status, params });
    } catch (err) {
      throw err;
    }
  };

  const validateQuoteData = (quoteData) => {
    const errors = {};
    
    if (!quoteData.service) {
      errors.service = 'Service is required';
    }
    
    if (!quoteData.cleaning_type) {
      errors.cleaning_type = 'Cleaning type is required';
    }
    
    if (!quoteData.property_address) {
      errors.property_address = 'Property address is required';
    }
    
    if (!quoteData.postcode) {
      errors.postcode = 'Postcode is required';
    }
    
    if (!quoteData.suburb) {
      errors.suburb = 'Suburb is required';
    }
    
    if (!quoteData.state) {
      errors.state = 'State is required';
    }
    
    if (!quoteData.number_of_rooms || quoteData.number_of_rooms < 1) {
      errors.number_of_rooms = 'Number of rooms must be at least 1';
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  };

  return {
    loading: createQuoteMutation.isPending || 
             updateQuoteMutation.isPending || 
             submitQuoteMutation.isPending || 
             cancelQuoteMutation.isPending || 
             duplicateQuoteMutation.isPending || 
             calculateQuoteMutation.isPending || 
             uploadAttachmentMutation.isPending || 
             deleteAttachmentMutation.isPending || 
             createQuoteItemMutation.isPending || 
             updateQuoteItemMutation.isPending || 
             deleteQuoteItemMutation.isPending || 
             getServicesMutation.isPending || 
             getServiceMutation.isPending || 
             getServiceAddonsMutation.isPending || 
             searchQuotesMutation.isPending || 
             getQuotesByStatusMutation.isPending,
    error,
    clearError,
    createQuote,
    updateQuote,
    submitQuote,
    cancelQuote,
    duplicateQuote,
    downloadPDF,
    calculateQuote,
    uploadAttachment,
    deleteAttachment,
    downloadAttachment,
    createQuoteItem,
    updateQuoteItem,
    deleteQuoteItem,
    getServices,
    getService,
    getServiceAddons,
    searchQuotes,
    getQuotesByStatus,
    validateQuoteData
  };
};

export default useQuoteActions;
