import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Send, ArrowLeft, Bot, User, UserCheck } from 'lucide-react';
import { operatorAPI, chatAPI } from '@/lib/api';
import { MessageRole, TicketStatus } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

export default function OperatorTicketPage() {
  const { ticketId } = useParams<{ ticketId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: ticket } = useQuery({
    queryKey: ['operator-ticket', ticketId],
    queryFn: () => operatorAPI.getTicket(ticketId!),
    enabled: !!ticketId,
  });

  const { data: chatData } = useQuery({
    queryKey: ['operator-chat', ticketId],
    queryFn: () => chatAPI.getMessages(ticketId!),
    enabled: !!ticketId,
    refetchInterval: 3000,
  });

  const takeMutation = useMutation({
    mutationFn: () => operatorAPI.takeTicket(ticketId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator-ticket', ticketId] });
      queryClient.invalidateQueries({ queryKey: ['operator-chat', ticketId] });
      queryClient.invalidateQueries({ queryKey: ['operator-stats'] });
    },
  });

  const respondMutation = useMutation({
    mutationFn: (content: string) =>
      operatorAPI.respond(ticketId!, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operator-chat', ticketId] });
      setMessage('');
    },
  });

  const handleRespond = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    respondMutation.mutate(message);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatData?.messages]);

  const needsToTake = ticket?.status === TicketStatus.ESCALATED;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/operator')}
            className="p-2"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-neutral-text-primary">
              {ticket?.title}
            </h1>
            <p className="text-sm text-neutral-text-secondary">
              Ticket #{ticketId?.slice(0, 8)} • {ticket?.message_count} mensajes
            </p>
          </div>
        </div>
        {needsToTake && (
          <Button
            onClick={() => takeMutation.mutate()}
            isLoading={takeMutation.isPending}
          >
            <UserCheck className="w-5 h-5" />
            Tomar ticket
          </Button>
        )}
      </div>

      {/* Warning si necesita tomar */}
      {needsToTake && (
        <Card glass={false} className="bg-orange-50 border border-orange-200">
          <div className="flex items-start gap-3">
            <UserCheck className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-orange-900 mb-1">
                Ticket escalado
              </h3>
              <p className="text-sm text-orange-700">
                Este ticket fue escalado por el agente. Tómalo para responder
                al usuario como operador humano.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Chat Container */}
      <Card className="h-[calc(100vh-320px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {chatData?.messages.map((msg) => {
            const isHuman = msg.meta_data?.human_response === true;
            
            return (
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
                      : isHuman
                      ? 'bg-green-500'
                      : 'gradient-aesa'
                  }`}
                >
                  {msg.role === MessageRole.USER ? (
                    <User className="w-5 h-5 text-white" />
                  ) : isHuman ? (
                    <UserCheck className="w-5 h-5 text-white" />
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
                        : isHuman
                        ? 'bg-green-50 border border-green-200 text-green-900'
                        : 'bg-white shadow-aesa-sm'
                    }`}
                  >
                    {isHuman && (
                      <p className="text-xs font-medium mb-1 text-green-700">
                        👤 Respuesta de operador humano
                      </p>
                    )}
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
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={handleRespond}
          className="border-t border-neutral-text-secondary/10 p-4"
        >
          <div className="flex gap-3">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={
                needsToTake
                  ? 'Toma el ticket primero para responder...'
                  : 'Escribe tu respuesta como operador...'
              }
              className="input-aesa flex-1"
              disabled={needsToTake || respondMutation.isPending}
            />
            <Button
              type="submit"
              disabled={!message.trim() || needsToTake || respondMutation.isPending}
              isLoading={respondMutation.isPending}
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
