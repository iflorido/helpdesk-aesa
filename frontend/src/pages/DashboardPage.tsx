import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, MessageSquare, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { ticketsAPI } from '@/lib/api';
import { TicketStatus, TicketCategory } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';

const statusIcons = {
  [TicketStatus.OPEN]: Clock,
  [TicketStatus.IN_PROGRESS]: MessageSquare,
  [TicketStatus.ESCALATED]: AlertCircle,
  [TicketStatus.CLOSED]: CheckCircle2,
};

const statusColors = {
  [TicketStatus.OPEN]: 'text-blue-500',
  [TicketStatus.IN_PROGRESS]: 'text-yellow-500',
  [TicketStatus.ESCALATED]: 'text-orange-500',
  [TicketStatus.CLOSED]: 'text-green-500',
};

const statusLabels = {
  [TicketStatus.OPEN]: 'Abierto',
  [TicketStatus.IN_PROGRESS]: 'En progreso',
  [TicketStatus.ESCALATED]: 'Escalado',
  [TicketStatus.CLOSED]: 'Cerrado',
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showNewTicket, setShowNewTicket] = useState(false);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState<TicketCategory>(TicketCategory.LICENSING);

  const { data, isLoading } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => ticketsAPI.list(),
  });

  const createMutation = useMutation({
    mutationFn: ticketsAPI.create,
    onSuccess: (newTicket) => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      setShowNewTicket(false);
      setTitle('');
      navigate(`/chat/${newTicket.id}`);
    },
  });

  const handleCreateTicket = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({ title, category });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-text-primary mb-2">
            Mis consultas
          </h1>
          <p className="text-neutral-text-secondary">
            Gestiona tus tickets y consultas al agente AESA
          </p>
        </div>
        <Button onClick={() => setShowNewTicket(true)}>
          <Plus className="w-5 h-5" />
          Nueva consulta
        </Button>
      </div>

      {/* New Ticket Form */}
      {showNewTicket && (
        <Card>
          <form onSubmit={handleCreateTicket} className="space-y-4">
            <h3 className="text-lg font-semibold text-neutral-text-primary">
              Nueva consulta
            </h3>
            
            <Input
              label="Título"
              placeholder="¿Cuál es tu consulta?"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />

            <div>
              <label className="block text-sm font-medium text-neutral-text-primary mb-2">
                Categoría
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as TicketCategory)}
                className="input-aesa"
              >
                <option value={TicketCategory.LICENSING}>Licencias</option>
                <option value={TicketCategory.TECHNICAL}>Técnico</option>
                <option value={TicketCategory.GENERAL}>General</option>
                <option value={TicketCategory.DOCUMENTATION}>Documentación</option>
              </select>
            </div>

            <div className="flex gap-3">
              <Button type="submit" isLoading={createMutation.isPending}>
                Crear consulta
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => setShowNewTicket(false)}
              >
                Cancelar
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Tickets List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-aesa-blue border-t-transparent"></div>
        </div>
      ) : data?.tickets.length === 0 ? (
        <Card className="text-center py-12">
          <MessageSquare className="w-16 h-16 text-neutral-text-secondary/30 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-neutral-text-primary mb-2">
            No tienes consultas
          </h3>
          <p className="text-neutral-text-secondary mb-6">
            Crea tu primera consulta para empezar a usar el agente AESA
          </p>
          <Button onClick={() => setShowNewTicket(true)}>
            <Plus className="w-5 h-5" />
            Nueva consulta
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4">
          {data?.tickets.map((ticket) => {
            const StatusIcon = statusIcons[ticket.status];
            return (
              <Card
                key={ticket.id}
                className="cursor-pointer hover:shadow-aesa hover:scale-[1.02]"
                onClick={() => navigate(`/chat/${ticket.id}`)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <StatusIcon
                        className={`w-5 h-5 ${statusColors[ticket.status]}`}
                      />
                      <h3 className="font-semibold text-neutral-text-primary">
                        {ticket.title}
                      </h3>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-neutral-text-secondary">
                      <span className="px-2 py-1 bg-aesa-blue/10 text-aesa-blue rounded">
                        {statusLabels[ticket.status]}
                      </span>
                      <span>{ticket.message_count} mensajes</span>
                      <span>
                        {formatDistanceToNow(new Date(ticket.created_at), {
                          addSuffix: true,
                          locale: es,
                        })}
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
