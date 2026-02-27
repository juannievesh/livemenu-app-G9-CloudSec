import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { fetchApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';

interface Restaurant {
  id: string;
  name: string;
  slug?: string;
  address?: string;
  description?: string;
}

export default function Settings() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const navigate = useNavigate();
  const { logout } = useAuth();

  const restaurant = restaurants[0];

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchApi<Restaurant[]>('/restaurants/');
        const list = Array.isArray(data) ? data : [];
        setRestaurants(list);
        if (list[0]) {
          setName(list[0].name);
          setAddress(list[0].address || '');
        }
      } catch {
        setRestaurants([]);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      if (restaurant) {
        await fetchApi(`/restaurants/${restaurant.id}`, {
          method: 'PUT',
          body: JSON.stringify({ name, address }),
        });
      } else {
        await fetchApi('/restaurants/', {
          method: 'POST',
          body: JSON.stringify({ name, address }),
        });
        navigate('/');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!restaurant || !deleteConfirm) return;
    setSaving(true);
    try {
      await fetchApi(`/restaurants/${restaurant.id}`, { method: 'DELETE' });
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al eliminar');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500">Cargando...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen p-6 pb-24">
      <h1 className="text-xl font-bold mb-6">
        {restaurant ? 'Configuración del restaurante' : 'Crear restaurante'}
      </h1>

      <form onSubmit={handleSave} className="space-y-4">
        <div>
          <Label htmlFor="name">Nombre del restaurante</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ej: El Buen Sabor"
            required
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="address">Dirección</Label>
          <Input
            id="address"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Calle, número, ciudad"
            className="mt-1"
          />
        </div>
        {restaurant?.slug && (
          <div>
            <Label>Slug (URL)</Label>
            <p className="text-sm text-slate-500 mt-1">{restaurant.slug}</p>
          </div>
        )}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button type="submit" className="w-full" disabled={saving}>
          {saving ? 'Guardando...' : restaurant ? 'Guardar cambios' : 'Crear restaurante'}
        </Button>
      </form>

      <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700">
        <Button type="button" variant="outline" className="w-full" onClick={logout}>
          Cerrar sesión
        </Button>
      </div>

      {restaurant && (
        <div className="mt-12 pt-8 border-t border-slate-200 dark:border-slate-700">
          <h2 className="text-sm font-medium text-red-600 mb-2">Zona de peligro</h2>
          {!deleteConfirm ? (
            <Button
              type="button"
              variant="outline"
              className="border-red-300 text-red-600 hover:bg-red-50"
              onClick={() => setDeleteConfirm(true)}
            >
              Eliminar restaurante
            </Button>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-slate-600">¿Seguro? Esta acción no se puede deshacer.</p>
              <div className="flex gap-2">
                <Button
                  type="button"
                  className="bg-red-600 hover:bg-red-700"
                  onClick={handleDelete}
                  disabled={saving}
                >
                  Sí, eliminar
                </Button>
                <Button type="button" variant="outline" onClick={() => setDeleteConfirm(false)}>
                  Cancelar
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
