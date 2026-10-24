import { useEffect, useMemo, useState } from 'react';
import { apiGet } from '../lib/apiClient';

interface DemoRow {
  id?: number;
  group_name?: string;
  group?: string;
  impact_type?: string;
  impact?: string;
  magnitude?: string;
  explanation?: string;
  detail?: string;
}

type SortKey = 'group' | 'impact' | 'magnitude';

export default function DemographicGrid({ sid }: { sid: string }) {
  const [rows, setRows] = useState<DemoRow[]>([]);
  const [err, setErr] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [sortKey, setSortKey] = useState<SortKey>('group');
  const [asc, setAsc] = useState<boolean>(true);

  useEffect(() => {
    if (!sid) {
      setLoading(false);
      return;
    }
    let live = true;
    (async () => {
      try {
        const d = await apiGet(`/api/policy/${sid}/demographics`);
        const list: DemoRow[] = Array.isArray(d) ? d : (d?.rows ?? []);
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

  const sorted = useMemo(() => {
    const val = (r: DemoRow): string => {
      if (sortKey === 'group') return (r.group_name ?? r.group ?? '').toLowerCase();
      if (sortKey === 'impact') return (r.impact_type ?? r.impact ?? '').toLowerCase();
      return (r.magnitude ?? '').toLowerCase();
    };
    return [...rows].sort((a, b) => {
      const c = val(a).localeCompare(val(b));
      return asc ? c : -c;
    });
  }, [rows, sortKey, asc]);

  function toggle(k: SortKey) {
    if (k === sortKey) setAsc((v) => !v);
    else {
      setSortKey(k);
      setAsc(true);
    }
  }

  if (!sid) return <p className="text-sm text-inksoft">No submission selected.</p>;
  if (loading) return <p className="text-sm text-inksoft">Loading demographic impacts…</p>;
  if (err) return <p className="text-sm text-red-700">{err}</p>;
  if (!sorted.length) return <p className="text-sm text-inksoft">No demographic rows for this submission.</p>;

  return (
    <div className="overflow-x-auto rounded border border-navy/20">
      <table className="w-full text-left text-xs">
        <thead className="bg-navy text-paper">
          <tr>
            <th className="px-3 py-2">
              <button type="button" onClick={() => toggle('group')}>Group {sortKey === 'group' ? (asc ? '▲' : '▼') : ''}</button>
            </th>
            <th className="px-3 py-2">
              <button type="button" onClick={() => toggle('impact')}>Impact {sortKey === 'impact' ? (asc ? '▲' : '▼') : ''}</button>
            </th>
            <th className="px-3 py-2">
              <button type="button" onClick={() => toggle('magnitude')}>Magnitude {sortKey === 'magnitude' ? (asc ? '▲' : '▼') : ''}</button>
            </th>
            <th className="px-3 py-2">Explanation</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((r, i) => (
            <tr key={r.id ?? i} className={i % 2 ? 'bg-parchment' : 'bg-paper'}>
              <td className="px-3 py-2 font-semibold">{r.group_name ?? r.group ?? '—'}</td>
              <td className="px-3 py-2">{r.impact_type ?? r.impact ?? '—'}</td>
              <td className="px-3 py-2">{r.magnitude ?? '—'}</td>
              <td className="px-3 py-2 text-navy/90">{r.explanation ?? r.detail ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
