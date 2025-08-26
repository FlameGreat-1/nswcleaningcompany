import { useState, useEffect, useCallback, useMemo } from 'react';
import invoicesService from '../services/invoicesService';
import { useAuth } from './useAuth';

export const useInvoices = (initialFilters = {}) => {
  const { user } = useAuth();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    is_ndis_invoice: null,
    email_sent: null,
    deposit_required: null,
    deposit_paid: null,
    search: '',
    ordering: '-created_at',
    ...initialFilters
  });

  const fetchInvoices = useCallback(async () => {
    if (!user) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        ...filters,
        status: filters.status === 'all' ? undefined : filters.status
      };
      
      const data = await invoicesService.getMyInvoices(params);
      setInvoices(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch invoices');
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  }, [user, filters]);

  const refreshInvoices = useCallback(() => {
    fetchInvoices();
  }, [fetchInvoices]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      status: 'all',
      is_ndis_invoice: null,
      email_sent: null,
      deposit_required: null,
      deposit_paid: null,
      search: '',
      ordering: '-created_at'
    });
  }, []);

  const downloadInvoice = useCallback(async (invoiceId) => {
    try {
      await invoicesService.downloadInvoicePDF(invoiceId);
      return { success: true };
    } catch (err) {
      return { 
        success: false, 
        error: err.response?.data?.message || 'Failed to download invoice' 
      };
    }
  }, []);

  const resendInvoiceEmail = useCallback(async (invoiceId) => {
    try {
      const result = await invoicesService.resendInvoiceEmail(invoiceId);
      
      setInvoices(prev => {
        const prevArray = Array.isArray(prev) ? prev : [];
        return prevArray.map(invoice => 
          invoice.id === invoiceId 
            ? { ...invoice, email_sent: true, email_sent_at: new Date().toISOString() }
            : invoice
        );
      });
      
      return { success: true, message: result.message };
    } catch (err) {
      return { 
        success: false, 
        error: err.response?.data?.message || 'Failed to resend invoice email' 
      };
    }
  }, []);

  const filteredInvoices = useMemo(() => {
    if (!invoices || !Array.isArray(invoices) || invoices.length === 0) return [];
    
    let result = [...invoices];
    
    if (filters.search) {
      result = invoicesService.searchInvoices(result, filters.search);
      result = Array.isArray(result) ? result : [];
    }
    
    if (filters.status && filters.status !== 'all') {
      result = invoicesService.filterInvoicesByStatus(result, filters.status);
      result = Array.isArray(result) ? result : [];
    }
    
    if (filters.is_ndis_invoice !== null) {
      result = invoicesService.filterInvoicesByNDIS(result, filters.is_ndis_invoice);
      result = Array.isArray(result) ? result : [];
    }
    
    if (filters.email_sent !== null) {
      result = Array.isArray(result) ? result.filter(invoice => invoice.email_sent === filters.email_sent) : [];
    }

    if (filters.deposit_required !== null) {
      result = Array.isArray(result) ? result.filter(invoice => 
        invoicesService.requiresDeposit(invoice) === filters.deposit_required
      ) : [];
    }

    if (filters.deposit_paid !== null) {
      result = Array.isArray(result) ? result.filter(invoice => 
        invoicesService.isDepositPaid(invoice) === filters.deposit_paid
      ) : [];
    }
    
    return invoicesService.sortInvoices(Array.isArray(result) ? result : [], filters.ordering);
  }, [invoices, filters.search, filters.status, filters.is_ndis_invoice, filters.email_sent, filters.deposit_required, filters.deposit_paid, filters.ordering]);

  const invoiceStats = useMemo(() => {
    if (!invoices || !Array.isArray(invoices) || invoices.length === 0) {
      return {
        total: 0,
        draft: 0,
        sent: 0,
        paid: 0,
        overdue: 0,
        ndis: 0,
        totalAmount: 0,
        overdueAmount: 0,
        depositsRequired: 0,
        depositsPaid: 0,
        depositsPending: 0,
        totalDepositAmount: 0
      };
    }

    const stats = {
      total: invoices.length,
      draft: 0,
      sent: 0,
      paid: 0,
      overdue: 0,
      ndis: 0,
      totalAmount: 0,
      overdueAmount: 0,
      depositsRequired: 0,
      depositsPaid: 0,
      depositsPending: 0,
      totalDepositAmount: 0
    };
    
    invoices.forEach(invoice => {
      stats[invoice.status] = (stats[invoice.status] || 0) + 1;
      stats.totalAmount += parseFloat(invoice.total_amount || 0);
      
      if (invoice.is_ndis_invoice) {
        stats.ndis += 1;
      }
      
      if (invoicesService.isInvoiceOverdue(invoice.due_date) && invoice.status !== 'paid') {
        stats.overdueAmount += parseFloat(invoice.total_amount || 0);
      }

      if (invoicesService.requiresDeposit(invoice)) {
        stats.depositsRequired += 1;
        stats.totalDepositAmount += invoicesService.getDepositAmount(invoice);
        
        if (invoicesService.isDepositPaid(invoice)) {
          stats.depositsPaid += 1;
        } else {
          stats.depositsPending += 1;
        }
      }
    });
    
    return stats;
  }, [invoices]);

  const overdueInvoices = useMemo(() => {
    if (!invoices || !Array.isArray(invoices) || invoices.length === 0) return [];
    return invoices.filter(invoice => 
      invoicesService.isInvoiceOverdue(invoice.due_date) && 
      invoice.status !== 'paid' && 
      invoice.status !== 'cancelled'
    );
  }, [invoices]);

  const recentInvoices = useMemo(() => {
    if (!invoices || !Array.isArray(invoices) || invoices.length === 0) return [];
    return invoicesService.sortInvoices([...invoices], '-created_at').slice(0, 5);
  }, [invoices]);

  const ndisInvoices = useMemo(() => {
    if (!invoices || !Array.isArray(invoices) || invoices.length === 0) return [];
    return invoices.filter(invoice => invoice.is_ndis_invoice);
  }, [invoices]);

  const depositInvoices = useMemo(() => {
    if (!invoices || !Array.isArray(invoices) || invoices.length === 0) return [];
    return invoices.filter(invoice => invoicesService.requiresDeposit(invoice));
  }, [invoices]);

  const pendingDepositInvoices = useMemo(() => {
    if (!invoices || !Array.isArray(invoices) || invoices.length === 0) return [];
    return invoices.filter(invoice => 
      invoicesService.requiresDeposit(invoice) && 
      !invoicesService.isDepositPaid(invoice)
    );
  }, [invoices]);

  const getInvoiceById = useCallback((invoiceId) => {
    if (!invoices || !Array.isArray(invoices) || invoices.length === 0) return null;
    return invoices.find(invoice => invoice.id === invoiceId);
  }, [invoices]);

  const hasInvoices = useMemo(() => {
    return Array.isArray(invoices) && invoices.length > 0;
  }, [invoices]);

  const hasOverdueInvoices = useMemo(() => {
    return Array.isArray(overdueInvoices) && overdueInvoices.length > 0;
  }, [overdueInvoices]);

  const hasNDISInvoices = useMemo(() => {
    return Array.isArray(ndisInvoices) && ndisInvoices.length > 0;
  }, [ndisInvoices]);

  const hasDepositInvoices = useMemo(() => {
    return Array.isArray(depositInvoices) && depositInvoices.length > 0;
  }, [depositInvoices]);

  const hasPendingDeposits = useMemo(() => {
    return Array.isArray(pendingDepositInvoices) && pendingDepositInvoices.length > 0;
  }, [pendingDepositInvoices]);

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]);

  return {
    invoices: filteredInvoices,
    allInvoices: invoices,
    loading,
    error,
    filters,
    invoiceStats,
    overdueInvoices,
    recentInvoices,
    ndisInvoices,
    depositInvoices,
    pendingDepositInvoices,
    hasInvoices,
    hasOverdueInvoices,
    hasNDISInvoices,
    hasDepositInvoices,
    hasPendingDeposits,
    fetchInvoices,
    refreshInvoices,
    updateFilters,
    clearFilters,
    downloadInvoice,
    resendInvoiceEmail,
    getInvoiceById
  };
};

export const useInvoiceDetail = (invoiceId) => {
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchInvoiceDetail = useCallback(async () => {
    if (!invoiceId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await invoicesService.getInvoiceDetail(invoiceId);
      setInvoice(data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch invoice details');
    } finally {
      setLoading(false);
    }
  }, [invoiceId]);

  const downloadInvoice = useCallback(async () => {
    if (!invoice) return { success: false, error: 'No invoice data' };
    
    try {
      await invoicesService.downloadInvoicePDF(invoice.id);
      return { success: true };
    } catch (err) {
      return { 
        success: false, 
        error: err.response?.data?.message || 'Failed to download invoice' 
      };
    }
  }, [invoice]);

  const resendEmail = useCallback(async () => {
    if (!invoice) return { success: false, error: 'No invoice data' };
    
    try {
      const result = await invoicesService.resendInvoiceEmail(invoice.id);
      setInvoice(prev => ({ 
        ...prev, 
        email_sent: true, 
        email_sent_at: new Date().toISOString() 
      }));
      return { success: true, message: result.message };
    } catch (err) {
      return { 
        success: false, 
        error: err.response?.data?.message || 'Failed to resend invoice email' 
      };
    }
  }, [invoice]);

  const invoiceSummary = useMemo(() => {
    return invoice ? invoicesService.getInvoiceSummary(invoice) : null;
  }, [invoice]);

  const invoiceItems = useMemo(() => {
    return invoice ? invoicesService.getInvoiceItems(invoice) : [];
  }, [invoice]);

  const ndisInfo = useMemo(() => {
    return invoice ? invoicesService.getNDISParticipantInfo(invoice) : null;
  }, [invoice]);

  const depositInfo = useMemo(() => {
    return invoice ? invoicesService.getDepositInfo(invoice) : null;
  }, [invoice]);

  const servicePeriod = useMemo(() => {
    return invoice ? invoicesService.getServicePeriod(invoice) : null;
  }, [invoice]);

  useEffect(() => {
    fetchInvoiceDetail();
  }, [fetchInvoiceDetail]);

  return {
    invoice,
    loading,
    error,
    invoiceSummary,
    invoiceItems,
    ndisInfo,
    depositInfo,
    servicePeriod,
    fetchInvoiceDetail,
    downloadInvoice,
    resendEmail
  };
};

export const useNDISInvoices = () => {
  const [ndisInvoices, setNdisInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchNDISInvoices = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await invoicesService.getNDISInvoices(params);
      setNdisInvoices(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch NDIS invoices');
      setNdisInvoices([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const checkCompliance = useCallback(async (invoiceId) => {
    try {
      const result = await invoicesService.checkNDISCompliance(invoiceId);
      return { success: true, data: result };
    } catch (err) {
      return { 
        success: false, 
        error: err.response?.data?.message || 'Failed to check NDIS compliance' 
      };
    }
  }, []);

  useEffect(() => {
    fetchNDISInvoices();
  }, [fetchNDISInvoices]);

  return {
    ndisInvoices,
    loading,
    error,
    fetchNDISInvoices,
    checkCompliance
  };
};
