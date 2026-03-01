import { QrCode, Sun, Moon } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export function MobileHeader() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 flex items-center justify-between px-4 py-3 bg-white/95 dark:bg-slate-900/95 backdrop-blur-lg border-b border-slate-100 dark:border-slate-800 md:hidden">
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500 text-slate-900">
          <QrCode className="h-4.5 w-4.5" />
        </div>
        <span className="text-base font-bold tracking-tight">LiveMenu</span>
      </div>

      <button
        type="button"
        onClick={toggleTheme}
        className="p-2 rounded-full text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        aria-label={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>
    </header>
  );
}
