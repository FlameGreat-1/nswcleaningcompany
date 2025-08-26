import api from './api.js';
import { API_ENDPOINTS } from './apiConfig.js';

class QuotesService {
  async getMyQuotes(params = {}) {
    const cleanParams = {};
    
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        cleanParams[key] = params[key];
      }
    });
    
    const response = await api.get(API_ENDPOINTS.QUOTES.MY_QUOTES, { params: cleanParams });
    return response.data;
  }

  async getQuote(id) {
    const response = await api.get(`${API_ENDPOINTS.QUOTES.BASE}${id}/`);
    return response.data;
  }

  async createQuote(data) {
    const response = await api.post(API_ENDPOINTS.QUOTES.BASE, data);
    return response.data;
  }

  async updateQuote(id, data) {
    const response = await api.patch(`${API_ENDPOINTS.QUOTES.BASE}${id}/`, data);
    return response.data;
  }

  async submitQuote(id) {
    const response = await api.post(`${API_ENDPOINTS.QUOTES.BASE}${id}/submit/`);
    return response.data;
  }

  async cancelQuote(id) {
    const response = await api.post(`${API_ENDPOINTS.QUOTES.BASE}${id}/cancel/`);
    return response.data;
  }

  async downloadQuotePDF(id) {
    const response = await api.get(`${API_ENDPOINTS.QUOTES.BASE}${id}/pdf/`, {
      responseType: 'blob'
    });
    return response.data;
  }

  async calculateQuote(data) {
    const response = await api.post(API_ENDPOINTS.QUOTES.CALCULATOR, data);
    return response.data;
  } 

  async duplicateQuote(id, data = {}) {
    const response = await api.post(`${API_ENDPOINTS.QUOTES.BASE}${id}/duplicate/`, data);
    return response.data;
  }

  async getQuoteItems(quoteId, params = {}) {
    const response = await api.get(API_ENDPOINTS.QUOTES.ITEMS, { 
      params: { quote_id: quoteId, ...params } 
    });
    return response.data;
  }

  async createQuoteItem(data) {
    const response = await api.post(API_ENDPOINTS.QUOTES.ITEMS, data);
    return response.data;
  }

  async updateQuoteItem(id, data) {
    const response = await api.patch(`${API_ENDPOINTS.QUOTES.ITEMS}${id}/`, data);
    return response.data;
  }

  async deleteQuoteItem(id) {
    const response = await api.delete(`${API_ENDPOINTS.QUOTES.ITEMS}${id}/`);
    return response.data;
  }

  async getQuoteAttachments(quoteId, params = {}) {
    const response = await api.get(API_ENDPOINTS.QUOTES.ATTACHMENTS, { 
      params: { quote_id: quoteId, ...params } 
    });
    return response.data;
  }

  async uploadQuoteAttachment(data) {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      formData.append(key, data[key]);
    });
    
    const response = await api.post(API_ENDPOINTS.QUOTES.ATTACHMENTS, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteQuoteAttachment(id) {
    const response = await api.delete(`${API_ENDPOINTS.QUOTES.ATTACHMENTS}${id}/`);
    return response.data;
  }

  async downloadQuoteAttachment(id) {
    const response = await api.get(`${API_ENDPOINTS.QUOTES.ATTACHMENTS}${id}/download/`, {
      responseType: 'blob'
    });
    return response.data;
  }

  async getServices(params = {}) {
    const response = await api.get(API_ENDPOINTS.SERVICES.LIST, { params });
    return response.data;
  }

  async getService(id) {
    const response = await api.get(`${API_ENDPOINTS.SERVICES.BASE}${id}/`);
    return response.data;
  }

  async getServiceAddons(serviceId, params = {}) {
    const response = await api.get(API_ENDPOINTS.SERVICES.ADDONS, { 
      params: { 
        service: serviceId,
        ...params 
      } 
    });
    return response.data;
  } 

  async getQuoteAddons(quoteId, params = {}) {
    const response = await api.get(`${API_ENDPOINTS.QUOTES.BASE}${quoteId}/addons/`, { 
      params: { ...params } 
    });
    return response.data;
  }  

  async searchQuotes(searchTerm, filters = {}) {
    const params = {
      search: searchTerm,
      ...filters
    };
    return this.getMyQuotes(params);
  }

  async getQuotesByStatus(status, params = {}) {
    return this.getMyQuotes({ status, ...params });
  }

  async getDraftQuotes(params = {}) {
    return this.getQuotesByStatus('draft', params);
  }

  async getSubmittedQuotes(params = {}) {
    return this.getQuotesByStatus('submitted', params);
  }

  async getApprovedQuotes(params = {}) {
    return this.getQuotesByStatus('approved', params);
  }

  async getRejectedQuotes(params = {}) {
    return this.getQuotesByStatus('rejected', params);
  }

  createDownloadUrl(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  async downloadQuotePDFWithFilename(id, filename) {
    try {
      const blob = await this.downloadQuotePDF(id);
      this.createDownloadUrl(blob, filename || `quote-${id}.pdf`);
      return true;
    } catch (error) {
      console.error('Download failed:', error);
      return false;
    }
  }

  async downloadAttachmentWithFilename(id, filename) {
    try {
      const blob = await this.downloadQuoteAttachment(id);
      this.createDownloadUrl(blob, filename || `attachment-${id}`);
      return true;
    } catch (error) {
      console.error('Download failed:', error);
      return false;
    }
  }

  async getQuoteRevisions(quoteId, params = {}) {
    const response = await api.get(API_ENDPOINTS.QUOTES.REVISIONS, { 
      params: { quote_id: quoteId, ...params } 
    });
    return response.data;
  }

  async getQuoteTemplates() {
    try {
      const response = await api.get(API_ENDPOINTS.QUOTES.TEMPLATES);
      return response.data;
    } catch (error) {
      console.error('Error fetching quote templates:', error);
      return [];
    }
  }  
  
}

export default new QuotesService();
