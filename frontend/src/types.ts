// Types para la API

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export enum TicketStatus {
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  ESCALATED = 'escalated',
  CLOSED = 'closed',
}

export enum TicketPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum TicketCategory {
  TECHNICAL = 'technical',
  LICENSING = 'licensing',
  GENERAL = 'general',
  DOCUMENTATION = 'documentation',
}

export interface Ticket {
  id: string;
  user_id: string;
  title: string;
  status: TicketStatus;
  priority: TicketPriority;
  category: TicketCategory;
  escalated_at: string | null;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface CreateTicketRequest {
  title: string;
  category?: TicketCategory;
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
}

export interface Message {
  id: string;
  ticket_id: string;
  role: MessageRole;
  content: string;
  meta_data: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface SendMessageRequest {
  content: string;
}

export interface ChatHistoryResponse {
  ticket_id: string;
  messages: Message[];
  total_messages: number;
}

export interface TicketListResponse {
  tickets: Ticket[];
  total: number;
  page: number;
  page_size: number;
}
