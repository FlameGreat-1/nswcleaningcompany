import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ 
  children, 
  requiredUserType = null,
  requiredClientType = null,
  requireVerification = true,
  fallbackPath = '/accounts/login'
}) => {
  const { 
    isAuthenticated, 
    user, 
    isLoading, 
    isVerified,
    checkAuthStatus 
  } = useAuth();
  const { isDark } = useTheme();
  const location = useLocation();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      checkAuthStatus();
    }
  }, [isLoading, isAuthenticated, checkAuthStatus]);

  if (isLoading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${
        isDark ? 'bg-[#180c2e]' : 'bg-gray-50'
      }`}>
        <div className="relative group">
          <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-30 animate-pulse"></div>
          <div className="relative app-bg-card app-border border-2 rounded-3xl p-8 app-shadow-xl">
            <LoadingSpinner size="lg" variant="branded" />
            <p className={`mt-4 text-sm font-medium ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
              Verifying authentication...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate 
        to={fallbackPath} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  if (requireVerification && !isVerified) {
    return (
      <Navigate 
        to="/accounts/email-verification" 
        state={{ 
          from: location,
          email: user?.email,
          message: 'Please verify your email address to access this page.'
        }} 
        replace 
      />
    );
  }

  if (requiredUserType && user?.user_type !== requiredUserType) {
    const unauthorizedPath = getUnauthorizedRedirectPath(user?.user_type);
    return (
      <Navigate 
        to={unauthorizedPath} 
        state={{ 
          from: location,
          error: 'You do not have permission to access this page.'
        }} 
        replace 
      />
    );
  }

  if (requiredClientType && user?.client_type !== requiredClientType) {
    const unauthorizedPath = getUnauthorizedRedirectPath(user?.user_type);
    return (
      <Navigate 
        to={unauthorizedPath} 
        state={{ 
          from: location,
          error: 'You do not have permission to access this page.'
        }} 
        replace 
      />
    );
  }

  return children;
};

const getUnauthorizedRedirectPath = (userType) => {
    switch (userType) {
      case 'admin':
        return '/admin/portal';       
      case 'staff':
        return '/staff/portal';       
      case 'client':
      default:
        return '/clients/portal';   
    }
  };

export const AdminRoute = ({ children, ...props }) => (
  <ProtectedRoute 
    requiredUserType="admin" 
    fallbackPath="/accounts/login?type=admin"
    {...props}
  >
    {children}
  </ProtectedRoute>
);

export const StaffRoute = ({ children, ...props }) => (
  <ProtectedRoute 
    requiredUserType="staff" 
    fallbackPath="/accounts/login?type=staff"
    {...props}
  >
    {children}
  </ProtectedRoute>
);

export const ClientRoute = ({ children, ...props }) => (
  <ProtectedRoute 
    requiredUserType="client" 
    fallbackPath="/accounts/login"
    {...props}
  >
    {children}
  </ProtectedRoute>
);

export const NDISRoute = ({ children, ...props }) => (
  <ProtectedRoute 
    requiredUserType="client"
    requiredClientType="ndis"
    fallbackPath="/accounts/login?client_type=ndis"
    {...props}
  >
    {children}
  </ProtectedRoute>
);

export const PublicRoute = ({ children, redirectIfAuthenticated = false, redirectTo = '/clients/portal' }) => {

  const { isAuthenticated, user, isLoading } = useAuth();
  const { isDark } = useTheme();

  if (isLoading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${
        isDark ? 'bg-[#180c2e]' : 'bg-gray-50'
      }`}>
        <div className="relative group">
          <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#180c2e] rounded-3xl blur opacity-30 animate-pulse"></div>
          <div className="relative app-bg-card app-border border-2 rounded-3xl p-8 app-shadow-xl">
            <LoadingSpinner size="lg" variant="branded" />
          </div>
        </div>
      </div>
    );
  }

  if (redirectIfAuthenticated && isAuthenticated && user) {
    const userRedirectPath = getUnauthorizedRedirectPath(user.user_type);
    return <Navigate to={userRedirectPath} replace />;
  }

  return children;
};

export default ProtectedRoute;
