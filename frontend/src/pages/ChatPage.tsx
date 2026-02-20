import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Send, ArrowLeft, Bot, User, CheckCircle2 } from 'lucide-react';
import { chatAPI, ticketsAPI } from '@/lib/api';
import { MessageRole } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

export default function ChatPage() {
  const { ticketId } = useParams<{ ticketId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: ticket } = useQuery({
    queryKey: ['ticket', ticketId],
    queryFn: () => ticketsAPI.get(ticketId!),
    enabled: !!ticketId,
  });

  const { data: chatData, isLoading } = useQuery({
    queryKey: ['chat', ticketId],
    queryFn: () => chatAPI.getMessages(ticketId!),
    enabled: !!ticketId,
    refetchInterval: 3000, // Refetch cada 3 segundos para ver respuestas del agente
  });

  const sendMutation = useMutation({
    mutationFn: (content: string) =>
      chatAPI.sendMessage(ticketId!, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat', ticketId] });
      queryClient.invalidateQueries({ queryKey: ['ticket', ticketId] });
      setMessage('');
    },
  });

  const closeMutation = useMutation({
    mutationFn: () => ticketsAPI.close(ticketId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ticket', ticketId] });
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
    },
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    sendMutation.mutate(message);
  };

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatData?.messages]);

  const isTicketOpen = ticket?.status === 'open' || ticket?.status === 'in_progress';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="p-2"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-neutral-text-primary">
              {ticket?.title}
            </h1>
            <p className="text-sm text-neutral-text-secondary">
              {ticket?.message_count} mensajes
            </p>
          </div>
        </div>
        {isTicketOpen && (
          <Button
            variant="secondary"
            onClick={() => closeMutation.mutate()}
            isLoading={closeMutation.isPending}
          >
            <CheckCircle2 className="w-5 h-5" />
            Cerrar consulta
          </Button>
        )}
      </div>

      {/* Chat Container */}
      <Card className="h-[calc(100vh-280px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aesa-blue border-t-transparent"></div>
            </div>
          ) : (
            <>
              {chatData?.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${
                    msg.role === MessageRole.USER ? 'flex-row-reverse' : ''
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                      msg.role === MessageRole.USER
                        ? 'bg-aesa-blue'
                        : msg.role === MessageRole.SYSTEM
                        ? 'bg-yellow-500'
                        : 'gradient-aesa'
                    }`}
                  >
                    {msg.role === MessageRole.USER ? (
                      <User className="w-5 h-5 text-white" />
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>

                  {/* Message */}
                  <div
                    className={`flex-1 max-w-2xl ${
                      msg.role === MessageRole.USER ? 'items-end' : 'items-start'
                    } flex flex-col`}
                  >
                    <div
                      className={`px-4 py-3 rounded-aesa ${
                        msg.role === MessageRole.USER
                          ? 'bg-aesa-blue text-white'
                          : msg.role === MessageRole.SYSTEM
                          ? 'bg-yellow-50 border border-yellow-200 text-yellow-900'
                          : 'bg-white shadow-aesa-sm'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                    <span className="text-xs text-neutral-text-secondary mt-1 px-2">
                      {formatDistanceToNow(new Date(msg.created_at), {
                        addSuffix: true,
                        locale: es,
                      })}
                    </span>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        {isTicketOpen ? (
          <form onSubmit={handleSend} className="border-t border-neutral-text-secondary/10 p-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Escribe tu consulta..."
                className="input-aesa flex-1"
                disabled={sendMutation.isPending}
              />
              <Button
                type="submit"
                disabled={!message.trim() || sendMutation.isPending}
                isLoading={sendMutation.isPending}
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </form>
        ) : (
          <div className="border-t border-neutral-text-secondary/10 p-4 text-center text-neutral-text-secondary">
            Esta consulta está cerrada
          </div>
        )}
      </Card>
    </div>
  );
}
