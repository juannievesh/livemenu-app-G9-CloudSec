import { useCallback } from 'react';
import { Switch } from './ui/switch';

const DAYS = [
  { key: 'lunes', label: 'Lun' },
  { key: 'martes', label: 'Mar' },
  { key: 'miércoles', label: 'Mié' },
  { key: 'jueves', label: 'Jue' },
  { key: 'viernes', label: 'Vie' },
  { key: 'sábado', label: 'Sáb' },
  { key: 'domingo', label: 'Dom' },
] as const;

interface ScheduleEditorProps {
  value: Record<string, string>;
  onChange: (value: Record<string, string>) => void;
}

function parseRange(range: string): { open: string; close: string } {
  const parts = range.split('-');
  return { open: parts[0] || '12:00', close: parts[1] || '22:00' };
}

export function ScheduleEditor({ value, onChange }: ScheduleEditorProps) {
  const toggleDay = useCallback(
    (day: string, enabled: boolean) => {
      const next = { ...value };
      if (enabled) {
        next[day] = '12:00-22:00';
      } else {
        delete next[day];
      }
      onChange(next);
    },
    [value, onChange]
  );

  const updateTime = useCallback(
    (day: string, field: 'open' | 'close', time: string) => {
      const current = parseRange(value[day] || '12:00-22:00');
      current[field] = time;
      onChange({ ...value, [day]: `${current.open}-${current.close}` });
    },
    [value, onChange]
  );

  return (
    <div className="space-y-2">
      {DAYS.map(({ key, label }) => {
        const enabled = key in value;
        const { open, close } = enabled ? parseRange(value[key]) : { open: '12:00', close: '22:00' };

        return (
          <div
            key={key}
            className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2.5"
          >
            <div className="flex items-center gap-3">
              <Switch
                checked={enabled}
                onCheckedChange={(checked) => toggleDay(key, checked)}
              />
              <span className="text-sm font-medium flex-1">{label}</span>
              {!enabled && (
                <span className="text-sm text-slate-400">Cerrado</span>
              )}
            </div>
            {enabled && (
              <div className="flex items-center gap-2 mt-2 pl-14">
                <input
                  type="time"
                  value={open}
                  onChange={(e) => updateTime(key, 'open', e.target.value)}
                  className="h-8 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2 text-sm flex-1 min-w-0"
                />
                <span className="text-slate-400 text-xs shrink-0">a</span>
                <input
                  type="time"
                  value={close}
                  onChange={(e) => updateTime(key, 'close', e.target.value)}
                  className="h-8 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2 text-sm flex-1 min-w-0"
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
