import { useState } from 'react';
import { useRegister } from '../../../hooks/useAuth';
import { useTheme } from '../../../contexts/ThemeContext';
import { validateEmail, validatePassword, validatePhoneNumber } from '../../../utils/auth';
import LoadingSpinner from '../../common/LoadingSpinner';
import GoogleAuthButton from './GoogleAuthButton';

const RegisterForm = ({ 
  onSuccess, 
  onError,
  userType = 'client',
  clientType = 'general',
  className = '' 
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    password: '',
    confirm_password: ''
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [focusedFields, setFocusedFields] = useState({});
  const [showLoginLink, setShowLoginLink] = useState(false);

  const { registerUser, loading, error, setError } = useRegister();
  const { isDark } = useTheme();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    if (error) {
      setError(null);
    }
  };

  const handleFocus = (fieldName) => {
    setFocusedFields(prev => ({ ...prev, [fieldName]: true }));
  };

  const handleBlur = (fieldName) => {
    if (!formData[fieldName]) {
      setFocusedFields(prev => ({ ...prev, [fieldName]: false }));
    }
  };

  const validateStep1 = () => {
    const newErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else {
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.isValid) {
        const errorMessages = [];
        if (passwordValidation.errors.minLength) errorMessages.push('at least 8 characters');
        if (passwordValidation.errors.hasUpperCase) errorMessages.push('one uppercase letter');
        if (passwordValidation.errors.hasLowerCase) errorMessages.push('one lowercase letter');
        if (passwordValidation.errors.hasNumbers) errorMessages.push('one number');
        newErrors.password = `Password must contain ${errorMessages.join(', ')}`;
      }
    }

    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your password';
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    } else if (formData.first_name.trim().length < 2) {
      newErrors.first_name = 'First name must be at least 2 characters';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    } else if (formData.last_name.trim().length < 2) {
      newErrors.last_name = 'Last name must be at least 2 characters';
    }

    if (formData.phone_number && !validatePhoneNumber(formData.phone_number)) {
      newErrors.phone_number = 'Please enter a valid phone number';
    }

    if (!acceptTerms) {
      newErrors.terms = 'You must accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleStep1Continue = (e) => {
    e.preventDefault();
    if (validateStep1()) {
      setCurrentStep(2);
    }
  };

  const handleStep2Submit = async (e) => {
    e.preventDefault();
    
    if (!validateStep2()) return;
  
    const response = await registerUser({
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      email: formData.email.trim(),
      phone_number: formData.phone_number.trim(),
      password: formData.password,
      password_confirm: formData.confirm_password,
      user_type: userType,
      client_type: clientType
    });
  
    if (response.success) {
      onSuccess?.(response);
    } else {
      if (response.errors) {
        const fieldErrors = {};
        
        Object.keys(response.errors).forEach(field => {
          if (Array.isArray(response.errors[field])) {
            fieldErrors[field] = response.errors[field][0];
          } else {
            fieldErrors[field] = response.errors[field];
          }
        });
        
        setErrors(fieldErrors);
      }
      
      onError?.(response.error || 'Registration failed');
    }
  };

  const handleGoogleSuccess = (response) => {
    onSuccess?.(response);
  };

  const handleGoogleError = (error) => {
    if (typeof error === 'object' && error.accountExists) {
      setError('This email is already registered. Please sign in instead.');
    } else {
      onError?.(error || 'Google registration failed. Please try again.');
    }
  };

  const getInputClasses = (fieldName, hasError = false) => {
    const baseClasses = `
      w-full px-4 pt-6 pb-2 rounded-xl border-2 transition-all duration-300
      font-medium text-base backdrop-blur-xl
      focus:outline-none focus:ring-4 focus:scale-[1.02] transform-gpu
      ${isDark 
        ? 'bg-white/5 border-white/20 text-white focus:border-[#006da6] focus:ring-[#006da6]/20 focus:bg-white/10' 
        : 'bg-white/90 border-gray-200 text-[#180c2e] focus:border-[#006da6] focus:ring-[#006da6]/20 focus:bg-white'
      }
    `;
    
    const errorClasses = hasError ? `
      border-red-500 focus:border-red-500 focus:ring-red-500/20
      ${isDark ? 'bg-red-500/5' : 'bg-red-50'}
    ` : '';

    return `${baseClasses} ${errorClasses}`.trim();
  };

  const getLabelClasses = (fieldName, hasError = false) => {
    const isActive = focusedFields[fieldName] || formData[fieldName];
    const baseClasses = `
      absolute left-4 transition-all duration-300 pointer-events-none font-semibold
      ${isActive 
        ? 'top-2 text-xs' 
        : 'top-1/2 transform -translate-y-1/2 text-base'
      }
      ${hasError 
        ? 'text-red-500' 
        : isActive 
          ? 'text-[#006da6]'
          : (isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]')
      }
    `;
    
    return baseClasses.trim();
  };

  const renderStep1 = () => (
    <form onSubmit={handleStep1Continue} className="space-y-6">
      <div className="space-y-5">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleInputChange}
              onFocus={() => handleFocus('email')}
              onBlur={() => handleBlur('email')}
              className={getInputClasses('email', errors.email)}
              disabled={loading}
            />
            <label 
              htmlFor="email" 
              className={getLabelClasses('email', errors.email)}
            >
              Email Address
            </label>
          </div>
          {errors.email && (
            <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.email}</p>
          )}
        </div>

        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              value={formData.password}
              onChange={handleInputChange}
              onFocus={() => handleFocus('password')}
              onBlur={() => handleBlur('password')}
              className={`${getInputClasses('password', errors.password)} pr-12`}
              disabled={loading}
            />
            <label 
              htmlFor="password" 
              className={getLabelClasses('password', errors.password)}
            >
              Password
            </label>
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-lg transition-all duration-300 z-10 hover:scale-110 ${
                isDark 
                  ? 'text-[#CCCCCC] hover:text-[#006da6] hover:bg-white/10' 
                  : 'text-[#6B7280] hover:text-[#006da6] hover:bg-[#006da6]/10'
              }`}
              disabled={loading}
            >
              {showPassword ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>
          {errors.password && (
            <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.password}</p>
          )}
        </div>

        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="confirm_password"
              name="confirm_password"
              type={showConfirmPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              value={formData.confirm_password}
              onChange={handleInputChange}
              onFocus={() => handleFocus('confirm_password')}
              onBlur={() => handleBlur('confirm_password')}
              className={`${getInputClasses('confirm_password', errors.confirm_password)} pr-12`}
              disabled={loading}
            />
            <label 
              htmlFor="confirm_password" 
              className={getLabelClasses('confirm_password', errors.confirm_password)}
            >
              Confirm Password
            </label>
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-lg transition-all duration-300 z-10 hover:scale-110 ${
                isDark 
                  ? 'text-[#CCCCCC] hover:text-[#006da6] hover:bg-white/10' 
                  : 'text-[#6B7280] hover:text-[#006da6] hover:bg-[#006da6]/10'
              }`}
              disabled={loading}
            >
              {showConfirmPassword ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>
          {errors.confirm_password && (
            <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.confirm_password}</p>
          )}
        </div>
      </div>

      {(error || errors.non_field_errors) && (
        <div className={`relative group p-4 rounded-xl border-2 animate-fade-in-up ${
          isDark 
            ? 'bg-red-500/10 border-red-500/30 backdrop-blur-xl' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 to-red-600/20 rounded-xl blur opacity-50"></div>
          <p className="relative text-sm text-red-500 font-semibold">
            {error || errors.non_field_errors}
          </p>
        </div>
      )}

      <div className="space-y-4">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-xl blur opacity-0 group-hover:opacity-30 transition-all duration-300"></div>
          <button
            type="submit"
            disabled={loading}
            className="relative w-full bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:via-[#2d1b4e] hover:to-[#180c2e] text-white font-black py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-[#006da6]/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:translate-y-0 backdrop-blur-xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative z-10">
              {loading ? (
                <div className="flex items-center justify-center gap-3">
                  <LoadingSpinner size="sm" color="white" />
                  <span>Processing...</span>
                </div>
              ) : (
                'Continue'
              )}
            </div>
          </button>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className={`w-full border-t-2 ${isDark ? 'border-white/20' : 'border-gray-200'}`} />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className={`px-6 font-semibold backdrop-blur-xl rounded-full ${
              isDark 
                ? 'bg-[#180c2e]/80 text-[#CCCCCC] border border-white/10' 
                : 'bg-white/90 text-[#6B7280] border border-gray-200'
            }`}>
              Or sign up with
            </span>
          </div>
        </div>

        <GoogleAuthButton
          mode="register"
          userType={userType}
          clientType={clientType}
          phoneNumber={formData.phone_number}
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          disabled={loading}
          size="lg"
        />
      </div>
    </form>
  );

  const renderStep2 = () => (
    <form onSubmit={handleStep2Submit} className="space-y-6">
      <div className="mb-6">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 to-[#005a8a]/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <button
            type="button"
            onClick={() => setCurrentStep(1)}
            className={`relative flex items-center gap-2 text-base font-black transition-all duration-300 cursor-pointer hover:scale-105 p-3 rounded-lg backdrop-blur-xl ${
              isDark 
                ? 'text-white hover:text-[#006da6] hover:bg-white/10 border border-white/20' 
                : 'text-[#180c2e] hover:text-[#006da6] hover:bg-[#006da6]/10 border border-gray-200'
            }`}
          >
            <svg className="w-5 h-5 transition-transform duration-300 group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to previous step
          </button>
        </div>
      </div>

      <div className="space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
            <div className="relative">
              <input
                id="first_name"
                name="first_name"
                type="text"
                autoComplete="given-name"
                required
                value={formData.first_name}
                onChange={handleInputChange}
                onFocus={() => handleFocus('first_name')}
                onBlur={() => handleBlur('first_name')}
                className={getInputClasses('first_name', errors.first_name)}
                disabled={loading}
              />
              <label 
                htmlFor="first_name" 
                className={getLabelClasses('first_name', errors.first_name)}
              >
                First Name
              </label>
            </div>
            {errors.first_name && (
              <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.first_name}</p>
            )}
          </div>

          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
            <div className="relative">
              <input
                id="last_name"
                name="last_name"
                type="text"
                autoComplete="family-name"
                required
                value={formData.last_name}
                onChange={handleInputChange}
                onFocus={() => handleFocus('last_name')}
                onBlur={() => handleBlur('last_name')}
                className={getInputClasses('last_name', errors.last_name)}
                disabled={loading}
              />
              <label 
                htmlFor="last_name" 
                className={getLabelClasses('last_name', errors.last_name)}
              >
                Last Name
              </label>
            </div>
            {errors.last_name && (
              <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.last_name}</p>
            )}
          </div>
        </div>

        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="phone_number"
              name="phone_number"
              type="tel"
              autoComplete="tel"
              value={formData.phone_number}
              onChange={handleInputChange}
              onFocus={() => handleFocus('phone_number')}
              onBlur={() => handleBlur('phone_number')}
              className={getInputClasses('phone_number', errors.phone_number)}
              disabled={loading}
            />
            <label 
              htmlFor="phone_number" 
              className={getLabelClasses('phone_number', errors.phone_number)}
            >
              Phone Number (Optional)
            </label>
          </div>
          {errors.phone_number && (
            <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.phone_number}</p>
          )}
        </div>

        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/10 to-[#005a8a]/10 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className={`relative flex items-start gap-4 p-4 rounded-xl backdrop-blur-xl border-2 transition-all duration-300 ${
            isDark 
              ? 'bg-white/5 border-white/20 hover:bg-white/10 hover:border-[#006da6]/30' 
              : 'bg-white/90 border-gray-200 hover:bg-white hover:border-[#006da6]/30'
          }`}>
            <div className="relative flex-shrink-0 mt-1">
              <input
                id="accept_terms"
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className={`w-5 h-5 rounded border-2 cursor-pointer transition-all duration-300 focus:ring-4 focus:ring-[#006da6]/20 ${
                  acceptTerms
                    ? 'bg-gradient-to-r from-[#006da6] to-[#005a8a] border-[#006da6] text-white'
                    : isDark 
                      ? 'bg-white/10 border-white/30 hover:border-[#006da6]' 
                      : 'bg-white border-gray-300 hover:border-[#006da6]'
                }`}
                disabled={loading}
              />
              {acceptTerms && (
                <svg className="absolute top-0.5 left-0.5 w-4 h-4 text-white pointer-events-none" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <label 
              htmlFor="accept_terms" 
              className={`text-sm font-semibold cursor-pointer leading-relaxed select-none transition-colors duration-300 ${
                isDark ? 'text-white hover:text-[#006da6]' : 'text-[#180c2e] hover:text-[#006da6]'
              }`}
            >
              I agree to the{' '}
              <a 
                href="/terms" 
                target="_blank" 
                rel="noopener noreferrer"
                className="font-black text-[#006da6] hover:text-[#0080c7] hover:underline transition-all duration-300"
              >
                Terms of Service
              </a>
              {' '}and{' '}
              <a 
                href="/privacy" 
                target="_blank" 
                rel="noopener noreferrer"
                className="font-black text-[#006da6] hover:text-[#0080c7] hover:underline transition-all duration-300"
              >
                Privacy Policy
              </a>
            </label>
          </div>
          {errors.terms && (
            <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.terms}</p>
          )}
        </div>
      </div>

      {(error || errors.non_field_errors) && (
        <div className={`relative group p-4 rounded-xl border-2 animate-fade-in-up ${
          isDark 
            ? 'bg-red-500/10 border-red-500/30 backdrop-blur-xl' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 to-red-600/20 rounded-xl blur opacity-50"></div>
          <p className="relative text-sm text-red-500 font-semibold">
            {error || errors.non_field_errors}
          </p>
        </div>
      )}

      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-xl blur opacity-0 group-hover:opacity-30 transition-all duration-300"></div>
        <button
          type="submit"
          disabled={loading || !acceptTerms}
          className="relative w-full bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:via-[#2d1b4e] hover:to-[#180c2e] text-white font-black py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-[#006da6]/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:translate-y-0 backdrop-blur-xl overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div className="relative z-10">
            {loading ? (
              <div className="flex items-center justify-center gap-3">
                <LoadingSpinner size="sm" color="white" />
                <span>Creating Account...</span>
              </div>
            ) : (
              'Create Account'
            )}
          </div>
        </button>
      </div>
    </form>
  );

  return (
    <div className={className}>
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className={`relative w-10 h-10 rounded-full flex items-center justify-center text-sm font-black transition-all duration-300 ${
              currentStep >= 1 
                ? 'bg-gradient-to-r from-[#006da6] to-[#005a8a] text-white shadow-lg' 
                : isDark ? 'bg-white/10 text-[#CCCCCC] border border-white/20' : 'bg-gray-100 text-[#6B7280] border border-gray-200'
            }`}>
              {currentStep > 1 ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                '1'
              )}
              {currentStep >= 1 && (
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full blur opacity-30"></div>
              )}
            </div>
            <span className={`text-sm font-black transition-colors duration-300 ${
              currentStep >= 1 
                ? isDark ? 'text-white' : 'text-[#180c2e]'
                : isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'
            }`}>
              Account Details
            </span>
          </div>
          
          <div className={`flex-1 h-1 mx-6 rounded-full transition-all duration-500 ${
            currentStep >= 2 
              ? 'bg-gradient-to-r from-[#006da6] to-[#005a8a]' 
              : isDark ? 'bg-white/20' : 'bg-gray-200'
          }`} />
          
          <div className="flex items-center space-x-3">
            <div className={`relative w-10 h-10 rounded-full flex items-center justify-center text-sm font-black transition-all duration-300 ${
              currentStep >= 2 
                ? 'bg-gradient-to-r from-[#006da6] to-[#005a8a] text-white shadow-lg' 
                : isDark ? 'bg-white/10 text-[#CCCCCC] border border-white/20' : 'bg-gray-100 text-[#6B7280] border border-gray-200'
            }`}>
              2
              {currentStep >= 2 && (
                <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] to-[#005a8a] rounded-full blur opacity-30"></div>
              )}
            </div>
            <span className={`text-sm font-black transition-colors duration-300 ${
              currentStep >= 2 
                ? isDark ? 'text-white' : 'text-[#180c2e]'
                : isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'
            }`}>
              Personal Info
            </span>
          </div>
        </div>
      </div>

      <div className="animate-fade-in-up">
        {currentStep === 1 ? renderStep1() : renderStep2()}
      </div>
    </div>
  );
};

export default RegisterForm;


