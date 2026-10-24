import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';

interface Stakeholder {
  id?: number;
  group_name?: string;
  group?: string;
  stance?: string;
  rating?: number;
  explanation?: string;
  detail?: string;
}

function stanceStyle(stance: string): string {
  const s = stance.toLowerCase();
  if (s === 'benefit') return 'border-navy/40 bg-paper';
  if (s === 'harm') return 'border-gold/60 bg-goldsoft/50';
  return 'border-navy/20 bg-parchment';
}

export default function StakeholderMap({ sid }: { sid: string }) {
  const [rows, setRows] = useState<Stakeholder[]>([]);
  const [err, setErr] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!sid) {
      setLoading(false);
      return;
    }
    let live = true;
    (async () => {
      try {
        const d = await apiGet(`/api/policy/${sid}/stakeholders`);
        const list: Stakeholder[] = Array.isArray(d) ? d : (d?.rows ?? []);
        if (live) setRows(list);
      } catch (e) {
        if (live) setErr(e instanceof Error ? e.message : 'Load failed.');
      } finally {
        if (live) setLoading(false);
      }
    })();
    return () => {
      live = false;
    };
  }, [sid]);

  if (!sid) return <p className="text-sm text-inksoft">No submission selected.</p>;
  if (loading) return <p className="text-sm text-inksoft">Loading stakeholder map…</p>;
  if (err) return <p className="text-sm text-red-700">{err}</p>;
  if (!rows.length) return <p className="text-sm text-inksoft">No stakeholder rows for this submission.</p>;

  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
      {rows.map((s, i) => {
        const stance = (s.stance ?? 'mixed').toLowerCase();
        return (
          <div key={s.id ?? i} className={`rounded border p-3 ${stanceStyle(stance)}`}>
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-semibold text-navy">{s.group_name ?? s.group ?? 'Stakeholder'}</p>
              <span className="rounded border border-navy/30 bg-paper px-1.5 py-0.5 text-[11px]">{stance}</span>
            </div>
            <p className="mt-1 text-xs text-inksoft">
              rating: <strong className="text-navy">{s.rating ?? '—'}</strong> / 5
            </p>
            <p className="mt-1 text-xs text-navy/90">{s.explanation ?? s.detail ?? ''}</p>
          </div>
        );
      })}
    </div>
  );
}
