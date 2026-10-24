import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';

interface Analogy {
  id?: number;
  title?: string;
  jurisdiction?: string;
  year?: number | string;
  outcome?: string;
  similarity?: string;
}

export default function AnalogiesList({ sid }: { sid: string }) {
  const [rows, setRows] = useState<Analogy[]>([]);
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
        const d = await apiGet(`/api/policy/${sid}/analogies`);
        const list: Analogy[] = Array.isArray(d) ? d : (d?.rows ?? []);
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
  if (loading) return <p className="text-sm text-inksoft">Loading analogies…</p>;
  if (err) return <p className="text-sm text-red-700">{err}</p>;
  if (!rows.length) return <p className="text-sm text-inksoft">No analogies for this submission.</p>;

  return (
    <ul className="space-y-2">
      {rows.map((a, i) => (
        <li key={a.id ?? i} className="rounded border border-navy/20 bg-paper p-3 text-xs">
          <p className="font-semibold text-navy">
            {a.title ?? 'Historical analogy'}
            {a.jurisdiction || a.year ? (
              <span className="ml-2 font-normal text-inksoft">
                {a.jurisdiction ?? ''}{a.jurisdiction && a.year ? ' · ' : ''}{a.year ?? ''}
              </span>
            ) : null}
          </p>
          {a.outcome && <p className="mt-1 text-navy/90">{a.outcome}</p>}
          {a.similarity && <p className="mt-1 text-inksoft">similarity: {a.similarity}</p>}
        </li>
      ))}
    </ul>
  );
}
