import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Camera, Upload, CheckCircle } from 'lucide-react';
import { fetchApi } from '../services/api';
import { OnboardingEmpty } from '../components/OnboardingEmpty';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function resolveImageUrl(url: string): string {
  if (url.startsWith('http') || url.startsWith('blob:')) return url;
  return `${API_BASE}${url}`;
}

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

async function uploadImageForDish(dishId: string, file: File): Promise<void> {
  const token = localStorage.getItem('token');
  const form = new FormData();
  form.append('file', file);
  form.append('dish_id', dishId);
  const res = await fetch(`${API_BASE}/api/v1/admin/upload/`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error((data as { detail?: string }).detail || 'Error al subir imagen');
  }
}

export default function EditDish() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = !id || id === 'new';
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [categories, setCategories] = useState<Category[]>([]);
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [offerPrice, setOfferPrice] = useState('');
  const [available, setAvailable] = useState(true);
  const [featured, setFeatured] = useState(false);
  const [tags, setTags] = useState('');
  const [categoryId, setCategoryId] = useState('');

  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [success, setSuccess] = useState('');

  useEffect(() => {
    (async () => {
      let cats: Category[] = [];
      try {
        const [catsRes, restRes] = await Promise.all([
          fetchApi<Category[]>('/admin/categories'),
          fetchApi<Restaurant>('/admin/restaurant'),
        ]);
        cats = Array.isArray(catsRes) ? catsRes : [];
        setCategories(cats);
        setRestaurants(restRes ? [restRes] : []);
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
          const raw = urls?.medium || urls?.large || urls?.thumbnail || null;
          setImagePreview(raw ? resolveImageUrl(raw) : null);
        } catch {
          setError('Plato no encontrado');
        }
      } else if (cats.length) {
        setCategoryId(cats[0].id);
      }
      setLoading(false);
    })();
  }, [id, isNew]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (isNew) {
      setPendingFile(file);
      setImagePreview(URL.createObjectURL(file));
    } else if (id) {
      doUpload(file, id);
    }
  };

  const doUpload = async (file: File, dishId: string) => {
    setUploading(true);
    setError('');
    setUploadSuccess(false);
    setImagePreview(URL.createObjectURL(file));

    try {
      await uploadImageForDish(dishId, file);
      setUploadSuccess(true);
      setPendingFile(null);
      setTimeout(() => setUploadSuccess(false), 4000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al subir imagen');
      setImagePreview(null);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
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

        if (pendingFile) {
          try {
            await uploadImageForDish(created.id, pendingFile);
          } catch {
            // Dish created but image failed — not critical
          }
        }

        navigate('/dishes', { state: { success: `Plato "${created.name}" creado correctamente` } });
      } else {
        if (!id) return;
        await fetchApi(`/admin/dishes/${id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        setSuccess('Cambios guardados');
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
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

  if (!restaurants.length) return <OnboardingEmpty step="restaurant" />;
  if (isNew && !categories.length) return <OnboardingEmpty step="categories" />;

  return (
    <div className="flex flex-col min-h-screen p-6 pb-24 md:pb-6">
      <div className="w-full max-w-2xl mx-auto">
        <h1 className="text-xl font-bold mb-6">
          {isNew ? 'Nuevo plato' : 'Editar plato'}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Image picker — always visible */}
          <div>
            <Label>Imagen</Label>
            <label className="mt-2 flex flex-col items-center gap-3 p-4 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 hover:border-amber-400 dark:hover:border-amber-500 bg-slate-50 dark:bg-slate-800/50 cursor-pointer transition-colors">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={handleFileSelect}
                disabled={uploading}
              />
              {imagePreview ? (
                <img src={imagePreview} alt="" className="h-32 w-32 rounded-lg object-cover" />
              ) : (
                <div className="h-32 w-32 rounded-lg bg-slate-200 dark:bg-slate-700 flex flex-col items-center justify-center text-slate-400">
                  <Camera className="h-8 w-8 mb-1" />
                  <span className="text-xs">Sin imagen</span>
                </div>
              )}
              <span className="inline-flex items-center gap-1.5 text-sm font-medium text-amber-600 dark:text-amber-400">
                <Upload className="h-4 w-4" />
                {uploading
                  ? 'Subiendo...'
                  : imagePreview
                    ? 'Cambiar imagen'
                    : 'Seleccionar imagen'}
              </span>
              <span className="text-xs text-slate-400">JPG, PNG o WebP (max 5 MB)</span>
              {isNew && pendingFile && (
                <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
                  Se subirá al guardar el plato
                </span>
              )}
              {uploadSuccess && (
                <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">
                  Imagen subida correctamente. Se procesará en segundo plano.
                </span>
              )}
            </label>
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
          {success && (
            <p className="flex items-center gap-1.5 text-sm text-emerald-600">
              <CheckCircle className="h-4 w-4" /> {success}
            </p>
          )}

          <div className="flex gap-2">
            <Button type="submit" disabled={saving || uploading} className="flex-1">
              {saving ? 'Guardando...' : isNew ? 'Crear plato' : 'Guardar cambios'}
            </Button>
            <Button type="button" variant="outline" onClick={() => navigate('/dishes')}>
              Cancelar
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
