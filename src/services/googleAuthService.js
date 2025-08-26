import authService from './authService';

class GoogleAuthService {
  constructor() {
    this.isInitialized = false;
    this.clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    this.googleAuthCallback = null;
  }

  async initializeGoogleAuth(callbackFn = null) {
    if (this.isInitialized || !this.clientId) {
      return this.isInitialized;
    }
  
    try {
      await this.loadGoogleScript();
      
      this.googleAuthCallback = callbackFn;
      
      await window.google.accounts.id.initialize({
        client_id: this.clientId,
        callback: (response) => {
          if (this.googleAuthCallback) {
            this.googleAuthCallback(response);
          } else {
            this.handleCredentialResponse(response);
          }
        },
        auto_select: false,
        cancel_on_tap_outside: true,
      });
      this.isInitialized = true;
      return true;
    } catch (error) {
      return false;
    }
  }
  
  loadGoogleScript() {
    return new Promise((resolve, reject) => {
      if (window.google) {
        resolve();
        return;
      }
  
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async handleCredentialResponse(response) {
    try {
      if (!response || !response.credential) {
        return {
          success: false,
          error: 'No credential received from Google',
        };
      }
      
      const credential = response.credential;
      
      try {
        const payload = this.parseJWT(credential);
        
        return {
          success: true,
          user: payload,
          credential: credential,
        };
      } catch (parseError) {
        return {
          success: false,
          error: 'Failed to parse Google credential: ' + parseError.message,
        };
      }
    } catch (error) {
      return {
        success: false,
        error: 'Failed to process Google credential: ' + error.message,
      };
    }
  }

  parseJWT(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const payload = JSON.parse(jsonPayload);
      return payload;
    } catch (error) {
      throw new Error('Invalid JWT token: ' + error.message);
    }
  }

  async signInWithGoogle(userType = 'client', clientType = 'general') {
    return new Promise(async (resolve) => {
      const handleGoogleResponse = async (response) => {
        try {
          const credentialResponse = await this.handleCredentialResponse(response);
          
          if (!credentialResponse.success) {
            resolve(credentialResponse);
            return;
          }
  
          try {
            const authResponse = await authService.googleAuth(
              response.credential,
              userType,
              clientType
            );
            resolve(authResponse);
          } catch (authError) {
            resolve({
              success: false,
              error: 'Error calling backend: ' + (authError.message || 'Unknown error'),
            });
          }
        } catch (error) {
          resolve({
            success: false,
            error: 'Google authentication failed: ' + (error.message || 'Unknown error'),
          });
        }
      };
      
      if (!this.isInitialized) {
        await this.initializeGoogleAuth(handleGoogleResponse);
      } else {
        this.googleAuthCallback = handleGoogleResponse;
      }

      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          resolve({
            success: false,
            error: 'Google Sign-In was cancelled or not displayed',
          });
        }
      });
    });
  }
  
  async registerWithGoogle(userType = 'client', clientType = 'general', phoneNumber = '') {
    return new Promise(async (resolve) => {
      const handleGoogleResponse = async (response) => {
        try {
          const credentialResponse = await this.handleCredentialResponse(response);
          
          if (!credentialResponse.success) {
            resolve(credentialResponse);
            return;
          }

          try {
            const authResponse = await authService.googleRegister(
              response.credential,
              userType,
              clientType,
              phoneNumber
            );
            resolve(authResponse);
          } catch (authError) {
            resolve({
              success: false,
              error: 'Error calling backend for registration: ' + (authError.message || 'Unknown error'),
            });
          }
        } catch (error) {
          resolve({
            success: false,
            error: 'Google registration failed: ' + (error.message || 'Unknown error'),
          });
        }
      };
      
      if (!this.isInitialized) {
        await this.initializeGoogleAuth(handleGoogleResponse);
      } else {
        this.googleAuthCallback = handleGoogleResponse;
      }

      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          resolve({
            success: false,
            error: 'Google Sign-In was cancelled or not displayed',
          });
        }
      });
    });
  }

  renderGoogleButton(elementId, options = {}) {
    if (!this.isInitialized) {
      return false;
    }

    const defaultOptions = {
      theme: 'outline',
      size: 'large',
      text: 'signin_with',
      shape: 'rectangular',
      logo_alignment: 'left',
    };

    window.google.accounts.id.renderButton(
      document.getElementById(elementId),
      { ...defaultOptions, ...options }
    );

    return true;
  }

  async linkGoogleAccount() {
    return new Promise(async (resolve) => {
      const handleGoogleResponse = async (response) => {
        try {
          try {
            const linkResponse = await authService.linkSocialAccount('google', response.credential);
            resolve(linkResponse);
          } catch (authError) {
            resolve({
              success: false,
              error: 'Error linking account: ' + (authError.message || 'Unknown error'),
            });
          }
        } catch (error) {
          resolve({
            success: false,
            error: 'Failed to link Google account: ' + (error.message || 'Unknown error'),
          });
        }
      };
      
      if (!this.isInitialized) {
        await this.initializeGoogleAuth(handleGoogleResponse);
      } else {
        this.googleAuthCallback = handleGoogleResponse;
      }

      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          resolve({
            success: false,
            error: 'Google Sign-In was cancelled or not displayed',
          });
        }
      });
    });
  }

  async unlinkGoogleAccount() {
    return await authService.unlinkSocialAccount('google');
  }

  signOut() {
    if (window.google && window.google.accounts) {
      window.google.accounts.id.disableAutoSelect();
    }
  }

  isConfigured() {
    return !!this.clientId;
  }

  getClientId() {
    return this.clientId;
  }
}

export default new GoogleAuthService();
