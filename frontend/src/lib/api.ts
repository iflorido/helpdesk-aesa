import axios from 'axios';
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  Ticket,
  CreateTicketRequest,
  TicketListResponse,
  Message,
  SendMessageRequest,
  ChatHistoryResponse,
} from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir el token a todas las peticiones
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await api.post('/api/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// Tickets
export const ticketsAPI = {
  list: async (params?: {
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<TicketListResponse> => {
    const response = await api.get('/api/tickets/', { params });
    return response.data;
  },

  create: async (data: CreateTicketRequest): Promise<Ticket> => {
    const response = await api.post('/api/tickets/', data);
    return response.data;
  },

  get: async (id: string): Promise<Ticket> => {
    const response = await api.get(`/api/tickets/${id}`);
    return response.data;
  },

  close: async (id: string): Promise<Ticket> => {
    const response = await api.post(`/api/tickets/${id}/close`);
    return response.data;
  },
};

// Chat
export const chatAPI = {
  getMessages: async (ticketId: string): Promise<ChatHistoryResponse> => {
    const response = await api.get(`/api/chat/${ticketId}/messages`);
    return response.data;
  },

  sendMessage: async (
    ticketId: string,
    data: SendMessageRequest
  ): Promise<Message> => {
    const response = await api.post(`/api/chat/${ticketId}/messages`, data);
    return response.data;
  },
};

// Operator
export const operatorAPI = {
  listTickets: async (params?: {
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<TicketListResponse> => {
    const response = await api.get('/api/operator/tickets', { params });
    return response.data;
  },

  getTicket: async (id: string): Promise<Ticket> => {
    const response = await api.get(`/api/operator/tickets/${id}`);
    return response.data;
  },

  takeTicket: async (id: string): Promise<Ticket> => {
    const response = await api.post(`/api/operator/tickets/${id}/take`);
    return response.data;
  },

  respond: async (
    ticketId: string,
    data: SendMessageRequest
  ): Promise<Message> => {
    const response = await api.post(
      `/api/operator/tickets/${ticketId}/respond`,
      data
    );
    return response.data;
  },

  getStats: async (): Promise<{
    escalated: number;
    in_progress: number;
    open: number;
    total: number;
  }> => {
    const response = await api.get('/api/operator/stats');
    return response.data;
  },
};

export default api;