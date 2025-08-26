import api from './api';
import { API_ENDPOINTS } from './apiConfig';

class InvoicesService {
  async getMyInvoices(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.search) queryParams.append('search', params.search);
    if (params.ordering) queryParams.append('ordering', params.ordering);
    if (params.is_ndis_invoice !== undefined) queryParams.append('is_ndis_invoice', params.is_ndis_invoice);
    if (params.deposit_required !== undefined) queryParams.append('deposit_required', params.deposit_required);
    if (params.deposit_paid !== undefined) queryParams.append('deposit_paid', params.deposit_paid);
    
    const url = queryParams.toString() 
      ? `${API_ENDPOINTS.INVOICES.MY_INVOICES}?${queryParams.toString()}`
      : API_ENDPOINTS.INVOICES.MY_INVOICES;
    
    const response = await api.get(url);
    return response.data;
  }

  async getInvoiceDetail(invoiceId) {
    const response = await api.get(`${API_ENDPOINTS.INVOICES.BASE}${invoiceId}/`);
    return response.data;
  }

  async downloadInvoicePDF(invoiceId) {
    const response = await api.get(`${API_ENDPOINTS.INVOICES.BASE}${invoiceId}/download/`, {
      responseType: 'blob'
    });
    
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `invoice-${invoiceId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    return true;
  }

  async getNDISInvoices(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.search) queryParams.append('search', params.search);
    if (params.ordering) queryParams.append('ordering', params.ordering);
    
    const url = queryParams.toString() 
      ? `${API_ENDPOINTS.INVOICES.NDIS}?${queryParams.toString()}`
      : API_ENDPOINTS.INVOICES.NDIS;
    
    const response = await api.get(url);
    return response.data;
  }

  async checkNDISCompliance(invoiceId) {
    const response = await api.get(`${API_ENDPOINTS.INVOICES.NDIS}${invoiceId}/compliance-check/`);
    return response.data;
  }

  formatInvoiceAmount(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) {
      return '$0.00';
    }
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  }

  formatInvoiceDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  isInvoiceOverdue(invoice) {
    return invoice.is_overdue || false;
  }

  getDaysOverdue(invoice) {
    return invoice.days_overdue || 0;
  }

  getInvoicePDFUrl(invoice) {
    return invoice.pdf_url || null;
  }

  canDownloadPDF(invoice) {
    return invoice.pdf_file ? true : false;
  }

  getInvoiceItems(invoice) {
    return invoice.items || [];
  }

  calculateInvoiceSubtotal(items) {
    return items.reduce((sum, item) => sum + parseFloat(item.total_price || 0), 0);
  }

  calculateInvoiceGST(items) {
    return items.reduce((sum, item) => {
      return sum + (item.is_taxable ? parseFloat(item.gst_amount || 0) : 0);
    }, 0);
  }

  isNDISInvoice(invoice) {
    return invoice.is_ndis_invoice === true;
  }

  requiresDeposit(invoice) {
    return invoice.requires_deposit === true || invoice.deposit_required === true;
  }

  isDepositPaid(invoice) {
    return invoice.deposit_paid === true;
  }

  getDepositStatus(invoice) {
    if (!this.requiresDeposit(invoice)) return 'not_required';
    return invoice.deposit_status || (this.isDepositPaid(invoice) ? 'paid' : 'pending');
  }

  getDepositAmount(invoice) {
    return parseFloat(invoice.deposit_amount || 0);
  }

  getDepositPercentage(invoice) {
    return parseFloat(invoice.deposit_percentage || 0);
  }

  getRemainingBalance(invoice) {
    return parseFloat(invoice.remaining_balance || 0);
  }

  getFormattedDepositAmount(invoice) {
    return invoice.formatted_deposit_amount || this.formatInvoiceAmount(this.getDepositAmount(invoice));
  }

  getFormattedRemainingBalance(invoice) {
    return invoice.formatted_remaining_balance || this.formatInvoiceAmount(this.getRemainingBalance(invoice));
  }

  getDepositInfo(invoice) {
    if (!this.requiresDeposit(invoice)) return null;
    
    return {
      required: true,
      amount: this.getDepositAmount(invoice),
      percentage: this.getDepositPercentage(invoice),
      formattedAmount: this.getFormattedDepositAmount(invoice),
      status: this.getDepositStatus(invoice),
      isPaid: this.isDepositPaid(invoice),
      paidDate: invoice.deposit_paid_date || null,
      remainingBalance: this.getRemainingBalance(invoice),
      formattedRemainingBalance: this.getFormattedRemainingBalance(invoice)
    };
  }

  getNDISParticipantInfo(invoice) {
    if (!this.isNDISInvoice(invoice)) return null;
    
    return {
      participantName: invoice.participant_name || '',
      ndisNumber: invoice.ndis_number || '',
      serviceStartDate: invoice.service_start_date || null,
      serviceEndDate: invoice.service_end_date || null
    };
  }

  getServicePeriod(invoice) {
    if (!invoice.service_start_date) return 'N/A';
    
    const startDate = this.formatInvoiceDate(invoice.service_start_date);
    const endDate = invoice.service_end_date 
      ? this.formatInvoiceDate(invoice.service_end_date)
      : startDate;
    
    return startDate === endDate ? startDate : `${startDate} - ${endDate}`;
  }

  getInvoiceSummary(invoice) {
    if (!invoice) return {};
    
    const depositInfo = this.getDepositInfo(invoice);
    
    return {
      invoiceNumber: invoice.invoice_number || '',
      clientName: invoice.client_full_name || invoice.client_name || 'Unknown Client',
      totalAmount: this.formatInvoiceAmount(invoice.total_amount),
      subtotal: this.formatInvoiceAmount(invoice.subtotal),
      gstAmount: this.formatInvoiceAmount(invoice.gst_amount),
      dueDate: this.formatInvoiceDate(invoice.due_date),
      invoiceDate: this.formatInvoiceDate(invoice.invoice_date),
      isOverdue: this.isInvoiceOverdue(invoice),
      daysOverdue: this.getDaysOverdue(invoice),
      isNDIS: this.isNDISInvoice(invoice),
      canDownload: this.canDownloadPDF(invoice),
      billingAddress: invoice.billing_address || '',
      serviceAddress: invoice.service_address || '',
      participantName: invoice.participant_name || '',
      ndisNumber: invoice.ndis_number || '',
      servicePeriod: this.getServicePeriod(invoice),
      deposit: depositInfo
    };
  }

  filterInvoicesByNDIS(invoices, isNDIS) {
    if (isNDIS === undefined || isNDIS === null || isNDIS === 'null') return invoices;
    return invoices.filter(invoice => invoice.is_ndis_invoice === (isNDIS === 'true' || isNDIS === true));
  }

  filterInvoicesByDeposit(invoices, depositFilter) {
    if (!depositFilter || depositFilter === 'all') return invoices;
    
    switch (depositFilter) {
      case 'required':
        return invoices.filter(invoice => this.requiresDeposit(invoice));
      case 'paid':
        return invoices.filter(invoice => this.requiresDeposit(invoice) && this.isDepositPaid(invoice));
      case 'pending':
        return invoices.filter(invoice => this.requiresDeposit(invoice) && !this.isDepositPaid(invoice));
      case 'not_required':
        return invoices.filter(invoice => !this.requiresDeposit(invoice));
      default:
        return invoices;
    }
  }

  sortInvoices(invoices, sortBy = '-created_at') {
    const sortedInvoices = [...invoices];
    
    const isDescending = sortBy.startsWith('-');
    const field = isDescending ? sortBy.substring(1) : sortBy;
    
    sortedInvoices.sort((a, b) => {
      let aValue = a[field];
      let bValue = b[field];
      
      if (field.includes('date')) {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }
      
      if (field === 'total_amount' || field === 'deposit_amount') {
        aValue = parseFloat(aValue || 0);
        bValue = parseFloat(bValue || 0);
      }
      
      if (aValue < bValue) return isDescending ? 1 : -1;
      if (aValue > bValue) return isDescending ? -1 : 1;
      return 0;
    });
    
    return sortedInvoices;
  }

  searchInvoices(invoices, searchTerm) {
    if (!searchTerm) return invoices;
    
    const term = searchTerm.toLowerCase();
    return invoices.filter(invoice => 
      invoice.invoice_number?.toLowerCase().includes(term) ||
      invoice.client_full_name?.toLowerCase().includes(term) ||
      invoice.client_name?.toLowerCase().includes(term) ||
      invoice.participant_name?.toLowerCase().includes(term)
    );
  }

  getInvoiceDisplayData(invoice) {
    if (!invoice) return null;
    
    return {
      id: invoice.id,
      invoiceNumber: invoice.invoice_number,
      clientName: invoice.client_full_name || invoice.client_name,
      totalAmount: invoice.total_amount,
      subtotal: invoice.subtotal,
      gstAmount: invoice.gst_amount,
      invoiceDate: invoice.invoice_date,
      dueDate: invoice.due_date,
      billingAddress: invoice.billing_address,
      serviceAddress: invoice.service_address,
      isNDIS: invoice.is_ndis_invoice,
      participantName: invoice.participant_name,
      ndisNumber: invoice.ndis_number,
      serviceStartDate: invoice.service_start_date,
      serviceEndDate: invoice.service_end_date,
      isOverdue: invoice.is_overdue,
      daysOverdue: invoice.days_overdue,
      items: invoice.items || [],
      itemsCount: invoice.items_count || 0,
      pdfFile: invoice.pdf_file,
      createdAt: invoice.created_at,
      depositRequired: invoice.deposit_required,
      depositAmount: invoice.deposit_amount,
      depositPercentage: invoice.deposit_percentage,
      remainingBalance: invoice.remaining_balance,
      depositPaid: invoice.deposit_paid,
      depositPaidDate: invoice.deposit_paid_date,
      requiresDeposit: this.requiresDeposit(invoice),
      depositStatus: this.getDepositStatus(invoice),
      formattedDepositAmount: this.getFormattedDepositAmount(invoice),
      formattedRemainingBalance: this.getFormattedRemainingBalance(invoice),
      depositInfo: this.getDepositInfo(invoice)
    };
  }
}

export default new InvoicesService();
