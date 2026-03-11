import React from "react";
import { CardSelectionDashboard } from "../components/CuratorWorkspace/CardSelectionDashboard";
import { CardEditor } from "../components/CuratorWorkspace/CardEditor";
import { useParams } from "react-router-dom";

export default function CuratorWorkspace() {
  const { cardId } = useParams();
  // Route: /curation for dashboard, /curation/card/:id for editor
  if (cardId) return <CardEditor cardId={cardId} initialCard={null} />;
  return <CardSelectionDashboard />;
}
