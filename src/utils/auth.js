export const TOKEN_KEY = 'authToken';
export const USER_KEY = 'user';
export const REFRESH_TOKEN_KEY = 'refreshToken';

export const setToken = (token) => {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
};

export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

export const setUser = (user) => {
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(USER_KEY);
  }
};

export const getUser = () => {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
};

export const removeUser = () => {
  localStorage.removeItem(USER_KEY);
};

export const clearAuthData = () => {
  removeToken();
  removeUser();
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

export const isAuthenticated = () => {
  const token = getToken();
  const user = getUser();
  return !!(token && user);
};

export const isTokenExpired = (token) => {
  if (!token) return true;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
  } catch (error) {
    return true;
  }
};

export const getUserRole = () => {
  const user = getUser();
  return user?.user_type || 'client';
};

export const getClientType = () => {
  const user = getUser();
  return user?.client_type || 'general';
};

export const isClient = () => {
  return getUserRole() === 'client';
};

export const isNDISClient = () => {
  const user = getUser();
  return user?.is_ndis_client || user?.client_type === 'ndis';
};

export const isVerified = () => {
  const user = getUser();
  return user?.is_verified || false;
};

export const isGoogleUser = () => {
  const user = getUser();
  return user?.auth_provider === 'google';
};

export const hasPermission = (permission) => {
  const user = getUser();
  if (!user) return false;
  
  const permissions = {
    'can_modify_profile': isAuthenticated(),
    'can_access_ndis': isNDISClient(),
    'can_create_quotes': isAuthenticated(),
    'can_view_quotes': isAuthenticated(),
  };
  
  return permissions[permission] || false;
};

export const formatUserName = (user = null) => {
  const currentUser = user || getUser();
  if (!currentUser) return '';
  
  const { first_name, last_name, email } = currentUser;
  
  if (first_name && last_name) {
    return `${first_name} ${last_name}`;
  }
  
  if (first_name) {
    return first_name;
  }
  
  return email || '';
};

export const getUserInitials = (user = null) => {
  const currentUser = user || getUser();
  if (!currentUser) return '';
  
  const { first_name, last_name, email } = currentUser;
  
  if (first_name && last_name) {
    return `${first_name.charAt(0)}${last_name.charAt(0)}`.toUpperCase();
  }
  
  if (first_name) {
    return first_name.charAt(0).toUpperCase();
  }
  
  if (email) {
    return email.charAt(0).toUpperCase();
  }
  
  return '';
};

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password) => {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  
  return {
    isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers,
    errors: {
      minLength: password.length < minLength,
      hasUpperCase: !hasUpperCase,
      hasLowerCase: !hasLowerCase,
      hasNumbers: !hasNumbers,
      hasSpecialChar: !hasSpecialChar,
    }
  };
};

export const validatePhoneNumber = (phone) => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  return phoneRegex.test(phone.replace(/\s/g, ''));
};

export const getAuthHeaders = () => {
  const token = getToken();
  return token ? { Authorization: `Token ${token}` } : {};
};

export const redirectToLogin = () => {
  clearAuthData();
  window.location.href = '/accounts/login';
};

export const redirectAfterLogin = (userType = null) => {
  // All users are clients, so always redirect to client portal
  return '/clients/portal';
};
  
export const shouldRedirectToVerification = () => {
  return isAuthenticated() && !isVerified() && !isGoogleUser();
};

export const canAccessRoute = (requireVerification = true) => {
  if (!isAuthenticated()) return false;
  
  if (requireVerification && !isVerified() && !isGoogleUser()) {
    return false;
  }
  
  return true;
};
