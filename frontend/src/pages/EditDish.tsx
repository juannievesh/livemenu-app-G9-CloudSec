import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchApi } from '../services/api';
import { OnboardingEmpty } from '../components/OnboardingEmpty';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  tags?: string[];
  image_urls?: Record<string, string>;
}

interface Restaurant {
  id: string;
  name: string;
}

export default function EditDish() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = !id || id === 'new';
  const [categories, setCategories] = useState<Category[]>([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [offerPrice, setOfferPrice] = useState('');
  const [available, setAvailable] = useState(true);
  const [featured, setFeatured] = useState(false);
  const [tags, setTags] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      let cats: Category[] = [];
      let rest: Restaurant[] = [];
      try {
        [cats, rest] = await Promise.all([
          fetchApi<Category[]>('/admin/categories'),
          fetchApi<Restaurant>('/admin/restaurant'),
        ]);
        setCategories(Array.isArray(cats) ? cats : []);
        setRestaurants(rest ? [rest] : []);
      } catch {
        setCategories([]);
        setRestaurants([]);
      }
      if (!isNew && id) {
        try {
          const d = await fetchApi<Dish>(`/admin/dishes/${id}`);
          setName(d.name);
          setDescription(d.description || '');
          setPrice(String(d.price));
          setOfferPrice(d.offer_price ? String(d.offer_price) : '');
          setAvailable(d.available);
          setFeatured(d.featured);
          setCategoryId(d.category_id);
          setTags(Array.isArray(d.tags) ? d.tags.join(', ') : '');
          const urls = d.image_urls;
          setImagePreview(urls?.medium || urls?.large || urls?.thumbnail || null);
        } catch {
          setError('Plato no encontrado');
        }
      } else if (cats.length) {
        setCategoryId(cats[0].id);
      }
      setLoading(false);
    })();
  }, [id, isNew]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const payload = {
        name,
        description: description || undefined,
        price: parseFloat(price),
        offer_price: offerPrice ? parseFloat(offerPrice) : undefined,
        available,
        featured,
        category_id: categoryId,
        tags: tags ? tags.split(',').map((t) => t.trim()).filter(Boolean) : [],
      };
      if (isNew) {
        const created = await fetchApi<Dish>('/admin/dishes', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        navigate(`/dishes/${created.id}`);
      } else {
        if (!id) {
          setError('Error inesperado. Vuelve a la lista de platos.');
          return;
        }
        await fetchApi(`/admin/dishes/${id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setSaving(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !id || isNew) return;
    setUploading(true);
    setError('');
    try {
      const token = localStorage.getItem('token');
      const form = new FormData();
      form.append('file', file);
      form.append('dish_id', id);
      const res = await fetch(`${API_BASE}/api/v1/admin/upload`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error((data as { detail?: string }).detail || 'Error al subir');
      }
      await res.json();
      setError('');
      setImagePreview(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setUploading(false);
    }
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

  if (isNew && !categories.length) {
    return <OnboardingEmpty step="categories" />;
  }

  return (
    <div className="flex flex-col min-h-screen p-6 pb-24">
      <h1 className="text-xl font-bold mb-6">
        {isNew ? 'Nuevo plato' : 'Editar plato'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label>Imagen</Label>
          <div className="mt-2 flex items-center gap-4">
            {imagePreview ? (
              <img
                src={imagePreview}
                alt=""
                className="h-24 w-24 rounded object-cover"
              />
            ) : (
              <div className="h-24 w-24 rounded bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-400 text-sm">
                Sin imagen
              </div>
            )}
            {!isNew && (
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={handleUpload}
                  disabled={uploading}
                />
                <span className="text-sm text-amber-600 hover:underline">
                  {uploading ? 'Subiendo...' : 'Subir imagen'}
                </span>
              </label>
            )}
          </div>
        </div>

        <div>
          <Label htmlFor="name">Nombre</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="desc">Descripción</Label>
          <Textarea
            id="desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="category">Categoría</Label>
          <select
            id="category"
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            required
            className="mt-1 w-full h-10 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3"
          >
            <option value="">Seleccionar</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <Label htmlFor="price">Precio ($)</Label>
          <Input
            id="price"
            type="number"
            step="0.01"
            min="0"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor="offer">Precio oferta ($)</Label>
          <Input
            id="offer"
            type="number"
            step="0.01"
            min="0"
            value={offerPrice}
            onChange={(e) => setOfferPrice(e.target.value)}
            className="mt-1"
          />
        </div>
        <div className="flex items-center justify-between">
          <Label>Disponible</Label>
          <Switch checked={available} onCheckedChange={setAvailable} />
        </div>
        <div className="flex items-center justify-between">
          <Label>Destacado</Label>
          <Switch checked={featured} onCheckedChange={setFeatured} />
        </div>
        <div>
          <Label htmlFor="tags">Etiquetas</Label>
          <Input
            id="tags"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="vegetariano, picante, sin gluten"
            className="mt-1"
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex gap-2">
          <Button type="submit" disabled={saving} className="flex-1">
            {saving ? 'Guardando...' : 'Guardar'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
}
