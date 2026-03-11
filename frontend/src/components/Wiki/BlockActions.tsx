import { useState } from 'react';
import { toast } from 'sonner';

interface BlockActionsProps {
  blockId: string;
  userId: string;
  verificationStatus: string;
  communityTrustScore: number;
  onVerify?: () => void;
  onFlag?: () => void;
}

export const BlockActions: React.FC<BlockActionsProps> = ({
  blockId, userId, verificationStatus, communityTrustScore, onVerify, onFlag
}) => {
  const [showFlagModal, setShowFlagModal] = useState(false);
  const [flagReason, setFlagReason] = useState('');
  const [flagComment, setFlagComment] = useState('');

  const handleVerify = async () => {
    await fetch(`/api/v1/blocks/block/${blockId}/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId })
    });
    toast.success("Block verified!");
    if (onVerify) onVerify();
  };

  const handleFlag = async () => {
    await fetch(`/api/v1/blocks/block/${blockId}/flag`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, reason: flagReason, comment: flagComment })
    });
    toast.error("Block flagged – sent for review.");
    setShowFlagModal(false);
    if (onFlag) onFlag();
  };

  return (
    <div className="flex gap-4 items-center mt-2">
      <button
        className="px-2 py-1 bg-green-100 rounded"
        onClick={handleVerify}
        aria-label="Verify block"
        disabled={verificationStatus === "COMMUNITY_VERIFIED"}
      >Verify</button>
      <button
        className="px-2 py-1 bg-red-100 rounded"
        onClick={() => setShowFlagModal(true)}
        aria-label="Flag block"
      >Flag</button>
      {showFlagModal && (
        <div className="fixed z-50 inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white p-4 w-80 rounded shadow">
            <h4 className="mb-2 font-bold">Flag Content</h4>
            <select className="w-full mb-2"
              value={flagReason}
              onChange={e => setFlagReason(e.target.value)}>
              <option value="">Select reason</option>
              <option value="incorrect">Incorrect Data</option>
              <option value="outdated">Outdated</option>
              <option value="other">Other</option>
            </select>
            <textarea
              className="w-full mb-2 border rounded"
              rows={3}
              placeholder="Optional comment"
              value={flagComment}
              onChange={e => setFlagComment(e.target.value)}
            />
            <button className="px-3 py-1 bg-red-500 text-white rounded mr-2" onClick={handleFlag}>Submit Flag</button>
            <button className="px-3 py-1" onClick={() => setShowFlagModal(false)}>Cancel</button>
          </div>
        </div>
      )}
      <span className="ml-auto text-xs">Trust: {communityTrustScore}</span>
    </div>
  );
};
