import { useEffect, useState } from 'react';
import { apiGet } from '../lib/apiClient';

export interface EffectNode {
  id: number;
  order: number;
  title: string;
  detail: string;
  domain_area: string;
  magnitude: string;
  direction: string;
  confidence: string;
  analogy: string;
  children?: EffectNode[];
}

function Badges({ n }: { n: EffectNode }) {
  return (
    <div className="mt-1 flex flex-wrap gap-1 text-[11px]">
      <span className="rounded border border-navy/30 bg-paper px-1.5 py-0.5">order {n.order}</span>
      <span className="rounded border border-navy/30 bg-paper px-1.5 py-0.5">{n.magnitude}</span>
      <span className="rounded border border-navy/30 bg-paper px-1.5 py-0.5">{n.direction}</span>
      <span
        className={
          'rounded border px-1.5 py-0.5 ' +
          (n.confidence === 'speculative'
            ? 'border-gold/60 bg-goldsoft'
            : 'border-navy/30 bg-paper')
        }
      >
        {n.confidence}
      </span>
    </div>
  );
}

function NodeCard({ n, depth }: { n: EffectNode; depth: number }) {
  const [open, setOpen] = useState<boolean>(depth < 2);
  const kids = n.children ?? [];
  return (
    <div
      className={
        'rounded border p-3 ' +
        (n.order === 1
          ? 'border-navy/40 bg-paper'
          : n.order === 2
            ? 'border-navy/25 bg-parchment'
            : 'border-gold/40 bg-goldsoft/40')
      }
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-2 text-left"
      >
        <span className="text-sm font-semibold text-navy">
          <span className="mr-2 inline-block rounded bg-navy px-1.5 py-0.5 align-middle text-[11px] font-bold text-paper">
            {n.order === 1 ? '1st' : n.order === 2 ? '2nd' : '3rd'}
          </span>
          {n.title}
        </span>
        <span className="shrink-0 text-xs text-inksoft">{open ? '▾' : '▸'}</span>
      </button>
      <Badges n={n} />
      {open && (
        <div className="mt-2">
          <p className="text-xs text-navy/90">{n.detail}</p>
          {n.domain_area && (
            <p className="mt-1 text-[11px] text-inksoft">area: {n.domain_area}</p>
          )}
          {n.analogy && (
            <p className="mt-1 text-[11px] text-inksoft">
              <span className="font-semibold">Analogy: </span>
              {n.analogy}
            </p>
          )}
          {kids.length > 0 && (
            <div className="mt-2 space-y-2 border-l-2 border-gold/60 pl-3">
              {kids.map((c) => (
                <NodeCard key={c.id} n={c} depth={depth + 1} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function EffectsTree({ sid }: { sid: string }) {
  const [roots, setRoots] = useState<EffectNode[]>([]);
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
        const d = await apiGet(`/api/policy/${sid}/impact`);
        const kids: EffectNode[] = Array.isArray(d?.children)
          ? d.children
          : Array.isArray(d)
            ? d
            : (d?.rows ?? []);
        if (live) setRoots(kids);
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

  if (!sid) return <p className="text-sm text-inksoft">No submission selected. Submit a policy first.</p>;
  if (loading) return <p className="text-sm text-inksoft">Loading effect tree…</p>;
  if (err) return <p className="text-sm text-red-700">{err}</p>;
  if (!roots.length) return <p className="text-sm text-inksoft">No effects modelled for this submission.</p>;

  return (
    <div className="space-y-3">
      {roots.map((n) => (
        <NodeCard key={n.id} n={n} depth={1} />
      ))}
    </div>
  );
}
