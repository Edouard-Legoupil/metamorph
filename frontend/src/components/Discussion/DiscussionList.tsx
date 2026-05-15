import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { MessageCircle, Search, Plus, Eye, Clock, Check, X, AlertTriangle } from 'lucide-react';
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

interface DiscussionListProps {
  threads: DiscussionThread[];
  currentUserId: string;
  onThreadSelected: (thread: DiscussionThread) => void;
  onRefresh: () => void;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const THREAD_STATUSES = [
  'all', 'open', 'under_review', 'consensus_reached', 'no_consensus', 'rejected', 'escalated', 'resolved', 'closed'
];

const CONSENSUS_RESULTS = [
  'all', 'accept', 'reject', 'modify', 'no_consensus', 'escalate'
];

export const DiscussionList: React.FC<DiscussionListProps> = ({
  threads,
  currentUserId,
  onThreadSelected,
  onRefresh
}) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [consensusFilter, setConsensusFilter] = useState('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadTopic, setNewThreadTopic] = useState('');
  const [newThreadLinkedCardId, setNewThreadLinkedCardId] = useState('');
  const [newThreadLinkedBlockId, setNewThreadLinkedBlockId] = useState('');
  const [newThreadInitialComment, setNewThreadInitialComment] = useState('');

  const filteredThreads = threads.filter(thread => {
    // Search filter
    if (searchQuery && !thread.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !thread.topic.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Status filter
    if (statusFilter !== 'all' && thread.status !== statusFilter) {
      return false;
    }
    
    // Consensus filter
    if (consensusFilter !== 'all') {
      if (consensusFilter === 'none' && thread.consensus_result) {
        return false;
      }
      if (consensusFilter !== 'none' && thread.consensus_result !== consensusFilter) {
        return false;
      }
    }
    
    return true;
  });

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

  const handleCreateThread = async () => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      if (!apiKey) {
        toast.error('Authentication required');
        return;
      }
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/discussion/threads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify({
          title: newThreadTitle,
          topic: newThreadTopic,
          linked_card_id: newThreadLinkedCardId || undefined,
          linked_block_id: newThreadLinkedBlockId || undefined,
          linked_entity_id: undefined,
          evidence_quality: 'medium',
          policy_compliance: true,
          initial_comment: newThreadInitialComment
        })
      });
      
      if (response.ok) {
        toast.success('Thread created successfully');
        setShowCreateDialog(false);
        // Reset form
        setNewThreadTitle('');
        setNewThreadTopic('');
        setNewThreadLinkedCardId('');
        setNewThreadLinkedBlockId('');
        setNewThreadInitialComment('');
        onRefresh();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to create thread');
      }
    } catch (error) {
      console.error('Error creating thread:', error);
      toast.error('Failed to create thread');
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Discussion Threads</h1>
          <p className="text-muted-foreground">Collaborative knowledge refinement</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="mr-2 h-4 w-4" /> New Thread
          </Button>
          <Button variant="outline" onClick={onRefresh}>
            <span className="mr-2">🔄</span> Refresh
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search threads..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                {THREAD_STATUSES.filter(s => s !== 'all').map(status => (
                  <SelectItem key={status} value={status}>{status}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Consensus Filter */}
            <Select value={consensusFilter} onValueChange={setConsensusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Consensus" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Consensus</SelectItem>
                <SelectItem value="none">No Consensus</SelectItem>
                {CONSENSUS_RESULTS.filter(c => c !== 'all').map(consensus => (
                  <SelectItem key={consensus} value={consensus}>{consensus}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Threads Table */}
      <Card>
        <CardHeader>
          <CardTitle>Threads ({filteredThreads.length} of {threads.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredThreads.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">No discussion threads found.</p>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="mr-2 h-4 w-4" /> Create First Thread
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Topic</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Consensus</TableHead>
                  <TableHead>Comments</TableHead>
                  <TableHead>Watchers</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredThreads.map(thread => (
                  <TableRow 
                    key={thread.id}
                    className="cursor-pointer"
                    onClick={() => onThreadSelected(thread)}
                  >
                    <TableCell className="font-medium">
                      {thread.title}
                    </TableCell>
                    <TableCell>{thread.topic}</TableCell>
                    <TableCell>
                      <Badge variant={getStatusBadge(thread.status).variant}>
                        {getStatusBadge(thread.status).text}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {thread.consensus_result ? (
                        <Badge variant={getConsensusBadge(thread.consensus_result)?.variant || 'default'}>
                          {getConsensusBadge(thread.consensus_result)?.text || thread.consensus_result}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground text-xs">None</span>
                      )}
                    </TableCell>
                    <TableCell>{thread.comment_count}</TableCell>
                    <TableCell>{thread.watchers.length}</TableCell>
                    <TableCell className="text-sm">
                      {formatDate(thread.created_at)}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button 
                          size="sm" 
                          variant="ghost" 
                          onClick={(e) => {
                            e.stopPropagation();
                            onThreadSelected(thread);
                          }}
                          title="View thread"
                        >
                          <MessageCircle className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Create Thread Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Create New Discussion Thread</h2>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setShowCreateDialog(false)}
              >
                ×
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Title *</label>
                <Input
                  value={newThreadTitle}
                  onChange={(e) => setNewThreadTitle(e.target.value)}
                  placeholder="Enter thread title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Topic *</label>
                <Input
                  value={newThreadTopic}
                  onChange={(e) => setNewThreadTopic(e.target.value)}
                  placeholder="Enter topic or subject"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Linked Card ID (optional)</label>
                <Input
                  value={newThreadLinkedCardId}
                  onChange={(e) => setNewThreadLinkedCardId(e.target.value)}
                  placeholder="Enter card ID if applicable"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Linked Block ID (optional)</label>
                <Input
                  value={newThreadLinkedBlockId}
                  onChange={(e) => setNewThreadLinkedBlockId(e.target.value)}
                  placeholder="Enter block ID if applicable"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Initial Comment *</label>
                <textarea
                  value={newThreadInitialComment}
                  onChange={(e) => setNewThreadInitialComment(e.target.value)}
                  placeholder="Enter initial comment to start the discussion"
                  className="w-full p-2 border rounded-md min-h-[100px]"
                />
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <Button 
                  variant="outline"
                  onClick={() => setShowCreateDialog(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateThread}
                  disabled={!newThreadTitle.trim() || !newThreadTopic.trim() || !newThreadInitialComment.trim()}
                >
                  Create Thread
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Export default for easier importing
export default DiscussionList;