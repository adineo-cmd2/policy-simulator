import { useState } from 'react';
import { apiPost } from '../lib/apiClient';

interface CompareSide {
  id?: number;
  title?: string;
  direction?: string;
  magnitude?: string;
  domain_area?: string;
  order?: number;
}

interface CompareRow {
  dimension: string;
  a: CompareSide | null;
  b: CompareSide | null;
  verdict: string;
}

function verdictStyle(v: string): string {
  if (v === 'same') return 'border-navy/30 bg-paper text-navy';
  if (v === 'contrast') return 'border-gold/60 bg-goldsoft text-navy';
  return 'border-navy/20 bg-parchment text-inksoft';
}

function sideText(s: CompareSide | null): string {
  if (!s) return '—';
  return `${s.title ?? 'effect'} (${s.direction ?? '?'}/${s.magnitude ?? '?'})`;
}

export default function PolicyCompare() {
  const [aId, setAId] = useState<string>('');
  const [bId, setBId] = useState<string>('');
  const [rows, setRows] = useState<CompareRow[]>([]);
  const [err, setErr] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  async function run() {
    setErr('');
    setLoading(true);
    try {
      const d = await apiPost('/api/policy/compare', {
        a_id: Number(aId),
        b_id: Number(bId),
      });
      // RULING (binding): compare returns a bare list — handle both shapes defensively.
      const list: CompareRow[] = Array.isArray(d) ? d : (d?.rows ?? []);
      setRows(list);
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Compare failed. Sign in via Settings first.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="grid grid-cols-1 gap-2 rounded border border-navy/20 bg-parchment p-4 md:grid-cols-3">
        <input
          value={aId}
          onChange={(e) => setAId(e.target.value)}
          placeholder="submission A id"
          inputMode="numeric"
          className="rounded border border-navy/30 bg-paper p-2 text-sm"
        />
        <input
          value={bId}
          onChange={(e) => setBId(e.target.value)}
          placeholder="submission B id"
          inputMode="numeric"
          className="rounded border border-navy/30 bg-paper p-2 text-sm"
        />
        <button
          type="button"
          onClick={run}
          disabled={loading || !aId || !bId}
          className="rounded bg-navy px-4 py-2 text-sm font-bold text-paper disabled:opacity-50"
        >
          {loading ? 'Comparing…' : 'Compare'}
        </button>
      </div>
      {err && <p className="mt-2 text-sm text-red-700">{err}</p>}
      {rows.length > 0 && (
        <div className="mt-4 overflow-x-auto rounded border border-navy/20">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy text-paper">
              <tr>
                <th className="px-3 py-2">Dimension</th>
                <th className="px-3 py-2">A</th>
                <th className="px-3 py-2">B</th>
                <th className="px-3 py-2">Verdict</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className={i % 2 ? 'bg-parchment' : 'bg-paper'}>
                  <td className="px-3 py-2 font-semibold">{r.dimension}</td>
                  <td className="px-3 py-2">{sideText(r.a)}</td>
                  <td className="px-3 py-2">{sideText(r.b)}</td>
                  <td className="px-3 py-2">
                    <span className={`rounded border px-1.5 py-0.5 ${verdictStyle(r.verdict)}`}>
                      {r.verdict}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && !err && rows.length === 0 && (
        <p className="mt-3 text-xs text-inksoft">Enter two submission ids and press Compare. Sign in via Settings first.</p>
      )}
    </div>
  );
}
