import { Link, useNavigate } from 'react-router-dom';
import { Store, BookOpen, UtensilsCrossed, ChevronRight, Sparkles, X } from 'lucide-react';

type Step = 'restaurant' | 'categories' | 'dishes';

interface OnboardingEmptyProps {
  step: Step;
}

const steps: { id: Step; label: string; icon: typeof Store; path: string }[] = [
  { id: 'restaurant', label: 'Crear restaurante', icon: Store, path: '/settings' },
  { id: 'categories', label: 'Crear categorías', icon: BookOpen, path: '/categories' },
  { id: 'dishes', label: 'Añadir platos', icon: UtensilsCrossed, path: '/dishes' },
];

export function OnboardingEmpty({ step }: OnboardingEmptyProps) {
  const navigate = useNavigate();
  const currentIdx = steps.findIndex((s) => s.id === step);
  const currentStep = steps[currentIdx];
  const Icon = currentStep.icon;

  const handleSkip = () => {
    navigate(currentStep.path);
  };

  return (
    <div className="fixed inset-0 z-[60] flex flex-col bg-slate-50 dark:bg-slate-950 pb-safe">
      {/* Botón saltar - esquina superior derecha */}
      <div className="flex justify-end p-4">
        <button
          type="button"
          onClick={handleSkip}
          className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-800 dark:text-slate-400 dark:hover:text-slate-300 transition-colors"
          aria-label="Saltar tutorial"
        >
          <X className="w-4 h-4" />
          Saltar
        </button>
      </div>

      {/* Contenido centrado - ocupa el resto de la pantalla */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-24 h-24 rounded-full bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center mb-8">
          <Icon className="w-12 h-12 text-amber-600 dark:text-amber-400" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-3">
          ¡Ey! Falta un paso
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mb-8 max-w-sm text-base">
          {step === 'restaurant' && (
            <>Primero debes crear tu restaurante para gestionar tu menú digital.</>
          )}
          {step === 'categories' && (
            <>Crea al menos una categoría para organizar tu menú (ej: Bebidas, Platos, Postres).</>
          )}
          {step === 'dishes' && (
            <>Añade platos a tus categorías para completar tu menú.</>
          )}
        </p>

        {/* Pasos del tutorial */}
        <div className="flex flex-wrap justify-center gap-2 mb-10">
          {steps.map((s, i) => {
            const StepIcon = s.icon;
            const isActive = i === currentIdx;
            const isDone = i < currentIdx;
            const isLocked = i > currentIdx;
            return (
              <div key={s.id} className="flex items-center">
                <div
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm transition-colors ${
                    isActive
                      ? 'bg-amber-500 text-slate-900 font-medium'
                      : isDone
                      ? 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500'
                  }`}
                >
                  <StepIcon className={`w-4 h-4 ${isLocked ? 'opacity-50' : ''}`} />
                  <span>{i + 1}. {s.label}</span>
                </div>
                {i < steps.length - 1 && (
                  <ChevronRight className="w-4 h-4 text-slate-300 dark:text-slate-600 mx-1" />
                )}
              </div>
            );
          })}
        </div>

        <Link
          to={currentStep.path}
          className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-8 py-4 text-lg text-slate-900 font-semibold hover:bg-amber-600 transition-colors shadow-lg shadow-amber-500/25"
        >
          <Sparkles className="w-5 h-5" />
          {step === 'restaurant' && 'Crear mi restaurante'}
          {step === 'categories' && 'Crear categoría'}
          {step === 'dishes' && 'Añadir plato'}
        </Link>

        {step === 'restaurant' && (
          <p className="mt-6 text-sm text-slate-500">
            Es obligatorio crear tu restaurante para continuar
          </p>
        )}
      </div>
    </div>
  );
}
