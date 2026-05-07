// API service for SmartPlate backend
// VITE_API_URL is set at build time: https://your-backend.onrender.com/api
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.updateTokens();
  }

  updateTokens() {
    this.token = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    console.log(' Token update:', {
      token: this.token ? 'present' : 'missing',
      refreshToken: this.refreshToken ? 'present' : 'missing',
      allLocalStorage: { ...localStorage }
    });
  }

  // Helper method for API calls
  async apiCall(endpoint, options = {}) {
    // Refresh tokens from localStorage before each call
    this.updateTokens();
    
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add authorization header if token exists
    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    // Debug the complete request
    if (endpoint === '/dashboard/change-password' || endpoint === '/cars') {
      console.log('=== API Call Debug ===');
      console.log('Endpoint:', endpoint);
      console.log('Complete request config:', config);
      console.log('Request body type:', typeof config.body);
      console.log('Request body:', config.body);
      console.log('Token exists:', !!this.token);
      console.log('Auth header:', config.headers.Authorization);
      console.log('===================');
      
      // If it's FormData, log its contents
      if (config.body instanceof FormData) {
        console.log(' FormData entries:');
        for (let [key, value] of config.body.entries()) {
          console.log(`  ${key}: ${value}`);
        }
      }
      
      // Log the final request that will be sent
      console.log(' Final request:', {
        method: config.method,
        headers: config.headers,
        body: config.body instanceof FormData ? 'FormData object' : config.body
      });
    }

    try {
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
      
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      // Try to parse JSON, but handle non-JSON responses
      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        const text = await response.text();
        data = { detail: text };
      }

      if (!response.ok) {
        // Handle different error formats
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (Array.isArray(data.detail)) {
            // Handle validation errors array
            errorMessage = data.detail.map(err => 
              typeof err === 'string' ? err : err.msg || err.loc ? `${err.loc.join('.')}: ${err.msg}` : JSON.stringify(err)
            ).join(', ');
          } else if (typeof data.detail === 'object') {
            errorMessage = JSON.stringify(data.detail);
          }
        } else if (data.message) {
          errorMessage = data.message;
        } else if (data.error) {
          errorMessage = data.error;
        }
        
        // Add status code to error for debugging
        errorMessage = `${errorMessage} (Status: ${response.status})`;
        
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      console.error('API call error:', error);
      // Re-throw with the error message
      throw error;
    }
  }

  // Authentication methods
  async signup(userData) {
    const payload = {
      email: userData.email,
      password: userData.password,
      confirm_password: userData.confirm || userData.password,
      full_name: userData.fullname || userData.full_name,
      phone: userData.phone || '+213555123456', // Default phone if not provided
      role: userData.role || 'user',
    };

    return this.apiCall('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async verifyEmail(email, otp) {
    return this.apiCall('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ email, code: otp }),
    });
  }

  async login(email, password) {
    return this.apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async verifyLoginOtp(email, otp, preAuthToken) {
    return this.apiCall('/auth/verify-login-otp', {
      method: 'POST',
      body: JSON.stringify({ code: otp, pre_auth_token: preAuthToken }),
    });
  }

  async resendOtp(email, purpose = 'signup') {
    // Backend expects lowercase: "signup" | "login"
    return this.apiCall('/auth/resend-otp', {
      method: 'POST',
      body: JSON.stringify({ email, purpose: purpose.toLowerCase() }),
    });
  }

  async sendPasswordOtp() {
    return this.apiCall('/dashboard/send-password-otp', {
      method: 'POST',
    });
  }

  async refreshToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.apiCall('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: this.refreshToken }),
    });

    // Update tokens
    this.setTokens(response.access_token, response.refresh_token);
    return response;
  }

  async getCurrentUser() {
    return this.apiCall('/auth/me');
  }

  async getUserProfile() {
    return this.apiCall('/dashboard/profile');
  }

  async updateProfilePicture(pictureUrl) {
    return this.apiCall(`/dashboard/profile?profile_picture=${encodeURIComponent(pictureUrl)}`, {
      method: 'PUT',
    });
  }

  async changePassword(currentPassword, newPassword, otpCode) {
    // Create query parameters since backend expects function parameters as query params
    const params = new URLSearchParams();
    params.append('current_password', currentPassword);
    params.append('new_password', newPassword);
    params.append('otp_code', otpCode);
    
    const url = `/dashboard/change-password?${params.toString()}`;
    
    const response = await this.apiCall(url, {
      method: 'POST',
      // No body needed for query parameters
    });
    
    return response;
  }

  async verifyOtpForPasswordReset(email, code) {
    return this.apiCall('/auth/verify-reset-otp', {
      method: 'POST',
      body: JSON.stringify({ email, code }),
    });
  }

  async resetPasswordWithToken(token, newPassword) {
    return this.apiCall('/auth/reset-password-with-token', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    });
  }

  async resetPassword(email, code, newPassword) {
    return this.apiCall('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ email, code, new_password: newPassword }),
    });
  }

  // Token management
  setTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    this.updateTokens();
  }

  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.updateTokens();
  }

  isAuthenticated() {
    return !!this.token;
  }

  // File upload methods
  async uploadFile(file, serviceType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('service_type', serviceType);

    return this.apiCall('/upload', {
      method: 'POST',
      headers: {
        // Remove Content-Type to let browser set it with boundary
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });
  }

  async getUserFiles() {
    return this.apiCall('/user/files');
  }

  // SOS methods
  async submitSosRequest(formData) {
    const requestBody = {
      full_name: formData.name,
      license_plate: formData.plate,
      emergency_description: formData.desc,
      current_location: formData.location || null,
      gps_coordinates: formData.location || null
    };
    
    const response = await this.apiCall('/sos/submit', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
    
    return response;
  }

  // Depannage methods
  async submitDepannageRequest(formData) {
    // Map breakdown types to French values expected by backend
    const breakdownTypeMap = {
      'battery': 'Batterie',
      'tire': 'Pneu crevé', 
      'engine': 'Moteur',
      'other': 'Autre'
    };

    const requestBody = {
      full_name: formData.name,
      phone: formData.phone,
      license_plate: formData.plate,
      breakdown_type: breakdownTypeMap[formData.problem] || formData.problem,
      location_address: formData.location || null,
      gps_coordinates: formData.location || null,
      additional_notes: formData.notes || null
    };
    
    const response = await this.apiCall('/depannage/submit', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
    
    return response;
  }

  // Document upload methods
  async uploadVignette(carId, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await this.apiCall(`/services/documents/vignette?car_id=${carId}`, {
      method: 'POST',
      headers: {
        // Remove Content-Type to let browser set it with boundary
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });
    
    return response;
  }

  async uploadControleTechnique(carId, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await this.apiCall(`/services/documents/controle-technique?car_id=${carId}`, {
      method: 'POST',
      headers: {
        // Remove Content-Type to let browser set it with boundary
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });
    
    return response;
  }

  async uploadAssurance(carId, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await this.apiCall(`/services/documents/assurance?car_id=${carId}`, {
      method: 'POST',
      headers: {
        // Remove Content-Type to let browser set it with boundary
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });
    
    return response;
  }

  async uploadPlatePhoto(carId, file) {
    const formData = new FormData();
    formData.append('file', file);

    return this.apiCall(`/dashboard/plates/${carId}/documents/plate-photo`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.token}` },
      body: formData,
    });
  }

  async uploadCartGrise(carId, file) {
    const formData = new FormData();
    formData.append('file', file);

    return this.apiCall(`/services/documents/cart-grise?car_id=${carId}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.token}` },
      body: formData,
    });
  }

  async getCarDocuments(carId) {
    return this.apiCall(`/cars/${carId}/documents`);
  }

  // Car management methods
  async getUserCars() {
    return this.apiCall('/cars/');
  }

  async createCar(carData) {
    return this.apiCall('/cars/', {
      method: 'POST',
      body: JSON.stringify(carData),
    });
  }

  async getCar(carId) {
    return this.apiCall(`/cars/${carId}/`);
  }

  /** Public — no auth needed. Returns vehicle info only (no personal data). */
  async getPublicVehicle(qrCode) {
    const res = await fetch(`${this.baseURL}/cars/public/${qrCode}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Véhicule introuvable");
    }
    return res.json();
  }

  /** Authenticated — returns full CarResponse including personal data. */
  async getCarByQrCode(qrCode) {
    return this.apiCall(`/cars/qr/${qrCode}`);
  }

  // Order management methods
  async createOrder(orderData) {
    console.log('Creating order with data:', orderData);
    console.log('Authentication token:', this.token);
    console.log('API base URL:', this.baseURL);
    
    return this.apiCall('/orders/', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  }

  async processOrder(orderId) {
    return this.apiCall(`/orders/${orderId}/process`, {
      method: 'POST',
    });
  }

  async getUserOrders() {
    return this.apiCall('/orders/my');
  }

  async getOrder(orderId) {
    return this.apiCall(`/orders/${orderId}/`);
  }

  async updateOrder(orderId, updateData) {
    return this.apiCall(`/orders/${orderId}/`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async cancelOrder(orderId) {
    return this.apiCall(`/orders/${orderId}/cancel`, {
      method: 'POST',
    });
  }

  async markOrderPaid(orderId) {
    return this.apiCall(`/orders/${orderId}/mark-paid`, {
      method: 'POST',
    });
  }

  async getOrderStats() {
    return this.apiCall('/orders/stats');
  }
}

export const apiService = new ApiService();