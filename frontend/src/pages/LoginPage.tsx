import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MessageSquare } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/');
    } catch (error) {
      // Error manejado por el store
    }
  };

  return (
    <div className="min-h-screen gradient-premium flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 gradient-aesa rounded-aesa-lg shadow-aesa mb-4">
            <MessageSquare className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-neutral-text-primary mb-2">
            Helpdesk AESA
          </h1>
          <p className="text-neutral-text-secondary">
            Agente inteligente para consultas A2
          </p>
        </div>

        {/* Form */}
        <Card>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-neutral-text-primary mb-2">
                Iniciar sesión
              </h2>
              <p className="text-sm text-neutral-text-secondary">
                Accede a tu cuenta para continuar
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-aesa text-sm">
                {error}
              </div>
            )}

            <Input
              label="Email"
              type="email"
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <Input
              label="Contraseña"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              isLoading={isLoading}
            >
              Iniciar sesión
            </Button>

            <div className="text-center text-sm text-neutral-text-secondary">
              ¿No tienes cuenta?{' '}
              <Link
                to="/register"
                className="text-aesa-blue font-medium hover:text-aesa-blue-dark"
              >
                Regístrate aquí
              </Link>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
