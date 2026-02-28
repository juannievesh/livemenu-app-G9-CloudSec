import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchApi } from '../services/api';
import { OnboardingEmpty } from '../components/OnboardingEmpty';
import { LayoutDashboard, ExternalLink, Plus, BookOpen, UtensilsCrossed, QrCode } from 'lucide-react';

interface Restaurant {
  id: string;
  name: string;
  slug?: string;
  address?: string;
}

export default function Dashboard() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchApi<Restaurant>('/admin/restaurant');
        setRestaurants(data ? [data] : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const restaurant = restaurants[0];
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const menuUrl = restaurant?.slug ? `${baseUrl}/m/${restaurant.slug}` : '';

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500">Cargando...</p>
      </div>
    );
  }

  if (!restaurant) {
    return <OnboardingEmpty step="restaurant" />;
  }

  return (
    <div className="flex flex-col min-h-screen p-6 pb-24 md:pb-6">
      <div className="w-full max-w-4xl mx-auto">
      <h1 className="text-xl font-bold mb-1">Bienvenido, {restaurant.name}</h1>
      <p className="text-slate-600 dark:text-slate-400 mb-6">Gestiona tu menú digital</p>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      <div className="grid gap-4 md:grid-cols-2">
        {menuUrl && (
          <a
            href={menuUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4"
          >
            <div className="flex items-center gap-3">
              <LayoutDashboard className="h-8 w-8 text-amber-500" />
              <div>
                <p className="font-medium">Ver menú público</p>
                <p className="text-sm text-slate-500">Abre en nueva pestaña</p>
              </div>
            </div>
            <ExternalLink className="h-5 w-5 text-slate-400" />
          </a>
        )}

        <Link
          to="/categories"
          className="flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4"
        >
          <BookOpen className="h-8 w-8 text-amber-500" />
          <div>
            <p className="font-medium">Categorías</p>
            <p className="text-sm text-slate-500">Organiza tu menú</p>
          </div>
        </Link>

        <Link
          to="/dishes"
          className="flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4"
        >
          <UtensilsCrossed className="h-8 w-8 text-amber-500" />
          <div>
            <p className="font-medium">Platos</p>
            <p className="text-sm text-slate-500">Añade y edita platos</p>
          </div>
        </Link>

        <Link
          to="/qr"
          className="flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4"
        >
          <QrCode className="h-8 w-8 text-amber-500" />
          <div>
            <p className="font-medium">Mi código QR</p>
            <p className="text-sm text-slate-500">Descarga e imprime</p>
          </div>
        </Link>
      </div>
      </div>
    </div>
  );
}
