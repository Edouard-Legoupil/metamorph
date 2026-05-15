import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DiscussionList } from '../components/Discussion/DiscussionList';
import { DiscussionThread } from '../components/Discussion/DiscussionThread';
import { Button } from '@/components/ui/button';
import { ArrowLeft, MessageCircle } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function DiscussionPage() {
  const { topicId, cardId } = useParams<{ topicId?: string; cardId?: string }>();
  const navigate = useNavigate();
  const [threads, setThreads] = useState<any[]>([]);
  const [selectedThread, setSelectedThread] = useState<any>(null);
  const [comments, setComments] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentUserId, setCurrentUserId] = useState('stub-user'); // Replace with actual user ID

  // Load user ID from localStorage if available
  useEffect(() => {
    const userId = localStorage.getItem('USER_ID') || 'stub-user';
    setCurrentUserId(userId);
  }, []);

  // Fetch discussion threads
  const fetchThreads = async () => {
    try {
      setIsLoading(true);
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      // Build query parameters based on context
      const params = new URLSearchParams();
      if (topicId) params.append('topic', topicId);
      if (cardId) params.append('linked_card_id', cardId);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/discussion/threads?${params.toString()}`, { headers });
      
      if (response.ok) {
        const data = await response.json();
        setThreads(data);
      } else {
        toast.error('Failed to fetch discussion threads');
      }
    } catch (error) {
      console.error('Error fetching discussion threads:', error);
      toast.error('Failed to fetch discussion threads');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch comments for a specific thread
  const fetchComments = async (threadId: string) => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/discussion/threads/${threadId}/comments`, { headers });
      
      if (response.ok) {
        const data = await response.json();
        setComments(data);
      } else {
        toast.error('Failed to fetch comments');
      }
    } catch (error) {
      console.error('Error fetching comments:', error);
      toast.error('Failed to fetch comments');
    }
  };

  useEffect(() => {
    fetchThreads();
  }, [topicId, cardId]);

  const handleThreadSelected = async (thread: any) => {
    setSelectedThread(thread);
    await fetchComments(thread.id);
  };

  const handleBackToList = () => {
    setSelectedThread(null);
    setComments([]);
  };

  const handleCommentAdded = (comment: any) => {
    setComments(prev => [...prev, comment]);
    // Update thread comment count
    setThreads(prev => prev.map(t => 
      t.id === selectedThread.id ? { ...t, comment_count: t.comment_count + 1 } : t
    ));
  };

  const handleWatchToggle = (threadId: string, isWatching: boolean) => {
    // Update the watcher count in the thread
    setThreads(prev => prev.map(t => 
      t.id === threadId 
        ? { 
            ...t, 
            watchers: isWatching 
              ? [...t.watchers, currentUserId] 
              : t.watchers.filter((id: string) => id !== currentUserId)
          }
        : t
    ));
  };

  const handleStatusUpdate = (status: string, consensusData?: any) => {
    // Update the thread status
    setThreads(prev => prev.map(t => 
      t.id === selectedThread.id 
        ? { 
            ...t, 
            status: status,
            consensus_result: consensusData?.consensus_result || t.consensus_result,
            resolution_summary: consensusData?.resolution_summary || t.resolution_summary
          }
        : t
    ));
    
    // If thread was closed, go back to list
    if (status === 'closed') {
      setTimeout(() => handleBackToList(), 2000);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {selectedThread ? (
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Button variant="outline" size="sm" onClick={handleBackToList}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Threads
            </Button>
            <h1 className="text-2xl font-bold">Discussion Thread</h1>
          </div>
          
          <DiscussionThread
            thread={selectedThread}
            comments={comments}
            currentUserId={currentUserId}
            onCommentAdded={handleCommentAdded}
            onWatchToggle={(isWatching) => handleWatchToggle(selectedThread.id, isWatching)}
            onStatusUpdate={handleStatusUpdate}
          />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-2xl font-bold">Discussion Threads</h1>
              <p className="text-muted-foreground">
                {topicId ? `Discussions about ${topicId}` : 'All discussion threads'}
              </p>
            </div>
          </div>
          
          <DiscussionList
            threads={threads}
            currentUserId={currentUserId}
            onThreadSelected={handleThreadSelected}
            onRefresh={fetchThreads}
          />
        </div>
      )}
    </div>
  );
}