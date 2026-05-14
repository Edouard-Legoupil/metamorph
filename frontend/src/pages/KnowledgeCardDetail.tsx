import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, CardHeader, CardTitle, CardContent, CardDescription
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Edit, Trash2, Check, X, Eye, Clock, Calendar, Tag, FileText, Plus, Search, Filter } from 'lucide-react';
import { toast } from 'sonner';

// Types
interface KnowledgeCard {
  id: string;
  card_type: string;
  title: string;
  description: string | null;
  domain: string;
  status: string;
  validity_start: string | null;
  validity_end: string | null;
  created_at: string;
  created_by: string;
  updated_at: string | null;
  updated_by: string | null;
  approved_at: string | null;
  approved_by: string | null;
  rejected_at: string | null;
  rejected_by: string | null;
  source_websites: string[];
  source_documents: string[];
  source_entities: string[];
  tags: string[];
  confidence_score: number | null;
  version: number;
  blocks_count: number;
  validation_cards_count: number;
  discussion_threads_count: number;
}

interface WikiBlock {
  id: string;
  card_id: string;
  section_name: string;
  content: string;
  word_limit: number;
  block_type: string;
  template_query: string | null;
  generated_from: string | null;
  verification_state: string;
  verified_at: string | null;
  verified_by: string | null;
  verification_notes: string | null;
  confidence_score: number | null;
  source_website_id: string | null;
  source_file_id: string | null;
  source_document_id: string | null;
  extraction_date: string | null;
  extraction_tool: string | null;
  maintenance_tags: string[];
  is_live: boolean;
  created_at: string;
  created_by: string;
  updated_at: string | null;
  updated_by: string | null;
}

interface ValidationCard {
  id: string;
  target_type: string;
  target_id: string;
  card_id: string | null;
  current_value: string | null;
  proposed_value: string | null;
  diff: string | null;
  status: string;
  sensitivity: string;
  assigned_tier: string | null;
  confidence_score: number | null;
  evidence: string[];
  provenance: Record<string, any>;
  source_reliability: string | null;
  contradiction_type: string | null;
  assigned_to: string | null;
  assigned_at: string | null;
  assigned_by: string | null;
  due_date: string | null;
  resolved_at: string | null;
  resolved_by: string | null;
  resolution: string | null;
  resolution_type: string | null;
  created_at: string;
  created_by: string;
}

interface DiscussionThread {
  id: string;
  title: string;
  topic: string | null;
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

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const CARD_TYPES = [
  { value: 'KC-1', label: 'KC-1: Donor Intelligence' },
  { value: 'KC-2', label: 'KC-2: Field Context' },
  { value: 'KC-3', label: 'KC-3: Outcome Evidence' },
  { value: 'KC-4', label: 'KC-4: Partner Capacity' },
  { value: 'KC-5', label: 'KC-5: Track Record' },
  { value: 'KC-6', label: 'KC-6: Crisis Political Economy' },
];

const KnowledgeCardDetail: React.FC = () => {
  const { cardId } = useParams<{ cardId: string }>();
  const navigate = useNavigate();
  const [card, setCard] = useState<KnowledgeCard | null>(null);
  const [blocks, setBlocks] = useState<WikiBlock[]>([]);
  const [validationCards, setValidationCards] = useState<ValidationCard[]>([]);
  const [discussionThreads, setDiscussionThreads] = useState<DiscussionThread[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>('blocks');
  
  // Form state for creating/editing blocks
  const [isBlockDialogOpen, setIsBlockDialogOpen] = useState<boolean>(false);
  const [editingBlock, setEditingBlock] = useState<WikiBlock | null>(null);
  const [blockFormData, setBlockFormData] = useState({
    section_name: '',
    content: '',
    word_limit: 200,
    block_type: 'text' as string,
    template_query: '',
    generated_from: '',
    source_website_id: '',
    source_file_id: '',
    source_document_id: '',
    maintenance_tags: '',
    is_live: false,
  });

  // Fetch card details
  const fetchCardDetails = async () => {
    if (!cardId) return;
    
    try {
      setIsLoading(true);
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      // Fetch card
      const cardResponse = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}`, { headers });
      if (cardResponse.ok) {
        setCard(await cardResponse.json());
      }
      
      // Fetch blocks
      const blocksResponse = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/blocks`, { headers });
      if (blocksResponse.ok) {
        setBlocks(await blocksResponse.json());
      }
      
      // Fetch validation cards
      const validationResponse = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards?card_id=${cardId}`, { headers });
      if (validationResponse.ok) {
        setValidationCards(await validationResponse.json());
      }
      
      // Fetch discussion threads
      const threadsResponse = await fetch(`${API_BASE_URL}/api/v1/cards/discussion/threads?linked_card_id=${cardId}`, { headers });
      if (threadsResponse.ok) {
        setDiscussionThreads(await threadsResponse.json());
      }
    } catch (error) {
      console.error('Error fetching card details:', error);
      toast.error('Failed to fetch card details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCardDetails();
  }, [cardId]);

  // Handle block form changes
  const handleBlockFormChange = (field: string, value: any) => {
    setBlockFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Create or update wiki block
  const handleBlockSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cardId) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        section_name: blockFormData.section_name,
        content: blockFormData.content,
        word_limit: blockFormData.word_limit,
        block_type: blockFormData.block_type,
        template_query: blockFormData.template_query || undefined,
        generated_from: blockFormData.generated_from || undefined,
        source_website_id: blockFormData.source_website_id || undefined,
        source_file_id: blockFormData.source_file_id || undefined,
        source_document_id: blockFormData.source_document_id || undefined,
        maintenance_tags: blockFormData.maintenance_tags ? blockFormData.maintenance_tags.split(',').map(s => s.trim()) : [],
        is_live: blockFormData.is_live,
      };
      
      let response;
      if (editingBlock) {
        response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/blocks/${editingBlock.id}`, {
          method: 'PATCH',
          headers,
          body: JSON.stringify(payload),
        });
      } else {
        response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/blocks`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        });
      }
      
      if (response.ok) {
        toast.success(editingBlock ? 'Wiki block updated successfully' : 'Wiki block created successfully');
        setIsBlockDialogOpen(false);
        setEditingBlock(null);
        setBlockFormData({
          section_name: '',
          content: '',
          word_limit: 200,
          block_type: 'text',
          template_query: '',
          generated_from: '',
          source_website_id: '',
          source_file_id: '',
          source_document_id: '',
          maintenance_tags: '',
          is_live: false,
        });
        fetchCardDetails();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save wiki block');
      }
    } catch (error) {
      console.error('Error saving wiki block:', error);
      toast.error('Failed to save wiki block');
    }
  };

  // Delete wiki block
  const handleDeleteBlock = async (blockId: string) => {
    if (!confirm('Are you sure you want to delete this wiki block?')) return;
    if (!cardId) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/blocks/${blockId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Wiki block deleted successfully');
        fetchCardDetails();
      } else {
        toast.error('Failed to delete wiki block');
      }
    } catch (error) {
      console.error('Error deleting wiki block:', error);
      toast.error('Failed to delete wiki block');
    }
  };

  // Verify wiki block
  const handleVerifyBlock = async (blockId: string) => {
    if (!cardId) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        verification_state: 'accepted',
        verification_notes: 'Verified via UI',
        confidence_score: 0.95,
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/blocks/${blockId}/verify`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Wiki block verified successfully');
        fetchCardDetails();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to verify wiki block');
      }
    } catch (error) {
      console.error('Error verifying wiki block:', error);
      toast.error('Failed to verify wiki block');
    }
  };

  // Flag wiki block
  const handleFlagBlock = async (blockId: string) => {
    if (!cardId) return;
    const reason = prompt('Please enter flag reason:');
    if (!reason) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        verification_state: 'disputed',
        flag_reason: reason,
        suggested_action: 'Review source information',
        maintenance_tags: ['needs_review'],
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/blocks/${blockId}/flag`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Wiki block flagged successfully');
        fetchCardDetails();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to flag wiki block');
      }
    } catch (error) {
      console.error('Error flagging wiki block:', error);
      toast.error('Failed to flag wiki block');
    }
  };

  // Open edit block dialog
  const openEditBlockDialog = (block: WikiBlock) => {
    setEditingBlock(block);
    setBlockFormData({
      section_name: block.section_name,
      content: block.content,
      word_limit: block.word_limit,
      block_type: block.block_type,
      template_query: block.template_query || '',
      generated_from: block.generated_from || '',
      source_website_id: block.source_website_id || '',
      source_file_id: block.source_file_id || '',
      source_document_id: block.source_document_id || '',
      maintenance_tags: block.maintenance_tags.join(', '),
      is_live: block.is_live,
    });
    setIsBlockDialogOpen(true);
  };

  // Get verification state color
  const getVerificationStateColor = (state: string) => {
    switch (state) {
      case 'accepted':
        return 'bg-green-100 text-green-800';
      case 'auto_accepted':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'disputed':
        return 'bg-yellow-100 text-yellow-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'flagged':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get validation card status color
  const getValidationStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'merged':
        return 'bg-purple-100 text-purple-800';
      case 'escalated':
        return 'bg-yellow-100 text-yellow-800';
      case 'under_review':
        return 'bg-blue-100 text-blue-800';
      case 'no_consensus':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get discussion thread status color
  const getThreadStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-blue-100 text-blue-800';
      case 'under_review':
        return 'bg-yellow-100 text-yellow-800';
      case 'consensus_reached':
        return 'bg-green-100 text-green-800';
      case 'no_consensus':
        return 'bg-gray-100 text-gray-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'resolved':
        return 'bg-purple-100 text-purple-800';
      case 'archived':
        return 'bg-gray-200 text-gray-600';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p>Loading knowledge card details...</p>
        </div>
      </div>
    );
  }

  if (!card) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <Alert variant="destructive">
          <AlertTitle>Card not found</AlertTitle>
          <AlertDescription>
            The knowledge card you requested could not be found.
          </AlertDescription>
        </Alert>
        <Button onClick={() => navigate('/cards')} className="mt-4">
          Back to Knowledge Cards
        </Button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Knowledge Card: {card.title}</h1>
            <p className="text-muted-foreground">
              {CARD_TYPES.find(t => t.value === card.card_type)?.label} | {card.domain}
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => navigate('/cards')} variant="outline">
              Back to All Cards
            </Button>
          </div>
        </div>

        {/* Card Details */}
        <Card>
          <CardHeader>
            <CardTitle>Card Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <Label className="text-sm text-muted-foreground">Status</Label>
                <div className="flex items-center gap-2">
                  <Badge className={getStatusColor(card.status)}>
                    {card.status}
                  </Badge>
                </div>
              </div>
              <div>
                <Label className="text-sm text-muted-foreground">Created</Label>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>{formatDate(card.created_at)}</span>
                </div>
              </div>
              <div>
                <Label className="text-sm text-muted-foreground">Updated</Label>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>{formatDate(card.updated_at)}</span>
                </div>
              </div>
              <div>
                <Label className="text-sm text-muted-foreground">Version</Label>
                <div className="flex items-center gap-2">
                  <Tag className="h-4 w-4 text-muted-foreground" />
                  <span>v{card.version}</span>
                </div>
              </div>
            </div>
            
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm text-muted-foreground">Validity Period</Label>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>
                    {card.validity_start ? formatDate(card.validity_start) : 'No start'} → 
                    {card.validity_end ? formatDate(card.validity_end) : 'No end'}
                  </span>
                </div>
              </div>
              <div>
                <Label className="text-sm text-muted-foreground">Confidence Score</Label>
                <div className="flex items-center gap-2">
                  <span className="font-medium">
                    {card.confidence_score ? `${card.confidence_score * 100}%` : 'Not set'}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <Label className="text-sm text-muted-foreground">Description</Label>
              <p className="mt-1 text-muted-foreground">
                {card.description || 'No description provided'}
              </p>
            </div>
            
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label className="text-sm text-muted-foreground">Source Websites</Label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {card.source_websites.length > 0 ? (
                    card.source_websites.map(website => (
                      <Badge key={website} variant="outline" className="text-xs">
                        {website}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-muted-foreground">No source websites</span>
                  )}
                </div>
              </div>
              <div>
                <Label className="text-sm text-muted-foreground">Source Documents</Label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {card.source_documents.length > 0 ? (
                    card.source_documents.map(doc => (
                      <Badge key={doc} variant="outline" className="text-xs">
                        {doc}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-muted-foreground">No source documents</span>
                  )}
                </div>
              </div>
              <div>
                <Label className="text-sm text-muted-foreground">Source Entities</Label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {card.source_entities.length > 0 ? (
                    card.source_entities.map(entity => (
                      <Badge key={entity} variant="outline" className="text-xs">
                        {entity}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-muted-foreground">No source entities</span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <Label className="text-sm text-muted-foreground">Tags</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {card.tags.length > 0 ? (
                  card.tags.map(tag => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))
                ) : (
                  <span className="text-xs text-muted-foreground">No tags</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5">
            <TabsTrigger value="blocks">Blocks ({blocks.length})</TabsTrigger>
            <TabsTrigger value="validation">Validation ({validationCards.length})</TabsTrigger>
            <TabsTrigger value="discussion">Discussion ({discussionThreads.length})</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Blocks Tab */}
          <TabsContent value="blocks">
            <Card>
              <CardHeader className="flex flex-row justify-between items-center">
                <div>
                  <CardTitle>Wiki Blocks</CardTitle>
                  <CardDescription>
                    Content blocks for this knowledge card
                  </CardDescription>
                </div>
                <Dialog open={isBlockDialogOpen} onOpenChange={setIsBlockDialogOpen}>
                  <DialogTrigger asChild>
                    <Button onClick={() => {
                      setEditingBlock(null);
                      setBlockFormData({
                        section_name: '',
                        content: '',
                        word_limit: 200,
                        block_type: 'text',
                        template_query: '',
                        generated_from: '',
                        source_website_id: '',
                        source_file_id: '',
                        source_document_id: '',
                        maintenance_tags: '',
                        is_live: false,
                      });
                    }}>
                      <Plus className="mr-2 h-4 w-4" /> Add Block
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle>{editingBlock ? 'Edit Wiki Block' : 'Create New Wiki Block'}</DialogTitle>
                      <DialogDescription>
                        {editingBlock ? 'Update wiki block content' : 'Add a new content block to this knowledge card'}
                      </DialogDescription>
                    </DialogHeader>
                    
                    <form onSubmit={handleBlockSubmit} className="space-y-4">
                      {/* Section Name */}
                      <div className="space-y-2">
                        <Label htmlFor="section_name">Section Name *</Label>
                        <Input
                          id="section_name"
                          value={blockFormData.section_name}
                          onChange={(e) => handleBlockFormChange('section_name', e.target.value)}
                          placeholder="Section name (e.g., Donor Overview)"
                          required
                        />
                      </div>

                      {/* Content */}
                      <div className="space-y-2">
                        <Label htmlFor="content">Content *</Label>
                        <textarea
                          id="content"
                          value={blockFormData.content}
                          onChange={(e) => handleBlockFormChange('content', e.target.value)}
                          className="w-full min-h-[150px] p-2 border rounded-md"
                          placeholder="Block content"
                          required
                        />
                      </div>

                      {/* Word Limit */}
                      <div className="space-y-2">
                        <Label htmlFor="word_limit">Word Limit *</Label>
                        <Input
                          id="word_limit"
                          type="number"
                          value={blockFormData.word_limit}
                          onChange={(e) => handleBlockFormChange('word_limit', parseInt(e.target.value) || 0)}
                          min="1"
                          max="1000"
                          required
                        />
                      </div>

                      {/* Block Type */}
                      <div className="space-y-2">
                        <Label htmlFor="block_type">Block Type *</Label>
                        <Select
                          value={blockFormData.block_type}
                          onValueChange={(value) => handleBlockFormChange('block_type', value)}
                          required
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select block type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="text">Text</SelectItem>
                            <SelectItem value="table">Table</SelectItem>
                            <SelectItem value="list">List</SelectItem>
                            <SelectItem value="quote">Quote</SelectItem>
                            <SelectItem value="code">Code</SelectItem>
                            <SelectItem value="image">Image</SelectItem>
                            <SelectItem value="chart">Chart</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      {/* Template Query */}
                      <div className="space-y-2">
                        <Label htmlFor="template_query">Template Query</Label>
                        <Input
                          id="template_query"
                          value={blockFormData.template_query}
                          onChange={(e) => handleBlockFormChange('template_query', e.target.value)}
                          placeholder="Template query used"
                        />
                      </div>

                      {/* Source Information */}
                      <div className="grid grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="source_website_id">Source Website ID</Label>
                          <Input
                            id="source_website_id"
                            value={blockFormData.source_website_id}
                            onChange={(e) => handleBlockFormChange('source_website_id', e.target.value)}
                            placeholder="website_id"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="source_file_id">Source File ID</Label>
                          <Input
                            id="source_file_id"
                            value={blockFormData.source_file_id}
                            onChange={(e) => handleBlockFormChange('source_file_id', e.target.value)}
                            placeholder="file_id"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="source_document_id">Source Document ID</Label>
                          <Input
                            id="source_document_id"
                            value={blockFormData.source_document_id}
                            onChange={(e) => handleBlockFormChange('source_document_id', e.target.value)}
                            placeholder="doc_id"
                          />
                        </div>
                      </div>

                      {/* Maintenance Tags */}
                      <div className="space-y-2">
                        <Label htmlFor="maintenance_tags">Maintenance Tags (comma separated)</Label>
                        <Input
                          id="maintenance_tags"
                          value={blockFormData.maintenance_tags}
                          onChange={(e) => handleBlockFormChange('maintenance_tags', e.target.value)}
                          placeholder="tag1, tag2"
                        />
                      </div>

                      {/* Live Block */}
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id="is_live"
                          checked={blockFormData.is_live}
                          onChange={(e) => handleBlockFormChange('is_live', e.target.checked)}
                          className="h-4 w-4"
                        />
                        <Label htmlFor="is_live">Live-updating block</Label>
                      </div>

                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsBlockDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button type="submit" disabled={!blockFormData.section_name || !blockFormData.content}>
                          {editingBlock ? 'Update Wiki Block' : 'Create Wiki Block'}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                {blocks.length === 0 ? (
                  <Alert>
                    <AlertTitle>No wiki blocks found</AlertTitle>
                    <AlertDescription>
                      Add your first wiki block to this knowledge card
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Section</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Words</TableHead>
                        <TableHead>Verification</TableHead>
                        <TableHead>Source</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {blocks.map(block => (
                        <TableRow key={block.id}>
                          <TableCell className="font-medium">{block.section_name}</TableCell>
                          <TableCell>
                            <Badge variant="outline" className="text-xs">
                              {block.block_type}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              {block.content.split(' ').length}/{block.word_limit}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Badge className={getVerificationStateColor(block.verification_state)}>
                                {block.verification_state}
                              </Badge>
                              {block.confidence_score && (
                                <span className="text-xs text-muted-foreground">
                                  ({Math.round(block.confidence_score * 100)}%)
                                </span>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-xs">
                              {block.source_website_id && (
                                <div>Website: {block.source_website_id}</div>
                              )}
                              {block.source_file_id && (
                                <div>File: {block.source_file_id}</div>
                              )}
                              {block.source_document_id && (
                                <div>Doc: {block.source_document_id}</div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-1">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => openEditBlockDialog(block)}
                                title="Edit"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              {block.verification_state === 'pending' && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => handleVerifyBlock(block.id)}
                                  title="Verify"
                                >
                                  <Check className="h-4 w-4 text-green-500" />
                                </Button>
                              )}
                              {block.verification_state !== 'accepted' && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => handleFlagBlock(block.id)}
                                  title="Flag"
                                >
                                  <X className="h-4 w-4 text-red-500" />
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-red-500 hover:text-red-700"
                                onClick={() => handleDeleteBlock(block.id)}
                                title="Delete"
                              >
                                <Trash2 className="h-4 w-4" />
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
          </TabsContent>

          {/* Validation Tab */}
          <TabsContent value="validation">
            <Card>
              <CardHeader>
                <CardTitle>Validation Cards</CardTitle>
                <CardDescription>
                  Content conflicts and resolutions for this knowledge card
                </CardDescription>
              </CardHeader>
              <CardContent>
                {validationCards.length === 0 ? (
                  <Alert>
                    <AlertTitle>No validation cards found</AlertTitle>
                    <AlertDescription>
                      All content appears to be validated
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Target</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Sensitivity</TableHead>
                        <TableHead>Assigned</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {validationCards.map(vc => (
                        <TableRow key={vc.id}>
                          <TableCell className="font-medium">{vc.id}</TableCell>
                          <TableCell>
                            <div className="text-sm font-medium">{vc.target_type}: {vc.target_id}</div>
                          </TableCell>
                          <TableCell>
                            <Badge className={getValidationStatusColor(vc.status)}>
                              {vc.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline" className="text-xs">
                              {vc.sensitivity}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {vc.assigned_to ? (
                              <div className="text-sm">
                                {vc.assigned_to} (Tier {vc.assigned_tier})
                                {vc.due_date && (
                                  <div className="text-xs text-muted-foreground">
                                    Due: {formatDate(vc.due_date)}
                                  </div>
                                )}
                              </div>
                            ) : (
                              <span className="text-xs text-muted-foreground">Unassigned</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <Button size="sm" variant="outline" onClick={() => navigate(`/validation/${vc.id}`)}>
                              View Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Discussion Tab */}
          <TabsContent value="discussion">
            <Card>
              <CardHeader>
                <CardTitle>Discussion Threads</CardTitle>
                <CardDescription>
                  Collaborative discussions about this knowledge card
                </CardDescription>
              </CardHeader>
              <CardContent>
                {discussionThreads.length === 0 ? (
                  <Alert>
                    <AlertTitle>No discussion threads found</AlertTitle>
                    <AlertDescription>
                      No discussions have been started for this card
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Title</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Quality</TableHead>
                        <TableHead>Comments</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {discussionThreads.map(thread => (
                        <TableRow key={thread.id}>
                          <TableCell className="font-medium">{thread.title}</TableCell>
                          <TableCell>
                            <Badge className={getThreadStatusColor(thread.status)}>
                              {thread.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {thread.evidence_quality && (
                              <Badge variant="outline" className="text-xs">
                                {thread.evidence_quality} quality
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">
                              {thread.comment_count} comments
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Button size="sm" variant="outline" onClick={() => navigate(`/discussion/${thread.id}`)}>
                              View Thread
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Activity Tab */}
          <TabsContent value="activity">
            <Card>
              <CardHeader>
                <CardTitle>Activity Log</CardTitle>
                <CardDescription>
                  Recent activity for this knowledge card
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Alert>
                  <AlertTitle>Activity Log</AlertTitle>
                  <AlertDescription>
                    Activity logging will be implemented in future phases
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Card Settings</CardTitle>
                <CardDescription>
                  Advanced settings for this knowledge card
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Alert>
                  <AlertTitle>Settings</AlertTitle>
                  <AlertDescription>
                    Advanced card settings will be implemented in future phases
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Export with Loader2 import
import { Loader2 } from 'lucide-react';
export default KnowledgeCardDetail;