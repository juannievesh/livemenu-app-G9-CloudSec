import { useEffect, useState } from 'react';
import { fetchApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Pencil, Trash2, GripVertical } from 'lucide-react';

interface Category {
  id: string;
  name: string;
  description?: string;
  position: number;
}

export default function Categories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<{ open: boolean; category?: Category }>({ open: false });
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const data = await fetchApi<Category[]>('/admin/categories');
      setCategories(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setName('');
    setDescription('');
    setModal({ open: true });
  };

  const openEdit = (c: Category) => {
    setName(c.name);
    setDescription(c.description || '');
    setModal({ open: true, category: c });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      if (modal.category) {
        await fetchApi(`/admin/categories/${modal.category.id}`, {
          method: 'PUT',
          body: JSON.stringify({ name, description }),
        });
      } else {
        await fetchApi('/admin/categories', {
          method: 'POST',
          body: JSON.stringify({ name, description }),
        });
      }
      setModal({ open: false });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (c: Category) => {
    if (!confirm('¿Eliminar esta categoría?')) return;
    try {
      await fetchApi(`/admin/categories/${c.id}`, { method: 'DELETE' });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    }
  };

  const handleReorder = async (fromIdx: number, toIdx: number) => {
    const next = [...categories];
    const [removed] = next.splice(fromIdx, 1);
    next.splice(toIdx, 0, removed);
    setCategories(next);
    try {
      await fetchApi('/admin/categories/reorder', {
        method: 'PATCH',
        body: JSON.stringify({
          order: next.map((c, i) => ({ id: c.id, position: i })),
        }),
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
      load();
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
      <h1 className="text-xl font-bold mb-6">Categorías</h1>
      {error && <p className="text-red-600 mb-4">{error}</p>}

      <Button onClick={openCreate} className="mb-6 w-full">
        Nueva categoría
      </Button>

      <ul className="space-y-2">
        {categories.map((c, i) => (
          <li
            key={c.id}
            className="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3"
          >
            <div className="flex gap-1">
              {i > 0 && (
                <button
                  type="button"
                  onClick={() => handleReorder(i, i - 1)}
                  className="p-1 text-slate-400 hover:text-slate-600"
                >
                  <GripVertical className="h-4 w-4" />
                </button>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{c.name}</p>
              {c.description && (
                <p className="text-sm text-slate-500 truncate">{c.description}</p>
              )}
            </div>
            <button
              type="button"
              onClick={() => openEdit(c)}
              className="p-2 text-slate-500 hover:text-amber-600"
            >
              <Pencil className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => handleDelete(c)}
              className="p-2 text-slate-500 hover:text-red-600"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </li>
        ))}
      </ul>

      {modal.open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-sm rounded-xl bg-white dark:bg-slate-900 p-6">
            <h2 className="text-lg font-bold mb-4">
              {modal.category ? 'Editar categoría' : 'Nueva categoría'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="cat-name">Nombre</Label>
                <Input
                  id="cat-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="cat-desc">Descripción</Label>
                <Input
                  id="cat-desc"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={saving} className="flex-1">
                  {saving ? '...' : 'Guardar'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setModal({ open: false })}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
