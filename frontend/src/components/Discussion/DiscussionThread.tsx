import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { MessageCircle, ThumbsUp, ThumbsDown, Eye, Clock, Check, X, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

// Types
interface DiscussionThread {
  id: string;
  title: string;
  topic: string;
  status: string;
  consensus_result: string | null;
  resolution_summary: string | null;
  linked_card_id: string | null;
  linked_block_id: string | null;
  linked_entity_id: string | null;
  evidence_quality: string | null;
  policy_compliance: boolean | null;
  created_at: string;
  created_by: string;
  updated_at: string | null;
  updated_by: string | null;
  resolved_at: string | null;
  resolved_by: string | null;
  watchers: string[];
  comment_count: number;
}

interface DiscussionComment {
  id: string;
  thread_id: string;
  content: string;
  created_at: string;
  created_by: string;
  updated_at: string | null;
  updated_by: string | null;
  is_edited: boolean;
  evidence_quality: string | null;
  policy_compliance: boolean | null;
  mentions: string[];
  attachments: string[];
}

interface DiscussionThreadProps {
  thread: DiscussionThread;
  comments: DiscussionComment[];
  currentUserId: string;
  onCommentAdded: (comment: DiscussionComment) => void;
  onWatchToggle: (isWatching: boolean) => void;
  onStatusUpdate: (status: string, consensusData?: any) => void;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const DiscussionThread: React.FC<DiscussionThreadProps> = ({
  thread,
  comments,
  currentUserId,
  onCommentAdded,
  onWatchToggle,
  onStatusUpdate
}) => {
  const navigate = useNavigate();
  const [newComment, setNewComment] = useState('');
  const [isWatching, setIsWatching] = useState(thread.watchers.includes(currentUserId));
  const [expandedComments, setExpandedComments] = useState<{[key: string]: boolean}>({});

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      open: { text: 'Open', variant: 'default' },
      under_review: { text: 'Under Review', variant: 'secondary' },
      consensus_reached: { text: 'Consensus Reached', variant: 'success' },
      no_consensus: { text: 'No Consensus', variant: 'destructive' },
      rejected: { text: 'Rejected', variant: 'destructive' },
      escalated: { text: 'Escalated', variant: 'warning' },
      resolved: { text: 'Resolved', variant: 'success' },
      closed: { text: 'Closed', variant: 'secondary' }
    };
    
    return statusConfig[status] || { text: status, variant: 'default' };
  };

  const getConsensusBadge = (consensus: string | null) => {
    if (!consensus) return null;
    
    const consensusConfig = {
      accept: { text: 'Accepted', variant: 'success' },
      reject: { text: 'Rejected', variant: 'destructive' },
      modify: { text: 'Modified', variant: 'warning' },
      no_consensus: { text: 'No Consensus', variant: 'secondary' },
      escalate: { text: 'Escalated', variant: 'warning' }
    };
    
    return consensusConfig[consensus] || { text: consensus, variant: 'default' };
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      if (!apiKey) {
        toast.error('Authentication required');
        return;
      }
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/discussion/threads/${thread.id}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify({
          content: newComment,
          evidence_quality: 'medium',
          policy_compliance: true,
          mentions: [],
          attachments: []
        })
      });
      
      if (response.ok) {
        const comment = await response.json();
        onCommentAdded(comment);
        setNewComment('');
        toast.success('Comment added successfully');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to add comment');
      }
    } catch (error) {
      console.error('Error adding comment:', error);
      toast.error('Failed to add comment');
    }
  };

  const handleWatchToggle = async () => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      if (!apiKey) {
        toast.error('Authentication required');
        return;
      }
      
      const endpoint = isWatching 
        ? `${API_BASE_URL}/api/v1/cards/discussion/threads/${thread.id}/watch`
        : `${API_BASE_URL}/api/v1/cards/discussion/threads/${thread.id}/watch`;
      const method = isWatching ? 'DELETE' : 'POST';
      
      const response = await fetch(endpoint, {
        method: method,
        headers: {
          'x-api-key': apiKey
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setIsWatching(!isWatching);
        onWatchToggle(!isWatching);
        toast.success(isWatching ? 'Unwatched thread' : 'Now watching thread');
      } else {
        toast.error('Failed to update watch status');
      }
    } catch (error) {
      console.error('Error toggling watch status:', error);
      toast.error('Failed to update watch status');
    }
  };

  const handleApplyConsensus = async (consensusResult: string) => {
    const resolutionSummary = prompt('Enter resolution summary:');
    if (!resolutionSummary) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      if (!apiKey) {
        toast.error('Authentication required');
        return;
      }
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/discussion/threads/${thread.id}/apply-consensus`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify({
          consensus_result: consensusResult,
          resolution_summary: resolutionSummary,
          evidence_quality: 'high',
          policy_compliance: true
        })
      });
      
      if (response.ok) {
        const updatedThread = await response.json();
        onStatusUpdate(updatedThread.status, { consensus_result: consensusResult });
        toast.success('Consensus applied successfully');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to apply consensus');
      }
    } catch (error) {
      console.error('Error applying consensus:', error);
      toast.error('Failed to apply consensus');
    }
  };

  const handleCloseThread = async () => {
    const resolutionSummary = prompt('Enter resolution summary:');
    if (!resolutionSummary) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      if (!apiKey) {
        toast.error('Authentication required');
        return;
      }
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/discussion/threads/${thread.id}/close`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify({
          resolution_summary: resolutionSummary,
          consensus_result: 'resolved'
        })
      });
      
      if (response.ok) {
        const updatedThread = await response.json();
        onStatusUpdate(updatedThread.status);
        toast.success('Thread closed successfully');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to close thread');
      }
    } catch (error) {
      console.error('Error closing thread:', error);
      toast.error('Failed to close thread');
    }
  };

  const toggleCommentExpand = (commentId: string) => {
    setExpandedComments(prev => ({
      ...prev,
      [commentId]: !prev[commentId]
    }));
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const statusBadge = getStatusBadge(thread.status);
  const consensusBadge = getConsensusBadge(thread.consensus_result);

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle className="text-xl font-bold">
              {thread.title}
            </CardTitle>
            <div className="flex gap-2 mt-2">
              <Badge variant={statusBadge.variant}>
                {statusBadge.text}
              </Badge>
              {consensusBadge && (
                <Badge variant={consensusBadge.variant}>
                  {consensusBadge.text}
                </Badge>
              )}
            </div>
          </div>
          <div className="flex gap-2 ml-4">
            <Button 
              size="sm" 
              variant="outline" 
              onClick={handleWatchToggle}
              title={isWatching ? 'Unwatch' : 'Watch'}
            >
              <Eye className="h-4 w-4 mr-1" />
              {isWatching ? 'Watching' : 'Watch'}
            </Button>
            {thread.status === 'open' && (
              <Button 
                size="sm" 
                variant="outline" 
                onClick={() => handleApplyConsensus('accept')}
                title="Apply Accept Consensus"
              >
                <Check className="h-4 w-4 mr-1 text-green-500" />
                Accept
              </Button>
            )}
            {thread.status === 'open' && (
              <Button 
                size="sm" 
                variant="outline" 
                onClick={() => handleApplyConsensus('reject')}
                title="Apply Reject Consensus"
              >
                <X className="h-4 w-4 mr-1 text-red-500" />
                Reject
              </Button>
            )}
            {thread.status === 'open' && (
              <Button 
                size="sm" 
                variant="outline" 
                onClick={() => handleApplyConsensus('escalate')}
                title="Escalate"
              >
                <AlertTriangle className="h-4 w-4 mr-1 text-yellow-500" />
                Escalate
              </Button>
            )}
            {thread.status === 'open' && (
              <Button 
                size="sm" 
                variant="outline" 
                onClick={handleCloseThread}
                title="Close Thread"
              >
                <Clock className="h-4 w-4 mr-1" />
                Close
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4 mb-6">
          <div className="flex items-center text-sm text-muted-foreground">
            <MessageCircle className="h-4 w-4 mr-2" />
            <span>Started by {thread.created_by} on {formatDate(thread.created_at)}</span>
          </div>
          
          {thread.resolution_summary && (
            <div className="bg-secondary p-3 rounded-lg">
              <strong>Resolution:</strong> {thread.resolution_summary}
            </div>
          )}
          
          <div className="flex gap-4 text-sm">
            <div className="flex items-center">
              <MessageCircle className="h-4 w-4 mr-1" />
              <span>{comments.length} comments</span>
            </div>
            <div className="flex items-center">
              <Eye className="h-4 w-4 mr-1" />
              <span>{thread.watchers.length} watchers</span>
            </div>
            {thread.evidence_quality && (
              <div className="flex items-center">
                <span>Evidence: {thread.evidence_quality}</span>
              </div>
            )}
            {thread.policy_compliance !== null && (
              <div className="flex items-center">
                <span>Policy: {thread.policy_compliance ? 'Compliant' : 'Non-compliant'}</span>
              </div>
            )}
          </div>
        </div>
        
        <Separator className="my-4" />
        
        <div className="space-y-4">
          <h4 className="font-semibold">Comments ({comments.length})</h4>
          
          {comments.length === 0 ? (
            <p className="text-muted-foreground text-sm">No comments yet. Be the first to comment!</p>
          ) : (
            <div className="space-y-4">
              {comments.map(comment => (
                <div key={comment.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>{comment.created_by.slice(0, 2).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-medium text-sm">{comment.created_by}</div>
                        <div className="text-xs text-muted-foreground">
                          {formatDate(comment.created_at)}
                          {comment.is_edited && <span className="ml-2">• Edited</span>}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="text-sm mt-2 whitespace-pre-wrap">
                    {expandedComments[comment.id] || comment.content.length <= 200 ? 
                      comment.content : 
                      comment.content.slice(0, 200) + '...'}
                    {comment.content.length > 200 && (
                      <Button 
                        size="sm" 
                        variant="link" 
                        className="text-xs p-0 h-auto" 
                        onClick={() => toggleCommentExpand(comment.id)}
                      >
                        {expandedComments[comment.id] ? 'Show less' : 'Show more'}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
      
      {thread.status === 'closed' ? (
        <CardFooter>
          <p className="text-sm text-muted-foreground">
            This thread is closed. No further comments can be added.
          </p>
        </CardFooter>
      ) : (
        <CardFooter>
          <div className="flex gap-2 w-full">
            <input
              type="text"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              className="flex-1 px-3 py-2 border rounded-md text-sm"
            />
            <Button 
              size="sm"
              onClick={handleAddComment}
              disabled={!newComment.trim()}
            >
              Post Comment
            </Button>
          </div>
        </CardFooter>
      )}
    </Card>
  );
};

// Export default for easier importing
export default DiscussionThread;