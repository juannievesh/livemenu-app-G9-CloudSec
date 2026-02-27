import { useState, useEffect } from 'react';
import { fetchApi, fetchBlob } from '../services/api';
import { OnboardingEmpty } from '../components/OnboardingEmpty';

interface Restaurant {
  id: string;
  name: string;
}

export default function QRCodePage() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [format, setFormat] = useState<'png' | 'svg'>('png');
  const [size, setSize] = useState<'S' | 'M' | 'L' | 'XL'>('M');
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    fetchApi<Restaurant>('/admin/restaurant')
      .then((data) => setRestaurants(data ? [data] : []))
      .catch(() => setRestaurants([]));
  }, []);

  useEffect(() => {
    if (!restaurants.length) return;
    let revoked = false;
    (async () => {
      try {
        const blob = await fetchBlob(`/admin/qr?format=${format}&size=${size}`);
        const url = URL.createObjectURL(blob);
        if (!revoked) setPreviewUrl((u) => { if (u) URL.revokeObjectURL(u); return url; });
        else URL.revokeObjectURL(url);
      } catch {
        setPreviewUrl(null);
      }
    })();
    return () => { revoked = true; setPreviewUrl((u) => { if (u) URL.revokeObjectURL(u); return null; }); };
  }, [format, size, restaurants.length]);

  const handleDownload = async () => {
    setLoading(true);
    try {
      const blob = await fetchBlob(`/admin/qr?format=${format}&size=${size}`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `qr-livemenu.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      const blob = await fetchBlob(`/admin/qr?format=${format}&size=${size}`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `qr-livemenu.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  };

  if (!restaurants.length) {
    return <OnboardingEmpty step="restaurant" />;
  }

  return (
    <div className="flex flex-col min-h-screen p-6 pb-24">
      <h1 className="text-xl font-bold mb-2">Mi código QR</h1>
      <p className="text-slate-600 dark:text-slate-400 mb-6">
        Escanea para ver el menú de tu restaurante
      </p>

      <div className="flex flex-col items-center rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-8 mb-6">
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Código QR"
            className="max-w-[280px] w-full h-auto"
          />
        ) : (
          <div className="h-[200px] w-[200px] bg-slate-200 dark:bg-slate-700 rounded flex items-center justify-center text-slate-500">
            Cargando...
          </div>
        )}
        <p className="text-sm text-slate-500 mt-4">Vista previa</p>
      </div>

      <div className="space-y-4 mb-6">
        <div>
          <label className="text-sm font-medium block mb-2">Formato</label>
          <select
            value={format}
            onChange={(e) => setFormat(e.target.value as 'png' | 'svg')}
            className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2"
          >
            <option value="png">PNG</option>
            <option value="svg">SVG</option>
          </select>
        </div>
        <div>
          <label className="text-sm font-medium block mb-2">Tamaño</label>
          <select
            value={size}
            onChange={(e) => setSize(e.target.value as 'S' | 'M' | 'L' | 'XL')}
            className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2"
          >
            <option value="S">S (200px)</option>
            <option value="M">M (400px)</option>
            <option value="L">L (800px)</option>
            <option value="XL">XL (1200px)</option>
          </select>
        </div>
      </div>

      <button
        type="button"
        onClick={handleDownload}
        disabled={loading}
        className="w-full rounded-lg bg-amber-500 py-3 text-slate-900 font-medium hover:bg-amber-600 disabled:opacity-50"
      >
        {loading ? 'Descargando...' : 'Descargar código QR'}
      </button>
    </div>
  );
}
