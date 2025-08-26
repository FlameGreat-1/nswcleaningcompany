import axios from 'axios';

const API_BASE_URL = '/api';
const API_VERSION = 'v1';

export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: `${API_BASE_URL}/${API_VERSION}/accounts/auth/register/`,
    LOGIN: `${API_BASE_URL}/${API_VERSION}/accounts/auth/login/`,
    LOGOUT: `${API_BASE_URL}/${API_VERSION}/accounts/auth/logout/`,
    GOOGLE_AUTH: `${API_BASE_URL}/${API_VERSION}/accounts/auth/google/`,
    GOOGLE_REGISTER: `${API_BASE_URL}/${API_VERSION}/accounts/auth/google/register/`,
    SOCIAL_LOGIN: `${API_BASE_URL}/${API_VERSION}/accounts/auth/social/login/`,
    PASSWORD_CHANGE: `${API_BASE_URL}/${API_VERSION}/accounts/auth/password/change/`,
    PASSWORD_RESET: `${API_BASE_URL}/${API_VERSION}/accounts/auth/password/reset/`,
    PASSWORD_RESET_CONFIRM: `${API_BASE_URL}/${API_VERSION}/accounts/auth/password/reset/confirm/`,
    EMAIL_VERIFY: `${API_BASE_URL}/${API_VERSION}/accounts/auth/email/verify/`,
    EMAIL_RESEND: `${API_BASE_URL}/${API_VERSION}/accounts/auth/email/resend/`,
  },
  PROFILE: {
    USER: `${API_BASE_URL}/${API_VERSION}/accounts/profile/`,
    CLIENT: `${API_BASE_URL}/${API_VERSION}/accounts/profile/client/`,
    DEACTIVATE: `${API_BASE_URL}/${API_VERSION}/accounts/profile/deactivate/`,
    SOCIAL: `${API_BASE_URL}/${API_VERSION}/accounts/profile/social/`,
    LINK: `${API_BASE_URL}/${API_VERSION}/accounts/profile/social/link/`,
    UNLINK: `${API_BASE_URL}/${API_VERSION}/accounts/profile/social/unlink/`,
  },
  ADDRESSES: `${API_BASE_URL}/${API_VERSION}/accounts/addresses/`,
  DASHBOARD: `${API_BASE_URL}/${API_VERSION}/accounts/dashboard/`,
  HEALTH: `${API_BASE_URL}/${API_VERSION}/accounts/health/`,
  
  QUOTES: {
    BASE: `${API_BASE_URL}/${API_VERSION}/quotes/`,
    MY_QUOTES: `${API_BASE_URL}/${API_VERSION}/quotes/my-quotes/`,
    CALCULATOR: `${API_BASE_URL}/${API_VERSION}/quotes/calculator/`,
    ITEMS: `${API_BASE_URL}/${API_VERSION}/quotes/items/`,
    ATTACHMENTS: `${API_BASE_URL}/${API_VERSION}/quotes/attachments/`,
    TEMPLATES: `${API_BASE_URL}/${API_VERSION}/quotes/templates/`,
    REVISIONS: `${API_BASE_URL}/${API_VERSION}/quotes/revisions/`,
  },

  SERVICES: {
    BASE: `${API_BASE_URL}/${API_VERSION}/services/`,
    ADDONS: `${API_BASE_URL}/${API_VERSION}/services/addons/`,
    LIST: `${API_BASE_URL}/${API_VERSION}/services/services/`,
  },

  INVOICES: {
    BASE: `${API_BASE_URL}/${API_VERSION}/invoices/`,
    MY_INVOICES: `${API_BASE_URL}/${API_VERSION}/invoices/my-invoices/`, 
    NDIS: `${API_BASE_URL}/${API_VERSION}/invoices/ndis/`,
    ITEMS: `${API_BASE_URL}/${API_VERSION}/invoices/items/`,
    DASHBOARD_STATS: `${API_BASE_URL}/${API_VERSION}/invoices/dashboard-stats/`,
  },
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token && token.trim()) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/accounts/login';
    }
    return Promise.reject(error);
  }
);

const initializeAuth = () => {
  const token = localStorage.getItem('authToken');
  if (token && token.trim()) {
    apiClient.defaults.headers.common['Authorization'] = `Token ${token}`;
  }
};

initializeAuth();

if (typeof window !== 'undefined') {
  window.apiClient = apiClient;
  window.initializeAuth = initializeAuth;
}

export { initializeAuth };
export default apiClient;
