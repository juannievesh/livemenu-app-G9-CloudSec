import { Link, useLocation } from 'react-router-dom';
import { Home, BookOpen, QrCode, UtensilsCrossed, Settings } from 'lucide-react';
import { cn } from '@/src/lib/utils';

export function BottomNav() {
  const path = useLocation().pathname;

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-lg border-t border-slate-100 dark:border-slate-800 pb-safe md:hidden">
      <div className="flex justify-around items-center px-2 py-3">
        <Link to="/" className="flex flex-col items-center gap-1 min-w-[64px] group">
          <Home className={cn("h-6 w-6", path === '/' ? "text-amber-500" : "text-slate-500")} />
          <span className={cn("text-[10px] font-medium", path === '/' ? "text-amber-500 font-bold" : "text-slate-500")}>Home</span>
        </Link>
        <Link to="/categories" className="flex flex-col items-center gap-1 min-w-[64px] group">
          <BookOpen className={cn("h-6 w-6", path.includes('/categories') ? "text-amber-500" : "text-slate-500")} />
          <span className={cn("text-[10px] font-medium", path.includes('/categories') ? "text-amber-500 font-bold" : "text-slate-500")}>Menu</span>
        </Link>
        <div className="relative -top-5">
          <Link to="/qr" className="flex h-14 w-14 items-center justify-center rounded-full bg-amber-500 text-slate-900 shadow-lg shadow-amber-500/40 transition-transform active:scale-95">
            <QrCode className="h-7 w-7" />
          </Link>
        </div>
        <Link to="/dishes" className="flex flex-col items-center gap-1 min-w-[64px] group">
          <UtensilsCrossed className={cn("h-6 w-6", path.includes('/dishes') ? "text-amber-500" : "text-slate-500")} />
          <span className={cn("text-[10px] font-medium", path.includes('/dishes') ? "text-amber-500 font-bold" : "text-slate-500")}>Dishes</span>
        </Link>
        <Link to="/settings" className="flex flex-col items-center gap-1 min-w-[64px] group">
          <Settings className={cn("h-6 w-6", path === '/settings' ? "text-amber-500" : "text-slate-500")} />
          <span className={cn("text-[10px] font-medium", path === '/settings' ? "text-amber-500 font-bold" : "text-slate-500")}>Settings</span>
        </Link>
      </div>
    </nav>
  );
}
