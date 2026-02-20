import { Link } from 'react-router-dom';
import { LogOut, User, MessageSquare, Shield } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export default function Navbar() {
  const { user, logout } = useAuthStore();

  return (
    <nav className="glass border-b border-neutral-text-secondary/10 sticky top-0 z-50">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 gradient-aesa rounded-aesa flex items-center justify-center shadow-aesa group-hover:scale-105">
              <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-neutral-text-primary text-lg">
                Helpdesk AESA
              </h1>
              <p className="text-xs text-neutral-text-secondary">
                Agente inteligente A2
              </p>
            </div>
          </Link>

          {/* Navigation */}
          <div className="flex items-center gap-4">
            {/* Operator panel link for admins */}
            {user?.is_admin && (
              <Link
                to="/operator"
                className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-aesa hover:bg-green-100 transition-all"
              >
                <Shield className="w-4 h-4" />
                <span className="hidden sm:inline text-sm font-medium">
                  Panel Operador
                </span>
              </Link>
            )}

            {/* User menu */}
            <div className="flex items-center gap-3 px-4 py-2 bg-white/50 rounded-aesa">
              <div className="w-8 h-8 gradient-aesa rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-neutral-text-primary">
                  {user?.full_name || user?.email}
                </p>
                <p className="text-xs text-neutral-text-secondary">
                  {user?.is_admin ? 'Operador' : user?.email}
                </p>
              </div>
            </div>

            <button
              onClick={logout}
              className="p-2 text-neutral-text-secondary hover:text-aesa-blue hover:bg-white/50 rounded-aesa"
              title="Cerrar sesión"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
