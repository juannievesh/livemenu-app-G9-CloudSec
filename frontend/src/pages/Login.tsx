import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { fetchApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { LogIn, UserPlus, Sun, Moon } from 'lucide-react';

const API_BASE = "https://livemenu-backend-403658009429.us-central1.run.app";

export default function Login() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      if (mode === 'register') {
        await fetchApi('/auth/register', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });
        setError('');
        setSuccess('¡Listo! Ahora ingresa a la aplicación con tu usuario y contraseña.');
        setPassword('');
        setMode('login');
      } else {
        setSuccess('');
        const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al iniciar sesión');
        const token = data.access_token;
        if (!token) throw new Error('No se recibió token');
        localStorage.setItem('token', token);
        login(token);
        navigate('/');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setLoading(false);
    }
  };

  const isLogin = mode === 'login';

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center p-6 transition-colors ${
      isLogin 
        ? 'bg-slate-100 dark:bg-slate-900' 
        : 'bg-amber-50 dark:bg-slate-950'
    }`}>
      {/* Theme toggle */}
      <button
        type="button"
        onClick={toggleTheme}
        className="absolute top-4 right-4 p-2 rounded-lg bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
        aria-label={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
      >
        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      </button>

      <div className={`w-full max-w-sm space-y-6 p-8 rounded-2xl shadow-lg transition-all ${
        isLogin 
          ? 'bg-white dark:bg-slate-800 border-2 border-indigo-200 dark:border-indigo-900/50' 
          : 'bg-white dark:bg-slate-800 border-2 border-amber-200 dark:border-amber-900/50'
      }`}>
        <div className="text-center">
          <div className={`inline-flex p-3 rounded-full mb-3 ${
            isLogin 
              ? 'bg-indigo-100 dark:bg-indigo-900/50' 
              : 'bg-amber-100 dark:bg-amber-900/50'
          }`}>
            {isLogin ? (
              <LogIn className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
            ) : (
              <UserPlus className="w-8 h-8 text-amber-600 dark:text-amber-400" />
            )}
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">LiveMenu</h1>
          <p className={`mt-1 font-medium ${
            isLogin 
              ? 'text-indigo-600 dark:text-indigo-400' 
              : 'text-amber-600 dark:text-amber-400'
          }`}>
            {isLogin ? 'Inicia sesión en tu cuenta' : 'Crea tu cuenta nueva'}
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            {isLogin ? 'Accede con tu email y contraseña' : 'Regístrate para comenzar a usar LiveMenu'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
              required
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="password">Contraseña</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
              className="mt-1"
            />
          </div>
          {error && (
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          )}
          {success && (
            <p className="text-sm text-green-600 dark:text-green-400">{success}</p>
          )}
          <Button
            type="submit"
            className={`w-full font-semibold text-white ${
              isLogin 
                ? 'bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600' 
                : 'bg-amber-500 hover:bg-amber-600 dark:bg-amber-500 dark:hover:bg-amber-600'
            }`}
            disabled={loading}
          >
            {loading ? '...' : isLogin ? 'Iniciar sesión' : 'Crear cuenta'}
          </Button>
        </form>

        <p className="text-center text-sm text-slate-600 dark:text-slate-400">
          {isLogin ? (
            <>
              ¿No tienes cuenta?{' '}
              <button
                type="button"
                onClick={() => { setMode('register'); setSuccess(''); setError(''); }}
                className="text-amber-600 dark:text-amber-400 hover:underline font-medium"
              >
                Regístrate
              </button>
            </>
          ) : (
            <>
              ¿Ya tienes cuenta?{' '}
              <button
                type="button"
                onClick={() => { setMode('login'); setSuccess(''); }}
                className="text-indigo-600 dark:text-indigo-400 hover:underline font-medium"
              >
                Inicia sesión
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
