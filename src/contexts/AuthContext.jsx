import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import authService from '../services/authService';
import googleAuthService from '../services/googleAuthService';
import { 
  getUser, 
  getToken, 
  setUser, 
  setToken, 
  clearAuthData, 
  isAuthenticated,
  isVerified,
  getUserRole 
} from '../utils/auth';

const AuthContext = createContext();

const initialState = {
  user: getUser(),
  token: getToken(),
  isAuthenticated: isAuthenticated(),
  isLoading: false,
  error: null,
  isInitialized: true,
};

const authReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
        error: null,
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };

    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };

    case 'INITIALIZE':
      return {
        ...state,
        isInitialized: true,
        isLoading: false,
      };

    case 'RESET_STATE':
      return initialState;

    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const setLoading = useCallback((loading) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, []);

  const setError = useCallback((error) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  const login = useCallback((user, token) => {
    setUser(user);
    setToken(token);
    authService.setAuthData(token, { user });
    dispatch({ 
      type: 'LOGIN_SUCCESS', 
      payload: { user, token } 
    });
  }, []);

  const logout = useCallback(async (skipApiCall = false) => {
    if (!skipApiCall) {
      setLoading(true);
    }
    
    try {
      if (window.quotesRefreshInterval) {
        clearInterval(window.quotesRefreshInterval);
        window.quotesRefreshInterval = null;
      }
      if (window.invoicesRefreshInterval) {
        clearInterval(window.invoicesRefreshInterval);
        window.invoicesRefreshInterval = null;
      }
      
      clearAuthData();
      authService.clearAuthData();
      googleAuthService.signOut();
      dispatch({ type: 'LOGOUT' });
      
      if (!skipApiCall) {
        authService.logout().catch(error => {
          console.error('Background logout error:', error);
        });
      }

      window.location.href = '/';
      
    } catch (error) {
      console.error('Logout error:', error);
      clearAuthData();
      dispatch({ type: 'LOGOUT' });
      window.location.href = '/';
    }
  }, []);
  
  const updateUser = useCallback((userData) => {
    const updatedUser = { ...state.user, ...userData };
    setUser(updatedUser);
    dispatch({ type: 'UPDATE_USER', payload: updatedUser });
  }, [state.user]);

  const register = useCallback(async (userData) => {
    setLoading(true);
    clearError();

    try {
      const response = await authService.register(userData);
      
      if (response.success) {
        if (response.data.token && response.data.user) {
          login(response.data.user, response.data.token);
        }
        return response;
      } else {
        setError(response.message || 'Registration failed');
        return response;
      }
    } catch (error) {
      const errorMessage = 'Registration failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [login, setLoading, clearError, setError]);

  const loginWithCredentials = useCallback(async (credentials) => {
    setLoading(true);
    clearError();

    try {
      const response = await authService.login(credentials);
      
      if (response.success) {
        login(response.data.user, response.data.token);
        return response;
      } else {
        setError(response.message || 'Login failed');
        return response;
      }
    } catch (error) {
      const errorMessage = 'Login failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [login, setLoading, clearError, setError]);

  const loginWithGoogle = useCallback(async (userType = 'client', clientType = 'general') => {
    setLoading(true);
    clearError();
  
    try {
      const response = await googleAuthService.signInWithGoogle(userType, clientType);
      
      if (response.success) {
        const userData = response.data?.user || response.user;
        const token = response.data?.token || response.token;
        
        if (userData && token) {
          login(userData, token);
          return {
            success: true,
            data: { user: userData, token: token }
          };
        }
      }
      
      setError(response.error || 'Google login failed');
      return response;
    } catch (error) {
      const errorMessage = 'Google login failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [login, setLoading, clearError, setError]);
  
  const registerWithGoogle = useCallback(async (userType = 'client', clientType = 'general', phoneNumber = '') => {
    setLoading(true);
    clearError();
  
    try {
      const response = await googleAuthService.registerWithGoogle(userType, clientType, phoneNumber);
      
      if (response.success) {
        const userData = response.data?.user || response.user;
        const token = response.data?.token || response.token;
        
        if (userData && token) {
          login(userData, token);
          return {
            success: true,
            data: { user: userData, token: token }
          };
        }
      }
      
      setError(response.error || 'Google registration failed');
      return response;
    } catch (error) {
      const errorMessage = 'Google registration failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [login, setLoading, clearError, setError]);
  
  const changePassword = useCallback(async (currentPassword, newPassword) => {
    setLoading(true);
    clearError();

    try {
      const response = await authService.changePassword(currentPassword, newPassword);
      
      if (response.success) {
        return response;
      } else {
        setError(response.message || 'Password change failed');
        return response;
      }
    } catch (error) {
      const errorMessage = 'Password change failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, setError]);

  const requestPasswordReset = useCallback(async (email) => {
    setLoading(true);
    clearError();

    try {
      const response = await authService.requestPasswordReset(email);
      
      if (!response.success) {
        setError(response.message || 'Password reset request failed');
      }
      
      return response;
    } catch (error) {
      const errorMessage = 'Password reset request failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, setError]);

  const confirmPasswordReset = useCallback(async (token, newPassword) => {
    setLoading(true);
    clearError();

    try {
      const response = await authService.confirmPasswordReset(token, newPassword);
      
      if (!response.success) {
        setError(response.message || 'Password reset failed');
      }
      
      return response;
    } catch (error) {
      const errorMessage = 'Password reset failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, setError]);

  const verifyEmail = useCallback(async (token) => {
    setLoading(true);
    clearError();
  
    try {
      const response = await authService.verifyEmail(token);
      
      if (response && (response.success || response.data || response.message)) {
        if (state.user) {
          const updatedUser = { ...state.user, is_verified: true };
          updateUser(updatedUser);
        }
        
        const result = {
          success: true,
          data: response.data || response,
          message: response.message || response.data?.message || 'Email verified successfully'
        };
        
        return result;
      } else {
        const errorMsg = response?.message || response?.error || 'Email verification failed';
        setError(errorMsg);
        return { success: false, error: errorMsg };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Email verification failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [updateUser, setLoading, clearError, setError, state.user]);

  const resendVerification = useCallback(async (email) => {
    setLoading(true);
    clearError();

    try {
      const response = await authService.resendVerification(email);
      
      if (!response.success) {
        setError(response.message || 'Failed to resend verification email');
      }
      
      return response;
    } catch (error) {
      const errorMessage = 'Failed to resend verification email. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [setLoading, clearError, setError]);

  const checkAuthStatus = useCallback(async () => {
    const token = getToken();
    const user = getUser();
    
    if (token && user) {
      authService.setAuthData(token, { user });
      dispatch({ 
        type: 'LOGIN_SUCCESS', 
        payload: { user, token } 
      });
    }
    
    dispatch({ type: 'INITIALIZE' });
  }, []);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  useEffect(() => {
    const initializeGoogleAuth = async () => {
      if (googleAuthService.isConfigured()) {
        await googleAuthService.initializeGoogleAuth();
      }
    };
    
    initializeGoogleAuth();
  }, []);

  const value = {
    user: state.user,
    token: state.token,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,
    isInitialized: state.isInitialized,
    isVerified: state.user ? isVerified() : false,
    userRole: state.user ? getUserRole() : null,
    login,
    logout,
    register,
    loginWithCredentials,
    loginWithGoogle,
    registerWithGoogle,
    updateUser,
    changePassword,
    requestPasswordReset,
    confirmPasswordReset,
    verifyEmail,
    resendVerification,
    setLoading,
    setError,
    clearError,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export { AuthContext };
export default AuthProvider;

