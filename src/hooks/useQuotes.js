import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useCallback, useRef } from 'react';
import quotesService from '../services/quotesService.js';

const useQuotes = (type = 'my', params = {}, autoFetch = true) => {
  const queryClient = useQueryClient();
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    page: 1,
    totalPages: 1
  });

  const stableParams = useRef(params);
  const stableType = useRef(type);
  
  useEffect(() => {
    stableParams.current = params;
    stableType.current = type;
  }, [params, type]);

  const serviceMap = {
    my: quotesService.getMyQuotes,
    draft: quotesService.getDraftQuotes,
    submitted: quotesService.getSubmittedQuotes,
    approved: quotesService.getApprovedQuotes,
    rejected: quotesService.getRejectedQuotes
  };

  const queryKey = ['quotes', stableType.current, JSON.stringify(stableParams.current)];

  const {
    data: quotesData,
    isLoading,
    isError,
    error: queryError,
    refetch: queryRefetch
  } = useQuery({
    queryKey,
    queryFn: async () => {
      if (!serviceMap[stableType.current]) {
        throw new Error(`Invalid quote type: ${stableType.current}`);
      }
      
      const response = await serviceMap[stableType.current]({
        ...stableParams.current,
        timestamp: Date.now()
      });
      
      return response;
    },
    enabled: autoFetch,
    refetchOnMount: true,
    refetchInterval: 30000,
    refetchOnWindowFocus: true,
    staleTime: 0,
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  const quotes = quotesData?.results || quotesData || [];
  const error = queryError ? (queryError.response?.data?.message || queryError.message || 'Failed to fetch quotes') : null;

  useEffect(() => {
    if (quotesData) {
      if (quotesData.results) {
        setPagination({
          count: quotesData.count,
          next: quotesData.next,
          previous: quotesData.previous,
          page: Math.ceil((stableParams.current.offset || 0) / (stableParams.current.limit || 20)) + 1,
          totalPages: Math.ceil(quotesData.count / (stableParams.current.limit || 20))
        });
      } else {
        setPagination({
          count: Array.isArray(quotesData) ? quotesData.length : 0,
          next: null,
          previous: null,
          page: 1,
          totalPages: 1
        });
      }
    }
  }, [quotesData]);

  const refetch = useCallback((newParams = {}) => {
    const updatedParams = { ...stableParams.current, ...newParams };
    stableParams.current = updatedParams;
    return queryRefetch();
  }, [queryRefetch]);

  const forceRefetch = useCallback(() => {
    return queryRefetch();
  }, [queryRefetch]);

  const loadMore = useCallback(() => {
    if (pagination.next && !isLoading) {
      const currentOffset = (pagination.page - 1) * (stableParams.current.limit || 20);
      const nextOffset = currentOffset + (stableParams.current.limit || 20);
      return refetch({ offset: nextOffset });
    }
  }, [pagination, isLoading, refetch]);

  const goToPage = useCallback((page) => {
    const offset = (page - 1) * (stableParams.current.limit || 20);
    return refetch({ offset });
  }, [refetch]);

  const updateQuoteInList = useCallback((updatedQuote) => {
    queryClient.setQueryData(queryKey, (oldData) => {
      if (!oldData) return oldData;
      
      const results = oldData.results || oldData;
      const updatedResults = Array.isArray(results) ? results.map(quote => 
        quote.id === updatedQuote.id ? { ...quote, ...updatedQuote } : quote
      ) : [updatedQuote];
      
      if (oldData.results) {
        return { ...oldData, results: updatedResults };
      }
      return updatedResults;
    });
  }, [queryClient, queryKey]);

  const removeQuoteFromList = useCallback((quoteId) => {
    queryClient.setQueryData(queryKey, (oldData) => {
      if (!oldData) return oldData;
      
      const results = oldData.results || oldData;
      const filteredResults = Array.isArray(results) ? results.filter(quote => quote.id !== quoteId) : [];
      
      if (oldData.results) {
        return { 
          ...oldData, 
          results: filteredResults,
          count: Math.max(0, oldData.count - 1)
        };
      }
      return filteredResults;
    });
  }, [queryClient, queryKey]);

  const addQuoteToList = useCallback((newQuote) => {
    queryClient.setQueryData(queryKey, (oldData) => {
      if (!oldData) return { results: [newQuote], count: 1 };
      
      const results = oldData.results || oldData;
      const quoteExists = Array.isArray(results) && results.some(quote => quote.id === newQuote.id);
      
      let updatedResults;
      if (quoteExists) {
        updatedResults = Array.isArray(results) ? results.map(quote => 
          quote.id === newQuote.id ? { ...quote, ...newQuote } : quote
        ) : [newQuote];
      } else {
        updatedResults = Array.isArray(results) ? [newQuote, ...results] : [newQuote];
      }
      
      if (oldData.results) {
        return { 
          ...oldData, 
          results: updatedResults,
          count: quoteExists ? oldData.count : oldData.count + 1
        };
      }
      return updatedResults;
    });
  }, [queryClient, queryKey]);

  const searchQuotes = useCallback(async (searchTerm, filters = {}) => {
    try {
      const response = await quotesService.searchQuotes(searchTerm, { ...filters, timestamp: Date.now() });
      const searchResults = Array.isArray(response) ? response : response.results || [];
      
      queryClient.setQueryData(['quotes', 'search', searchTerm, JSON.stringify(filters)], searchResults);
      
      return searchResults;
    } catch (err) {
      console.error('Search failed:', err);
      throw err;
    }
  }, [queryClient]);

  const filterByStatus = useCallback((status) => {
    return refetch({ status });
  }, [refetch]);

  const filterByCleaningType = useCallback((cleaningType) => {
    return refetch({ cleaning_type: cleaningType });
  }, [refetch]);

  const filterByDateRange = useCallback((startDate, endDate) => {
    return refetch({ 
      created_at__gte: startDate,
      created_at__lte: endDate 
    });
  }, [refetch]);

  useEffect(() => {
    if (autoFetch) {
      const handleVisibilityChange = () => {
        if (document.visibilityState === 'visible') {
          forceRefetch();
        }
      };
      
      document.addEventListener('visibilitychange', handleVisibilityChange);
      
      window.quotesRefreshInterval = window.setInterval(() => {
        if (document.visibilityState === 'visible') {
          forceRefetch();
        }
      }, 30000);
      
      return () => {
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        if (window.quotesRefreshInterval) {
          clearInterval(window.quotesRefreshInterval);
          window.quotesRefreshInterval = null;
        }
      };
    }
  }, [autoFetch, forceRefetch]);

  return {
    quotes,
    loading: isLoading,
    error,
    pagination,
    refetch,
    forceRefetch,
    loadMore,
    goToPage,
    updateQuoteInList,
    removeQuoteFromList,
    addQuoteToList,
    searchQuotes,
    filterByStatus,
    filterByCleaningType,
    filterByDateRange,
    hasMore: !!pagination.next,
    isEmpty: quotes.length === 0 && !isLoading,
    totalCount: pagination.count
  };
};

export default useQuotes;
