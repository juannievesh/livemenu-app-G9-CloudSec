import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { BottomNav } from './components/BottomNav';
import { MobileHeader } from './components/MobileHeader';
import { Sidebar } from './components/Sidebar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Categories from './pages/Categories';
import Dishes from './pages/Dishes';
import EditDish from './pages/EditDish';
import QRCodePage from './pages/QRCode';

function ProtectedRoute() {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return (
    <div className="relative flex min-h-screen w-full flex-col md:flex-row overflow-x-hidden bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-display">
      <Sidebar />
      <div className="flex-1 flex flex-col min-h-screen md:ml-60">
        <MobileHeader />
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
      <BottomNav />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/dishes" element={<Dishes />} />
            <Route path="/dishes/new" element={<EditDish />} />
            <Route path="/dishes/:id" element={<EditDish />} />
            <Route path="/qr" element={<QRCodePage />} />
          </Route>
        </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}
