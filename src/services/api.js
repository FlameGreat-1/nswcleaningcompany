import apiClient from './apiConfig';

class ApiService { 
  async get(url, config = {}) {
    const response = await apiClient.get(url, config);
    return response;
  }

  async post(url, data = {}, config = {}) {
    const response = await apiClient.post(url, data, config);
    return response;
  }

  async put(url, data = {}, config = {}) {
    const response = await apiClient.put(url, data, config);
    return response;
  }

  async patch(url, data = {}, config = {}) {
    const response = await apiClient.patch(url, data, config);
    return response;
  }

  async delete(url, config = {}) {
    const response = await apiClient.delete(url, config);
    return response;
  }

  async getSafe(url, config = {}) {
    try {
      const response = await apiClient.get(url, config);
      return {
        success: true,
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async postSafe(url, data = {}, config = {}) {
    try {
      const response = await apiClient.post(url, data, config);
      return {
        success: true,
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async patchSafe(url, data = {}, config = {}) {
    try {
      const response = await apiClient.patch(url, data, config);
      return {
        success: true,
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async deleteSafe(url, config = {}) {
    try {
      const response = await apiClient.delete(url, config);
      return {
        success: true,
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async uploadFile(url, file, additionalData = {}, onProgress = null) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
      });

      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      };

      if (onProgress) {
        config.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        };
      }

      const response = await apiClient.post(url, formData, config);
      return {
        success: true,
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async downloadFile(url, filename = null) {
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      return {
        success: true,
        message: 'File downloaded successfully',
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async downloadInvoicePDF(url, invoiceNumber = null) {
    try {
      const response = await apiClient.get(url, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = invoiceNumber ? `${invoiceNumber}.pdf` : 'invoice.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      return {
        success: true,
        message: 'Invoice PDF downloaded successfully',
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getMyInvoices(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `/invoices/my-invoices/?${queryString}` : '/invoices/my-invoices/';
    return this.getSafe(url);
  }

  async getInvoiceDetail(invoiceId) {
    return this.getSafe(`/invoices/${invoiceId}/`);
  }

  async downloadInvoice(invoiceId) {
    try {
      const response = await apiClient.get(`/invoices/${invoiceId}/download_pdf/`, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `invoice-${invoiceId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      return {
        success: true,
        message: 'Invoice downloaded successfully',
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getNDISInvoices(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `/invoices/ndis_invoices/?${queryString}` : '/invoices/ndis_invoices/';
    return this.getSafe(url);
  }

  async checkNDISCompliance(invoiceId) {
    return this.getSafe(`/invoices/ndis/${invoiceId}/compliance_check/`);
  }

  async getQuoteTemplate(id) {
    return this.getSafe(`/quotes/templates/${id}/`);
  }

  async createQuoteTemplate(data) {
    return this.postSafe('/quotes/templates/', data);
  }

  async updateQuoteTemplate(id, data) {
    return this.patchSafe(`/quotes/templates/${id}/`, data);
  }

  async deleteQuoteTemplate(id) {
    return this.deleteSafe(`/quotes/templates/${id}/`);
  }

  handleError(error) {
    const errorResponse = {
      success: false,
      status: error.response?.status || 500,
      message: 'An error occurred',
      errors: {},
      isNetworkError: false,
      isServerError: false,
      isValidationError: false,
      isAuthError: false,
    };

    if (!error.response && error.request) {
      errorResponse.isNetworkError = true;
      errorResponse.message = 'Network error. Please check your internet connection.';
      return errorResponse;
    }

    if (error.response?.status >= 500) {
      errorResponse.isServerError = true;
      errorResponse.message = 'Server error. Please try again later.';
      return errorResponse;
    }

    if (error.response?.status === 401) {
      errorResponse.isAuthError = true;
      errorResponse.message = 'Authentication required. Please log in.';
      return errorResponse;
    }

    if (error.response?.status === 400) {
      errorResponse.isValidationError = true;
    }

    if (error.response?.data) {
      const data = error.response.data;
      
      if (typeof data === 'string') {
        errorResponse.message = data;
      } else if (data.error) {
        errorResponse.message = data.error;
      } else if (data.message) {
        errorResponse.message = data.message;
      } else if (data.detail) {
        errorResponse.message = data.detail;
      } else if (data.non_field_errors) {
        errorResponse.message = Array.isArray(data.non_field_errors) 
          ? data.non_field_errors[0] 
          : data.non_field_errors;
      }

      if (data.errors || (typeof data === 'object' && !data.error && !data.message && !data.detail)) {
        errorResponse.errors = data.errors || data;
      }
    } else if (error.message) {
      errorResponse.message = error.message;
    }

    return errorResponse;
  }

  setAuthToken(token) {
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Token ${token}`;
      localStorage.setItem('authToken', token);
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
      localStorage.removeItem('authToken');
    }
  }

  removeAuthToken() {
    this.setAuthToken(null);
    localStorage.removeItem('user');
    localStorage.removeItem('userProfile');
  }

  getAuthToken() {
    return localStorage.getItem('authToken');
  }

  isAuthenticated() {
    return !!this.getAuthToken();
  }

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  setCurrentUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  }

  isNetworkError(error) {
    return !error.response && error.request;
  }

  isServerError(error) {
    return error.response?.status >= 500;
  }

  isClientError(error) {
    return error.response?.status >= 400 && error.response?.status < 500;
  }

  isValidationError(error) {
    return error.response?.status === 400;
  }

  isAuthError(error) {
    return error.response?.status === 401;
  }

  isForbiddenError(error) {
    return error.response?.status === 403;
  }

  isNotFoundError(error) {
    return error.response?.status === 404;
  }

  getErrorMessage(error) {
    if (this.isNetworkError(error)) {
      return 'Network error. Please check your internet connection.';
    }
    
    if (this.isAuthError(error)) {
      return 'Please log in to continue.';
    }

    if (this.isForbiddenError(error)) {
      return 'You do not have permission to perform this action.';
    }

    if (this.isNotFoundError(error)) {
      return 'The requested resource was not found.';
    }
    
    if (this.isServerError(error)) {
      return 'Server error. Please try again later.';
    }

    return error.response?.data?.message || 
           error.response?.data?.error || 
           error.response?.data?.detail ||
           'An error occurred. Please try again.';
  }

  getFieldErrors(error) {
    if (error.response?.data && typeof error.response.data === 'object') {
      const data = error.response.data;
      const fieldErrors = {};
      
      Object.keys(data).forEach(key => {
        if (Array.isArray(data[key])) {
          fieldErrors[key] = data[key][0];
        } else if (typeof data[key] === 'string') {
          fieldErrors[key] = data[key];
        }
      });
      
      return fieldErrors;
    }
    return {};
  }

  formatCurrency(amount, currency = 'AUD') {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  }

  formatDate(dateString, options = {}) {
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    };
    
    return new Date(dateString).toLocaleDateString('en-AU', {
      ...defaultOptions,
      ...options
    });
  }

  formatDateTime(dateString, options = {}) {
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return new Date(dateString).toLocaleDateString('en-AU', {
      ...defaultOptions,
      ...options
    });
  }

  isDateOverdue(dateString) {
    return new Date(dateString) < new Date();
  }

  calculateDaysDifference(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  buildQueryString(params) {
    const filteredParams = Object.entries(params)
      .filter(([key, value]) => value !== null && value !== undefined && value !== '')
      .reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {});
    
    return new URLSearchParams(filteredParams).toString();
  }

  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  validatePhone(phone) {
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
  }

  sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    return input.trim().replace(/[<>]/g, '');
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

export default new ApiService();
