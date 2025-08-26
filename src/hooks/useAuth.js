import { useState, useEffect, useContext, useCallback } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import authService from '../services/authService';
import googleAuthService from '../services/googleAuthService';
import { 
  isAuthenticated, 
  getUser, 
  getUserRole, 
  isVerified, 
  isGoogleUser,
  clearAuthData,
  redirectAfterLogin,
  shouldRedirectToVerification 
} from '../utils/auth';

export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export const useAuthState = () => {
  const [user, setUser] = useState(getUser());
  const [isLoggedIn, setIsLoggedIn] = useState(isAuthenticated());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateAuthState = useCallback(() => {
    const currentUser = getUser();
    const authenticated = isAuthenticated();
    
    setUser(currentUser);
    setIsLoggedIn(authenticated);
  }, []);

  useEffect(() => {
    updateAuthState();
    
    const handleStorageChange = (e) => {
      if (e.key === 'authToken' || e.key === 'user') {
        updateAuthState();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [updateAuthState]);

  return {
    user,
    isLoggedIn,
    loading,
    error,
    updateAuthState,
    setLoading,
    setError,
  };
};

export const useLogin = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login } = useAuth();

  const loginUser = useCallback(async (credentials) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authService.login(credentials);
      
      if (response.token && response.user) {
        login(response.user, response.token);
        
        const redirectPath = redirectAfterLogin(response.user.user_type);
        
        const result = {
          success: true,
          user: response.user,
          redirectTo: redirectPath,
        };
        return result;
      } else {
        setError(response.message || 'Login failed');
        return { success: false, error: response.message };
      }
    } catch (err) {
      const errorMessage = 'Login failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [login]);

  return { loginUser, loading, error, setError };
};

export const useRegister = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login } = useAuth();

  const registerUser = useCallback(async (userData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authService.register(userData);
      
      if (response.success) {
        if (response.data.token && response.data.user) {
          login(response.data.user, response.data.token);
        }
        
        return {
          success: true,
          user: response.data.user,
          requiresVerification: response.data.requires_verification,
          message: response.data.message,
        };
      } else {
        setError(response.message || 'Registration failed');
        return { success: false, error: response.message, errors: response.errors };
      }
    } catch (err) {
      const errorMessage = 'Registration failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [login]);

  return { registerUser, loading, error, setError };
};

export const useGoogleAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login } = useAuth();

  const googleLogin = useCallback(async (userType = 'client', clientType = 'general') => {
    setLoading(true);
    setError(null);

    try {
      const response = await googleAuthService.signInWithGoogle(userType, clientType);
      
      if (response.success) {
        const userData = response.data?.user || response.user;
        const token = response.data?.token || response.token;
        
        if (userData && token) {
          login(userData, token);
          return {
            success: true,
            user: userData,
            redirectTo: redirectAfterLogin(userData.user_type),
          };
        }
      }
      
      setError(response.error || 'Google login failed');
      return { success: false, error: response.error };
    } catch (err) {
      const errorMessage = 'Google login failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [login]);

  const googleRegister = useCallback(async (userType = 'client', clientType = 'general', phoneNumber = '') => {
    setLoading(true);
    setError(null);

    try {
      const response = await googleAuthService.registerWithGoogle(userType, clientType, phoneNumber);
      
      if (response.success) {
        const userData = response.data?.user || response.user;
        const token = response.data?.token || response.token;
        
        if (userData && token) {
          login(userData, token);
          return {
            success: true,
            user: userData,
            redirectTo: redirectAfterLogin(userData.user_type),
          };
        }
      }
      
      setError(response.error || 'Google registration failed');
      return { success: false, error: response.error };
    } catch (err) {
      const errorMessage = 'Google registration failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [login]);

  return { googleLogin, googleRegister, loading, error, setError };
};

export const usePasswordReset = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const requestReset = useCallback(async (email) => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await authService.requestPasswordReset(email);
      
      if (response.success) {
        setSuccess(true);
        return { success: true, message: response.data.message };
      } else {
        setError(response.message || 'Password reset request failed');
        return { success: false, error: response.message };
      }
    } catch (err) {
      const errorMessage = 'Password reset request failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const confirmReset = useCallback(async (token, newPassword) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authService.confirmPasswordReset(token, newPassword);
      
      if (response.success) {
        return { success: true, message: response.data.message };
      } else {
        setError(response.message || 'Password reset failed');
        return { success: false, error: response.message };
      }
    } catch (err) {
      const errorMessage = 'Password reset failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  return { requestReset, confirmReset, loading, error, success, setError };
};

export const useEmailVerification = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { verifyEmail: contextVerifyEmail, resendVerification: contextResendVerification } = useAuth();

  const verifyEmail = useCallback(async (token) => {
    setLoading(true);
    setError(null);

    try {
      const response = await contextVerifyEmail(token);
      return response;
    } catch (err) {
      setError('Email verification failed. Please try again.');
      return { success: false, error: 'Email verification failed. Please try again.' };
    } finally {
      setLoading(false);
    }
  }, [contextVerifyEmail]);

  const resendVerification = useCallback(async (email) => {
    setLoading(true);
    setError(null);

    try {
      const response = await contextResendVerification(email);
      return response;
    } catch (err) {
      setError('Failed to resend verification email. Please try again.');
      return { success: false, error: 'Failed to resend verification email. Please try again.' };
    } finally {
      setLoading(false);
    }
  }, [contextResendVerification]);

  return { verifyEmail, resendVerification, loading, error, setError };
};

export const useAuthRedirect = () => {
  const { user, isLoggedIn } = useAuth();

  useEffect(() => {
    if (shouldRedirectToVerification()) {
      window.location.href = '/accounts/email-verification';
    }
  }, [user, isLoggedIn]);

  const getRedirectPath = useCallback(() => {
    if (!isLoggedIn) return '/accounts/login';
    if (shouldRedirectToVerification()) return '/accounts/email-verification';
    return redirectAfterLogin(user?.user_type);
  }, [isLoggedIn, user]);

  return { getRedirectPath };
};

