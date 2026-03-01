import { Link, useLocation } from 'react-router-dom';
import { Home, BookOpen, QrCode, UtensilsCrossed, Settings, Sun, Moon } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { useTheme } from '../contexts/ThemeContext';

const navItems = [
  { to: '/', icon: Home, label: 'Home', match: (p: string) => p === '/' },
  { to: '/categories', icon: BookOpen, label: 'Menú', match: (p: string) => p.includes('/categories') },
  { to: '/qr', icon: QrCode, label: 'Código QR', match: (p: string) => p === '/qr' },
  { to: '/dishes', icon: UtensilsCrossed, label: 'Platos', match: (p: string) => p.includes('/dishes') },
  { to: '/settings', icon: Settings, label: 'Ajustes', match: (p: string) => p === '/settings' },
];

export function Sidebar() {
  const path = useLocation().pathname;
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="hidden md:flex flex-col w-60 fixed top-0 left-0 h-screen bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 z-30">
      <div className="flex items-center gap-2 px-6 py-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500 text-slate-900">
          <QrCode className="h-5 w-5" />
        </div>
        <span className="text-lg font-bold tracking-tight">LiveMenu</span>
      </div>

      <nav className="flex-1 flex flex-col gap-1 px-3 mt-2">
        {navItems.map(({ to, icon: Icon, label, match }) => {
          const active = match(path);
          return (
            <Link
              key={to}
              to={to}
              className={cn(
                'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                active
                  ? 'bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
              )}
            >
              <Icon className={cn('h-5 w-5', active ? 'text-amber-500' : '')} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="px-3 pb-4">
        <button
          type="button"
          onClick={toggleTheme}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          {theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
        </button>
      </div>
    </aside>
  );
}
