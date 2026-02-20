import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { AlertCircle, Clock, MessageSquare, Users } from 'lucide-react';
import { operatorAPI } from '@/lib/api';
import { TicketStatus } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import Card from '@/components/ui/Card';

const statusLabels = {
  [TicketStatus.OPEN]: 'Abierto',
  [TicketStatus.IN_PROGRESS]: 'En progreso',
  [TicketStatus.ESCALATED]: 'Escalado',
  [TicketStatus.CLOSED]: 'Cerrado',
};

export default function OperatorDashboardPage() {
  const navigate = useNavigate();

  const { data: stats } = useQuery({
    queryKey: ['operator-stats'],
    queryFn: operatorAPI.getStats,
    refetchInterval: 5000,
  });

  const { data, isLoading } = useQuery({
    queryKey: ['operator-tickets'],
    queryFn: () => operatorAPI.listTickets(),
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-neutral-text-primary mb-2">
          Panel de Operador
        </h1>
        <p className="text-neutral-text-secondary">
          Gestiona tickets escalados y responde a usuarios
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card glass={false} className="border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-text-secondary">Escalados</p>
                <p className="text-3xl font-bold text-neutral-text-primary">
                  {stats.escalated}
                </p>
              </div>
              <AlertCircle className="w-10 h-10 text-orange-500" />
            </div>
          </Card>

          <Card glass={false} className="border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-text-secondary">
                  En progreso
                </p>
                <p className="text-3xl font-bold text-neutral-text-primary">
                  {stats.in_progress}
                </p>
              </div>
              <Clock className="w-10 h-10 text-yellow-500" />
            </div>
          </Card>

          <Card glass={false} className="border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-text-secondary">Abiertos</p>
                <p className="text-3xl font-bold text-neutral-text-primary">
                  {stats.open}
                </p>
              </div>
              <MessageSquare className="w-10 h-10 text-blue-500" />
            </div>
          </Card>

          <Card glass={false} className="border-l-4 border-aesa-blue">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-text-secondary">Total</p>
                <p className="text-3xl font-bold text-neutral-text-primary">
                  {stats.total}
                </p>
              </div>
              <Users className="w-10 h-10 text-aesa-blue" />
            </div>
          </Card>
        </div>
      )}

      {/* Tickets List */}
      <Card>
        <h2 className="text-xl font-semibold text-neutral-text-primary mb-4">
          Tickets que requieren atención
        </h2>

        {isLoading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aesa-blue border-t-transparent"></div>
          </div>
        ) : data?.tickets.length === 0 ? (
          <div className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-neutral-text-secondary/30 mx-auto mb-4" />
            <p className="text-neutral-text-secondary">
              No hay tickets escalados en este momento
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {data?.tickets.map((ticket) => (
              <div
                key={ticket.id}
                className="p-4 bg-neutral-light rounded-aesa hover:bg-white cursor-pointer transition-all border-l-4 hover:shadow-aesa"
                style={{
                  borderLeftColor:
                    ticket.status === TicketStatus.ESCALATED
                      ? '#f97316'
                      : '#eab308',
                }}
                onClick={() => navigate(`/operator/ticket/${ticket.id}`)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          ticket.status === TicketStatus.ESCALATED
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {statusLabels[ticket.status]}
                      </span>
                      <h3 className="font-semibold text-neutral-text-primary">
                        {ticket.title}
                      </h3>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-neutral-text-secondary">
                      <span>{ticket.message_count} mensajes</span>
                      <span>
                        {formatDistanceToNow(new Date(ticket.created_at), {
                          addSuffix: true,
                          locale: es,
                        })}
                      </span>
                      {ticket.escalated_at && (
                        <span className="text-orange-600 font-medium">
                          Escalado hace{' '}
                          {formatDistanceToNow(new Date(ticket.escalated_at), {
                            locale: es,
                          })}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
