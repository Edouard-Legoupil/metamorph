import React from "react";

interface ValidationCardProps {
  conflict_id: string;
  type: string;
  severity: string;
  current_value: { value: string, source: string, date: string };
  incoming_value: { value: string, source: string, date: string };
  assigned_tier: 1|2|3;
  context: { document_title: string, page_reference: string, snippet: string };
  onApprove: () => void;
  onReject: () => void;
  onEdit: () => void;
  onEscalate: () => void;
}

export const ValidationCard: React.FC<ValidationCardProps> = ({
  conflict_id, type, severity, current_value, incoming_value, assigned_tier, context,
  onApprove, onReject, onEdit, onEscalate
}) => (
  <div className="bg-white border rounded-md mb-4 p-4 shadow">
    <div className="flex items-center gap-3 mb-2">
      <span className={`inline-flex text-2xl`}>
        {type === "QUANTITATIVE" ? "📊" : type === "NORMATIVE" ? "📄" : type === "CONTACT" ? "👤" : "🔗"}
      </span>
      <span className={`font-bold ${severity === "CRITICAL" ? "text-red-600" : "text-yellow-500"}`}>
        {severity === "CRITICAL" ? "🔴" : "🟡"} {severity}
      </span>
      <span className="ml-auto text-xs text-neutral-500">Tier {assigned_tier}</span>
    </div>
    <div className="mb-3">
      <strong>Current:</strong> {current_value.value}
      <span className="ml-2 text-xs text-neutral-500">({current_value.source}, {current_value.date})</span>
    </div>
    <div className="mb-3">
      <strong>Proposed:</strong> {incoming_value.value}
      <span className="ml-2 text-xs text-neutral-500">({incoming_value.source}, {incoming_value.date})</span>
    </div>
    <div className="bg-neutral-100 text-xs px-2 py-1 rounded mb-2">{context.document_title} · pg. {context.page_reference}</div>
    <div className="text-neutral-700 italic mb-2">"{context.snippet}"</div>
    <div className="flex gap-2">
      <button className="bg-green-100 px-2 py-1 rounded" onClick={onApprove}>Approve</button>
      <button className="bg-red-100 px-2 py-1 rounded" onClick={onReject}>Reject</button>
      <button className="bg-yellow-100 px-2 py-1 rounded" onClick={onEdit}>Edit</button>
      <button className="bg-orange-100 px-2 py-1 rounded" onClick={onEscalate}>Escalate</button>
    </div>
  </div>
);
