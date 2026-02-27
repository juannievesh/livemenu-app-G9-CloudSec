import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { fetchApi } from '../services/api';
import { Sun, Moon } from 'lucide-react';
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
  logo_url?: string;
  phone?: string;
  horarios?: Record<string, string>;
}

export default function Settings() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [description, setDescription] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [phone, setPhone] = useState('');
  const [horarios, setHorarios] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const restaurant = restaurants[0];

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchApi<Restaurant>('/admin/restaurant');
        const r = data ? [data] : [];
        setRestaurants(r);
        if (r[0]) {
          setName(r[0].name);
          setAddress(r[0].address || '');
          setDescription(r[0].description || '');
          setLogoUrl(r[0].logo_url || '');
          setPhone(r[0].phone || '');
          setHorarios(r[0].horarios ? JSON.stringify(r[0].horarios, null, 2) : '');
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
      let horariosObj: Record<string, string> | undefined;
      if (horarios.trim()) {
        try {
          horariosObj = JSON.parse(horarios);
        } catch {
          setError('Horarios: JSON inválido');
          setSaving(false);
          return;
        }
      }
      const payload = { name, address, description: description || undefined, logo_url: logoUrl || undefined, phone: phone || undefined, horarios: horariosObj };
      if (restaurant) {
        await fetchApi('/admin/restaurant', {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
      } else {
        await fetchApi('/admin/restaurant', {
          method: 'POST',
          body: JSON.stringify(payload),
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
      await fetchApi('/admin/restaurant', { method: 'DELETE' });
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
        <div>
          <Label htmlFor="description">Descripción</Label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Breve descripción del restaurante"
            rows={2}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="logo">Logo (URL)</Label>
          <Input
            id="logo"
            type="url"
            value={logoUrl}
            onChange={(e) => setLogoUrl(e.target.value)}
            placeholder="https://..."
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="phone">Teléfono</Label>
          <Input
            id="phone"
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+34 600 000 000"
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="horarios">Horarios (JSON)</Label>
          <Textarea
            id="horarios"
            value={horarios}
            onChange={(e) => setHorarios(e.target.value)}
            placeholder='{"lunes":"12:00-22:00","martes":"12:00-22:00"}'
            rows={3}
            className="mt-1 font-mono text-sm"
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

      <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700 space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-600 dark:text-slate-400">Apariencia</span>
          <button
            type="button"
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
            aria-label={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
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
