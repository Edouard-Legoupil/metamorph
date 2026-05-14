import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
import { Plus, Search, Filter, Check, X, Edit, Trash2, Eye, Clock, Calendar, Tag, FileText } from 'lucide-react';
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

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const CARD_TYPES = [
  { value: 'KC-1', label: 'KC-1: Donor Intelligence' },
  { value: 'KC-2', label: 'KC-2: Field Context' },
  { value: 'KC-3', label: 'KC-3: Outcome Evidence' },
  { value: 'KC-4', label: 'KC-4: Partner Capacity' },
  { value: 'KC-5', label: 'KC-5: Track Record' },
  { value: 'KC-6', label: 'KC-6: Crisis Political Economy' },
];

const CARD_DOMAINS = [
  'geographic', 'crisis', 'demographics', 'programming', 'policy', 'finance', 'hr', 'knowledge_assets'
];

const CARD_STATUSES = [
  'draft', 'under_review', 'approved', 'rejected', 'expired', 'archived'
];

const KnowledgeCards: React.FC = () => {
  const navigate = useNavigate();
  const [cards, setCards] = useState<KnowledgeCard[]>([]);
  const [blocks, setBlocks] = useState<WikiBlock[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [cardTypeFilter, setCardTypeFilter] = useState<string>('all');
  const [domainFilter, setDomainFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [validityFilter, setValidityFilter] = useState<string>('all');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(20);
  const [total, setTotal] = useState<number>(0);
  
  // Form state for creating/editing cards
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [editingCard, setEditingCard] = useState<KnowledgeCard | null>(null);
  const [formData, setFormData] = useState({
    card_type: 'KC-1' as string,
    title: '',
    description: '',
    domain: 'geographic' as string,
    validity_start: '' as string,
    validity_end: '' as string,
    source_website_ids: '' as string,
    source_document_ids: '' as string,
    source_entity_ids: '' as string,
    tags: '' as string,
  });
  
  // Form state for creating blocks
  const [isBlockDialogOpen, setIsBlockDialogOpen] = useState<boolean>(false);
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
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

  // Fetch knowledge cards
  const fetchCards = async () => {
    try {
      setIsLoading(true);
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      // Build query parameters
      const params = new URLSearchParams();
      if (cardTypeFilter !== 'all') params.append('card_type', cardTypeFilter);
      if (domainFilter !== 'all') params.append('domain', domainFilter);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (validityFilter !== 'all') params.append('validity', validityFilter);
      if (searchQuery) params.append('search', searchQuery);
      params.append('page', page.toString());
      params.append('page_size', pageSize.toString());
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards?${params.toString()}`, { headers });
      
      if (response.ok) {
        const data = await response.json();
        setCards(data.data);
        setTotal(data.total);
      } else {
        toast.error('Failed to fetch knowledge cards');
      }
    } catch (error) {
      console.error('Error fetching knowledge cards:', error);
      toast.error('Failed to fetch knowledge cards');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch blocks for a specific card
  const fetchBlocks = async (cardId: string) => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/blocks`, { headers });
      
      if (response.ok) {
        const data = await response.json();
        setBlocks(data);
      } else {
        toast.error('Failed to fetch wiki blocks');
      }
    } catch (error) {
      console.error('Error fetching wiki blocks:', error);
      toast.error('Failed to fetch wiki blocks');
    }
  };

  useEffect(() => {
    fetchCards();
  }, [page, pageSize, cardTypeFilter, domainFilter, statusFilter, validityFilter, searchQuery]);

  // Handle form changes
  const handleFormChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle block form changes
  const handleBlockFormChange = (field: string, value: any) => {
    setBlockFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Create or update knowledge card
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        card_type: formData.card_type,
        title: formData.title,
        description: formData.description || undefined,
        domain: formData.domain,
        validity_start: formData.validity_start || undefined,
        validity_end: formData.validity_end || undefined,
        source_website_ids: formData.source_website_ids ? formData.source_website_ids.split(',').map(s => s.trim()) : [],
        source_document_ids: formData.source_document_ids ? formData.source_document_ids.split(',').map(s => s.trim()) : [],
        source_entity_ids: formData.source_entity_ids ? formData.source_entity_ids.split(',').map(s => s.trim()) : [],
        tags: formData.tags ? formData.tags.split(',').map(s => s.trim()) : [],
      };
      
      let response;
      if (editingCard) {
        response = await fetch(`${API_BASE_URL}/api/v1/cards/${editingCard.id}`, {
          method: 'PATCH',
          headers,
          body: JSON.stringify(payload),
        });
      } else {
        response = await fetch(`${API_BASE_URL}/api/v1/cards`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        });
      }
      
      if (response.ok) {
        toast.success(editingCard ? 'Knowledge card updated successfully' : 'Knowledge card created successfully');
        setIsDialogOpen(false);
        setEditingCard(null);
        setFormData({
          card_type: 'KC-1',
          title: '',
          description: '',
          domain: 'geographic',
          validity_start: '',
          validity_end: '',
          source_website_ids: '',
          source_document_ids: '',
          source_entity_ids: '',
          tags: '',
        });
        fetchCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save knowledge card');
      }
    } catch (error) {
      console.error('Error saving knowledge card:', error);
      toast.error('Failed to save knowledge card');
    }
  };

  // Create wiki block
  const handleBlockSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCardId) return;
    
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
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/${selectedCardId}/blocks`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Wiki block created successfully');
        setIsBlockDialogOpen(false);
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
        if (selectedCardId) {
          fetchBlocks(selectedCardId);
        }
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to create wiki block');
      }
    } catch (error) {
      console.error('Error creating wiki block:', error);
      toast.error('Failed to create wiki block');
    }
  };

  // Delete knowledge card
  const handleDeleteCard = async (cardId: string) => {
    if (!confirm('Are you sure you want to delete this knowledge card?')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Knowledge card deleted successfully');
        fetchCards();
      } else {
        toast.error('Failed to delete knowledge card');
      }
    } catch (error) {
      console.error('Error deleting knowledge card:', error);
      toast.error('Failed to delete knowledge card');
    }
  };

  // Approve knowledge card
  const handleApproveCard = async (cardId: string) => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        validity_period: {},
        approval_notes: 'Approved via UI',
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/approve`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Knowledge card approved successfully');
        fetchCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to approve knowledge card');
      }
    } catch (error) {
      console.error('Error approving knowledge card:', error);
      toast.error('Failed to approve knowledge card');
    }
  };

  // Reject knowledge card
  const handleRejectCard = async (cardId: string) => {
    const reason = prompt('Please enter rejection reason:');
    if (!reason) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        rejection_reason: reason,
        suggested_actions: [],
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/reject`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Knowledge card rejected successfully');
        fetchCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to reject knowledge card');
      }
    } catch (error) {
      console.error('Error rejecting knowledge card:', error);
      toast.error('Failed to reject knowledge card');
    }
  };

  // Open edit dialog
  const openEditDialog = (card: KnowledgeCard) => {
    setEditingCard(card);
    setFormData({
      card_type: card.card_type,
      title: card.title,
      description: card.description || '',
      domain: card.domain,
      validity_start: card.validity_start || '',
      validity_end: card.validity_end || '',
      source_website_ids: card.source_websites.join(', '),
      source_document_ids: card.source_documents.join(', '),
      source_entity_ids: card.source_entities.join(', '),
      tags: card.tags.join(', '),
    });
    setIsDialogOpen(true);
  };

  // Open block creation dialog
  const openBlockDialog = (cardId: string) => {
    setSelectedCardId(cardId);
    setIsBlockDialogOpen(true);
  };

  // View card details
  const viewCardDetails = (cardId: string) => {
    navigate(`/cards/${cardId}`);
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'under_review':
        return 'bg-blue-100 text-blue-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'expired':
        return 'bg-yellow-100 text-yellow-800';
      case 'archived':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get card type label
  const getCardTypeLabel = (cardType: string) => {
    const type = CARD_TYPES.find(t => t.value === cardType);
    return type ? type.label : cardType;
  };

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (isLoading && cards.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p>Loading knowledge cards...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Knowledge Cards</h1>
            <p className="text-muted-foreground">Manage structured knowledge representations</p>
          </div>
          <div className="flex gap-2">
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => {
                  setEditingCard(null);
                  setFormData({
                    card_type: 'KC-1',
                    title: '',
                    description: '',
                    domain: 'geographic',
                    validity_start: '',
                    validity_end: '',
                    source_website_ids: '',
                    source_document_ids: '',
                    source_entity_ids: '',
                    tags: '',
                  });
                }}>
                  <Plus className="mr-2 h-4 w-4" /> Create Knowledge Card
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>{editingCard ? 'Edit Knowledge Card' : 'Create New Knowledge Card'}</DialogTitle>
                  <DialogDescription>
                    {editingCard ? 'Update knowledge card details' : 'Create a new structured knowledge card'}
                  </DialogDescription>
                </DialogHeader>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Card Type */}
                  <div className="space-y-2">
                    <Label htmlFor="card_type">Card Type *</Label>
                    <Select
                      value={formData.card_type}
                      onValueChange={(value) => handleFormChange('card_type', value)}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select card type" />
                      </SelectTrigger>
                      <SelectContent>
                        {CARD_TYPES.map(type => (
                          <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Title */}
                  <div className="space-y-2">
                    <Label htmlFor="title">Title *</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => handleFormChange('title', e.target.value)}
                      placeholder="Card title"
                      required
                    />
                  </div>

                  {/* Description */}
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={formData.description}
                      onChange={(e) => handleFormChange('description', e.target.value)}
                      placeholder="Brief description of the card"
                    />
                  </div>

                  {/* Domain */}
                  <div className="space-y-2">
                    <Label htmlFor="domain">Domain *</Label>
                    <Select
                      value={formData.domain}
                      onValueChange={(value) => handleFormChange('domain', value)}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select domain" />
                      </SelectTrigger>
                      <SelectContent>
                        {CARD_DOMAINS.map(domain => (
                          <SelectItem key={domain} value={domain}>{domain}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Validity Period */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="validity_start">Validity Start</Label>
                      <Input
                        id="validity_start"
                        type="datetime-local"
                        value={formData.validity_start}
                        onChange={(e) => handleFormChange('validity_start', e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="validity_end">Validity End</Label>
                      <Input
                        id="validity_end"
                        type="datetime-local"
                        value={formData.validity_end}
                        onChange={(e) => handleFormChange('validity_end', e.target.value)}
                      />
                    </div>
                  </div>

                  {/* Source IDs */}
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="source_websites">Source Website IDs (comma separated)</Label>
                      <Input
                        id="source_websites"
                        value={formData.source_website_ids}
                        onChange={(e) => handleFormChange('source_website_ids', e.target.value)}
                        placeholder="website_1, website_2"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="source_documents">Source Document IDs (comma separated)</Label>
                      <Input
                        id="source_documents"
                        value={formData.source_document_ids}
                        onChange={(e) => handleFormChange('source_document_ids', e.target.value)}
                        placeholder="doc_1, doc_2"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="source_entities">Source Entity IDs (comma separated)</Label>
                      <Input
                        id="source_entities"
                        value={formData.source_entity_ids}
                        onChange={(e) => handleFormChange('source_entity_ids', e.target.value)}
                        placeholder="entity_1, entity_2"
                      />
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="space-y-2">
                    <Label htmlFor="tags">Tags (comma separated)</Label>
                    <Input
                      id="tags"
                      value={formData.tags}
                      onChange={(e) => handleFormChange('tags', e.target.value)}
                      placeholder="tag1, tag2, tag3"
                    />
                  </div>

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={!formData.title}>
                      {editingCard ? 'Update Knowledge Card' : 'Create Knowledge Card'}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search cards..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8"
                />
              </div>

              {/* Card Type Filter */}
              <Select value={cardTypeFilter} onValueChange={setCardTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Card Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {CARD_TYPES.map(type => (
                    <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Domain Filter */}
              <Select value={domainFilter} onValueChange={setDomainFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Domain" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Domains</SelectItem>
                  {CARD_DOMAINS.map(domain => (
                    <SelectItem key={domain} value={domain}>{domain}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Status Filter */}
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  {CARD_STATUSES.map(status => (
                    <SelectItem key={status} value={status}>{status}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Validity Filter */}
              <Select value={validityFilter} onValueChange={setValidityFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Validity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="valid">Valid</SelectItem>
                  <SelectItem value="expired">Expired</SelectItem>
                  <SelectItem value="expiring_soon">Expiring Soon</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Cards Table */}
        <Card>
          <CardHeader>
            <CardTitle>Knowledge Cards</CardTitle>
            <CardDescription>
              {total} knowledge cards found
            </CardDescription>
          </CardHeader>
          <CardContent>
            {cards.length === 0 ? (
              <Alert>
                <AlertTitle>No knowledge cards found</AlertTitle>
                <AlertDescription>
                  Create your first knowledge card to get started
                </AlertDescription>
              </Alert>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Domain</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Validity</TableHead>
                    <TableHead>Blocks</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {cards.map(card => (
                    <TableRow key={card.id}>
                      <TableCell className="font-medium">{card.id}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs">
                          {card.card_type}
                        </Badge>
                        <div className="text-xs text-muted-foreground">
                          {getCardTypeLabel(card.card_type)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="font-medium">{card.title}</div>
                        <div className="text-xs text-muted-foreground truncate max-w-xs">
                          {card.description}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="text-xs">
                          {card.domain}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(card.status)}>
                          {card.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="text-xs">
                          {card.validity_start ? (
                            <div>{formatDate(card.validity_start)}</div>
                          ) : 'No start'}
                          {card.validity_end ? (
                            <div>{formatDate(card.validity_end)}</div>
                          ) : 'No end'}
                        </div>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline">
                          {card.blocks_count} blocks
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => viewCardDetails(card.id)}
                            title="View details"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => openBlockDialog(card.id)}
                            title="Add block"
                          >
                            <FileText className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => openEditDialog(card)}
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          {card.status === 'draft' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleApproveCard(card.id)}
                              title="Approve"
                            >
                              <Check className="h-4 w-4 text-green-500" />
                            </Button>
                          )}
                          {card.status === 'draft' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleRejectCard(card.id)}
                              title="Reject"
                            >
                              <X className="h-4 w-4 text-red-500" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-red-500 hover:text-red-700"
                            onClick={() => handleDeleteCard(card.id)}
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

        {/* Pagination */}
        {total > pageSize && (
          <div className="flex justify-center gap-2">
            <Button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              variant="outline"
            >
              Previous
            </Button>
            <span className="flex items-center">
              Page {page} of {Math.ceil(total / pageSize)}
            </span>
            <Button
              disabled={page * pageSize >= total}
              onClick={() => setPage(page + 1)}
              variant="outline"
            >
              Next
            </Button>
          </div>
        )}

        {/* Block Creation Dialog */}
        <Dialog open={isBlockDialogOpen} onOpenChange={setIsBlockDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Wiki Block</DialogTitle>
              <DialogDescription>
                Add a new content block to the knowledge card
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
                  Create Wiki Block
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

// Export with Loader2 import
import { Loader2 } from 'lucide-react';
export default KnowledgeCards;