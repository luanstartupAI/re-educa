/**
 * Sistema de API para integração com backend
 * Configuração completa com interceptors e tratamento de erros
 */

import axios from 'axios';
import { toast } from 'sonner';

// Configuração base da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Instância base do axios
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('re-educa-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para refresh token automático
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('re-educa-refresh-token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { token, refresh_token } = response.data;
          localStorage.setItem('re-educa-token', token);
          localStorage.setItem('re-educa-refresh-token', refresh_token);

          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh token expirado, logout
        localStorage.removeItem('re-educa-token');
        localStorage.removeItem('re-educa-refresh-token');
        localStorage.removeItem('re-educa-user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Função para tratamento de erros
const handleApiError = (error) => {
  let message = 'Erro interno do servidor';

  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        message = data.error || 'Dados inválidos';
        if (data.details) {
          message += ': ' + data.details.map(d => d.message).join(', ');
        }
        break;
      case 401:
        message = 'Sessão expirada. Faça login novamente.';
        break;
      case 403:
        message = 'Acesso negado';
        break;
      case 404:
        message = 'Recurso não encontrado';
        break;
      case 429:
        message = 'Muitas requisições. Tente novamente em alguns instantes.';
        break;
      case 500:
        message = 'Erro interno do servidor';
        break;
      default:
        message = data.error || 'Erro desconhecido';
    }
  } else if (error.request) {
    message = 'Erro de conexão. Verifique sua internet.';
  }

  toast.error(message);
  return Promise.reject(error);
};

// Aplicar interceptor de erro
api.interceptors.response.use(
  (response) => response,
  handleApiError
);

// Serviços da API
export const apiService = {
  // Autenticação
  auth: {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    logout: () => api.post('/auth/logout'),
    refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
    forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
    resetPassword: (data) => api.post('/auth/reset-password', data),
  },

  // Usuários
  users: {
    getProfile: () => api.get('/users/profile'),
    updateProfile: (data) => api.put('/users/profile', data),
    changePassword: (data) => api.post('/users/change-password', data),
    getSubscription: () => api.get('/users/subscription'),
    getActivity: (params) => api.get('/users/activity', { params }),
  },

  // Ferramentas de Saúde
  health: {
    // IMC
    calculateIMC: (data) => api.post('/health/imc/calculate', data),
    getIMCHistory: (params) => api.get('/health/imc/history', { params }),
    
    // Calorias
    calculateCalories: (data) => api.post('/health/calories/calculate', data),
    
    // Nutrição
    searchFoods: (query) => api.get('/health/nutrition/search', { params: { query } }),
    getFoodDetails: (fdcId) => api.get(`/health/nutrition/food/${fdcId}`),
    
    // Diário Alimentar
    addFoodEntry: (data) => api.post('/health/food-diary/entries', data),
    getFoodEntries: (params) => api.get('/health/food-diary/entries', { params }),
    
    // Exercícios
    addExerciseEntry: (data) => api.post('/health/exercise/entries', data),
    getExerciseEntries: (params) => api.get('/health/exercise/entries', { params }),
    
    // Analytics
    getAnalytics: (params) => api.get('/health/analytics/summary', { params }),
    
    // Metas
    getGoals: () => api.get('/health/goals'),
    createGoal: (data) => api.post('/health/goals', data),
  },

  // Produtos
  products: {
    getAll: (params) => api.get('/products', { params }),
    getById: (id) => api.get(`/products/${id}`),
    getCategories: () => api.get('/products/categories'),
    getFeatured: () => api.get('/products/featured'),
    getRecommendations: () => api.get('/products/recommendations'),
    getReviews: (productId, params) => api.get(`/products/${productId}/reviews`, { params }),
    createReview: (productId, data) => api.post(`/products/${productId}/reviews`, data),
  },

  // Pedidos
  orders: {
    getAll: (params) => api.get('/orders', { params }),
    getById: (id) => api.get(`/orders/${id}`),
    create: (data) => api.post('/orders', data),
    cancel: (id) => api.post(`/orders/${id}/cancel`),
  },

  // Pagamentos
  payments: {
    createPaymentIntent: (data) => api.post('/payments/create-payment-intent', data),
    createSubscription: (data) => api.post('/payments/subscription/create', data),
    cancelSubscription: () => api.post('/payments/subscription/cancel'),
  },

  // Admin (apenas para admins)
  admin: {
    getAllUsers: (params) => api.get('/admin/users', { params }),
    getAnalytics: (params) => api.get('/admin/analytics', { params }),
    getAllOrders: (params) => api.get('/admin/orders', { params }),
  },
};

// Hooks para React
export const useApi = () => {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const request = React.useCallback(async (apiCall, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiCall();
      
      if (options.onSuccess) {
        options.onSuccess(response.data);
      }
      
      return response.data;
    } catch (err) {
      setError(err);
      
      if (options.onError) {
        options.onError(err);
      }
      
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    request,
  };
};

// Hook para autenticação
export const useAuth = () => {
  const [user, setUser] = React.useState(null);
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const token = localStorage.getItem('re-educa-token');
    const userData = localStorage.getItem('re-educa-user');

    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Erro ao parsear dados do usuário:', error);
        localStorage.removeItem('re-educa-token');
        localStorage.removeItem('re-educa-user');
      }
    }
    
    setLoading(false);
  }, []);

  const login = React.useCallback(async (credentials) => {
    try {
      const response = await apiService.auth.login(credentials);
      const { user, token, refresh_token } = response.data;

      localStorage.setItem('re-educa-token', token);
      localStorage.setItem('re-educa-refresh-token', refresh_token);
      localStorage.setItem('re-educa-user', JSON.stringify(user));

      setUser(user);
      setIsAuthenticated(true);

      toast.success('Login realizado com sucesso!');
      return response.data;
    } catch (error) {
      toast.error('Erro ao fazer login. Verifique suas credenciais.');
      throw error;
    }
  }, []);

  const register = React.useCallback(async (userData) => {
    try {
      const response = await apiService.auth.register(userData);
      const { user, token, refresh_token } = response.data;

      localStorage.setItem('re-educa-token', token);
      localStorage.setItem('re-educa-refresh-token', refresh_token);
      localStorage.setItem('re-educa-user', JSON.stringify(user));

      setUser(user);
      setIsAuthenticated(true);

      toast.success('Conta criada com sucesso!');
      return response.data;
    } catch (error) {
      toast.error('Erro ao criar conta. Tente novamente.');
      throw error;
    }
  }, []);

  const logout = React.useCallback(() => {
    localStorage.removeItem('re-educa-token');
    localStorage.removeItem('re-educa-refresh-token');
    localStorage.removeItem('re-educa-user');

    setUser(null);
    setIsAuthenticated(false);

    toast.success('Logout realizado com sucesso!');
  }, []);

  const updateUser = React.useCallback((userData) => {
    setUser(userData);
    localStorage.setItem('re-educa-user', JSON.stringify(userData));
  }, []);

  return {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    updateUser,
  };
};

export default api;