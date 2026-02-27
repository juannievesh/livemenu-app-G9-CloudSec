import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchApi } from '../services/api';
import { OnboardingEmpty } from '../components/OnboardingEmpty';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Switch } from '../components/ui/switch';
import { Plus, Pencil, Trash2 } from 'lucide-react';

interface Category {
  id: string;
  name: string;
}

interface Dish {
  id: string;
  name: string;
  description?: string;
  price: number;
  offer_price?: number;
  available: boolean;
  featured: boolean;
  category_id: string;
  image_urls?: Record<string, string>;
}

interface Restaurant {
  id: string;
  name: string;
}

export default function Dishes() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [dishes, setDishes] = useState<Dish[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const [dishesRes, catsRes, restRes] = await Promise.all([
        fetchApi<Dish[]>('/admin/dishes'),
        fetchApi<Category[]>('/admin/categories'),
        fetchApi<Restaurant>('/admin/restaurant'),
      ]);
      setDishes(Array.isArray(dishesRes) ? dishesRes : []);
      setCategories(Array.isArray(catsRes) ? catsRes : []);
      setRestaurants(restRes ? [restRes] : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggleAvailability = async (d: Dish) => {
    try {
      await fetchApi(`/admin/dishes/${d.id}/availability`, { method: 'PATCH' });
      setDishes((prev) =>
        prev.map((x) => (x.id === d.id ? { ...x, available: !x.available } : x))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    }
  };

  const handleDelete = async (d: Dish) => {
    if (!confirm('¿Eliminar este plato?')) return;
    try {
      await fetchApi(`/admin/dishes/${d.id}`, { method: 'DELETE' });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    }
  };

  const filtered = dishes.filter((d) => {
    if (categoryFilter !== 'all' && d.category_id !== categoryFilter) return false;
    if (search && !d.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const getImageUrl = (d: Dish) => {
    const urls = d.image_urls;
    if (!urls) return null;
    return urls.thumbnail || urls.medium || urls.large || null;
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500">Cargando...</p>
      </div>
    );
  }

  if (!restaurants.length) {
    return <OnboardingEmpty step="restaurant" />;
  }

  if (!categories.length) {
    return <OnboardingEmpty step="categories" />;
  }

  return (
    <div className="flex flex-col min-h-screen p-6 pb-24">
      <h1 className="text-xl font-bold mb-6">Platos</h1>
      {error && <p className="text-red-600 mb-4">{error}</p>}

      <div className="flex gap-2 mb-4">
        <Input
          placeholder="Buscar..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1"
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="w-[140px] h-10 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3"
        >
          <option value="all">Todas</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      <Link to="/dishes/new" className="mb-6">
        <Button className="w-full">
          <Plus className="h-4 w-4 mr-2" />
          Nuevo plato
        </Button>
      </Link>

      <ul className="space-y-2">
        {filtered.map((d) => (
          <li
            key={d.id}
            className="flex items-center gap-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3"
          >
            {getImageUrl(d) ? (
              <img
                src={getImageUrl(d)!}
                alt=""
                className="h-12 w-12 rounded object-cover"
              />
            ) : (
              <div className="h-12 w-12 rounded bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-400">
                —
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{d.name}</p>
              <p className="text-sm text-slate-500">
                ${Number(d.price).toFixed(2)}
                {d.offer_price && (
                  <span className="text-amber-600 ml-1">
                    (oferta ${Number(d.offer_price).toFixed(2)})
                  </span>
                )}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={d.available}
                onCheckedChange={() => toggleAvailability(d)}
              />
              <Link to={`/dishes/${d.id}`} className="p-2 text-slate-500 hover:text-amber-600">
                <Pencil className="h-4 w-4" />
              </Link>
              <button
                type="button"
                onClick={() => handleDelete(d)}
                className="p-2 text-slate-500 hover:text-red-600"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
