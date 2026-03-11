import { useState, useMemo } from "react";
import { ValidationCard } from "./ValidationCard";
import useSWR from 'swr';

function useConflicts() {
  const { data, error, mutate } = useSWR('/api/v1/curation/conflicts', url => fetch(url).then(r => r.json()), { refreshInterval: 10000 });
  return { data, error, mutate };
}

export function CurationQueue() {
  const { data: conflicts, isLoading } = useConflicts();
  const [filters, setFilters] = useState({ type: "", severity: "", tier: "", status: "", search: "" });
  const filtered = useMemo(() =>
    (conflicts || []).filter(c =>
      (!filters.type || c.type === filters.type) &&
      (!filters.severity || c.severity === filters.severity) &&
      (!filters.tier || c.assigned_tier === Number(filters.tier)) &&
      (!filters.status || c.status === filters.status) &&
      (!filters.search || (c.current_value?.value || '').toLowerCase().includes(filters.search.toLowerCase()))
    ),
    [conflicts, filters]
  );

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <header className="flex gap-2 mb-3">
        <input placeholder="Search..." className="px-2 rounded border"
          value={filters.search} onChange={e => setFilters(f => ({ ...f, search: e.target.value }))} />
        <select value={filters.type} onChange={e => setFilters(f => ({ ...f, type: e.target.value }))}>
          <option value="">Type</option>
          <option value="QUANTITATIVE">Quantitative</option>
          <option value="NORMATIVE">Normative</option>
          <option value="CONTACT">Contact</option>
        </select>
        <select value={filters.severity} onChange={e => setFilters(f => ({ ...f, severity: e.target.value }))}>
          <option value="">Severity</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="MINOR">MINOR</option>
        </select>
        <select value={filters.tier} onChange={e => setFilters(f => ({ ...f, tier: e.target.value }))}>
          <option value="">Tier</option>
          <option value="1">Tier 1</option>
          <option value="2">Tier 2</option>
          <option value="3">Tier 3</option>
        </select>
      </header>
      <div>
        {filtered.map(conflict => (
          <ValidationCard
            key={conflict.conflict_id}
            {...conflict}
            onApprove={() => {}}
            onReject={() => {}}
            onEdit={() => {}}
            onEscalate={() => {}}
          />
        ))}
      </div>
    </div>
  );
}
