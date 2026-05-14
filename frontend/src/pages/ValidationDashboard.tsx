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
import { Search, Filter, Check, X, Edit, Trash2, Eye, Clock, Calendar, Tag, FileText, Plus, User, Shield, AlertTriangle, GitMerge, ArrowUp } from 'lucide-react';
import { toast } from 'sonner';

// Types
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

interface KnowledgeCard {
  id: string;
  card_type: string;
  title: string;
  domain: string;
  status: string;
}

interface WikiBlock {
  id: string;
  card_id: string;
  section_name: string;
  content: string;
  verification_state: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const VALIDATION_STATUSES = [
  'open', 'under_review', 'approved', 'rejected', 'merged', 'escalated', 'no_consensus'
];

const SENSITIVITY_LEVELS = [
  'low', 'medium', 'high'
];

const TIER_LEVELS = [
  'tier_1', 'tier_2', 'tier_3'
];

const TARGET_TYPES = [
  'block', 'entity', 'card', 'triplet'
];

const ValidationDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [validationCards, setValidationCards] = useState<ValidationCard[]>([]);
  const [knowledgeCards, setKnowledgeCards] = useState<KnowledgeCard[]>([]);
  const [wikiBlocks, setWikiBlocks] = useState<WikiBlock[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sensitivityFilter, setSensitivityFilter] = useState<string>('all');
  const [tierFilter, setTierFilter] = useState<string>('all');
  const [targetTypeFilter, setTargetTypeFilter] = useState<string>('all');
  const [assignedToFilter, setAssignedToFilter] = useState<string>('all');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(20);
  const [total, setTotal] = useState<number>(0);
  
  // Form state for creating validation cards
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    target_type: 'block' as string,
    target_id: '' as string,
    card_id: '' as string,
    current_value: '' as string,
    proposed_value: '' as string,
    diff: '' as string,
    sensitivity: 'medium' as string,
    assigned_tier: '' as string,
    confidence_score: '' as string,
    evidence: '' as string,
    source_reliability: '' as string,
    contradiction_type: '' as string,
  });

  // Fetch validation cards
  const fetchValidationCards = async () => {
    try {
      setIsLoading(true);
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      // Build query parameters
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (sensitivityFilter !== 'all') params.append('sensitivity', sensitivityFilter);
      if (tierFilter !== 'all') params.append('assigned_tier', tierFilter);
      if (targetTypeFilter !== 'all') params.append('target_type', targetTypeFilter);
      if (assignedToFilter !== 'all') params.append('assigned_to', assignedToFilter);
      if (searchQuery) params.append('search', searchQuery);
      params.append('page', page.toString());
      params.append('page_size', pageSize.toString());
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards?${params.toString()}`, { headers });
      
      if (response.ok) {
        const data = await response.json();
        setValidationCards(data);
        setTotal(data.length);
      } else {
        toast.error('Failed to fetch validation cards');
      }
    } catch (error) {
      console.error('Error fetching validation cards:', error);
      toast.error('Failed to fetch validation cards');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch knowledge cards for reference
  const fetchKnowledgeCards = async () => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards?page_size=100`, { headers });
      
      if (response.ok) {
        const data = await response.json();
        setKnowledgeCards(data.data);
      }
    } catch (error) {
      console.error('Error fetching knowledge cards:', error);
    }
  };

  // Fetch wiki blocks for reference
  const fetchWikiBlocks = async () => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      // Fetch blocks from all cards (limit to first card for demo)
      const cardResponse = await fetch(`${API_BASE_URL}/api/v1/cards?page_size=1`, { headers });
      if (cardResponse.ok) {
        const cardData = await cardResponse.json();
        if (cardData.data.length > 0) {
          const blocksResponse = await fetch(`${API_BASE_URL}/api/v1/cards/${cardData.data[0].id}/blocks`, { headers });
          if (blocksResponse.ok) {
            setWikiBlocks(await blocksResponse.json());
          }
        }
      }
    } catch (error) {
      console.error('Error fetching wiki blocks:', error);
    }
  };

  useEffect(() => {
    fetchValidationCards();
    fetchKnowledgeCards();
    fetchWikiBlocks();
  }, [page, pageSize, statusFilter, sensitivityFilter, tierFilter, targetTypeFilter, assignedToFilter, searchQuery]);

  // Handle form changes
  const handleFormChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Create validation card
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        target_type: formData.target_type,
        target_id: formData.target_id,
        card_id: formData.card_id || undefined,
        current_value: formData.current_value || undefined,
        proposed_value: formData.proposed_value || undefined,
        diff: formData.diff || undefined,
        sensitivity: formData.sensitivity,
        assigned_tier: formData.assigned_tier || undefined,
        confidence_score: formData.confidence_score ? parseFloat(formData.confidence_score) : undefined,
        evidence: formData.evidence ? formData.evidence.split(',').map(s => s.trim()) : [],
        provenance: {},
        source_reliability: formData.source_reliability || undefined,
        contradiction_type: formData.contradiction_type || undefined,
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card created successfully');
        setIsDialogOpen(false);
        setFormData({
          target_type: 'block',
          target_id: '',
          card_id: '',
          current_value: '',
          proposed_value: '',
          diff: '',
          sensitivity: 'medium',
          assigned_tier: '',
          confidence_score: '',
          evidence: '',
          source_reliability: '',
          contradiction_type: '',
        });
        fetchValidationCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to create validation card');
      }
    } catch (error) {
      console.error('Error creating validation card:', error);
      toast.error('Failed to create validation card');
    }
  };

  // Assign validation card
  const handleAssign = async (cardId: string) => {
    const userId = prompt('Enter user ID to assign to:');
    if (!userId) return;
    
    const tier = prompt('Enter review tier (tier_1, tier_2, tier_3):');
    if (!tier || !['tier_1', 'tier_2', 'tier_3'].includes(tier)) {
      toast.error('Invalid tier');
      return;
    }
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        assigned_to: userId,
        assigned_tier: tier,
        priority: 'normal',
        due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${cardId}/assign`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card assigned successfully');
        fetchValidationCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to assign validation card');
      }
    } catch (error) {
      console.error('Error assigning validation card:', error);
      toast.error('Failed to assign validation card');
    }
  };

  // Approve validation card
  const handleApprove = async (cardId: string) => {
    const resolution = prompt('Enter resolution notes:');
    if (!resolution) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        resolution: resolution,
        confidence_score: 0.95,
        update_target: true,
        notification_message: 'Validation approved',
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${cardId}/approve`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card approved successfully');
        fetchValidationCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to approve validation card');
      }
    } catch (error) {
      console.error('Error approving validation card:', error);
      toast.error('Failed to approve validation card');
    }
  };

  // Reject validation card
  const handleReject = async (cardId: string) => {
    const resolution = prompt('Enter rejection reason:');
    if (!resolution) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        resolution: resolution,
        confidence_score: 0.3,
        update_target: false,
        notification_message: 'Validation rejected',
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${cardId}/reject`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card rejected successfully');
        fetchValidationCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to reject validation card');
      }
    } catch (error) {
      console.error('Error rejecting validation card:', error);
      toast.error('Failed to reject validation card');
    }
  };

  // Merge validation card
  const handleMerge = async (cardId: string) => {
    const resolution = prompt('Enter merge resolution:');
    if (!resolution) return;
    
    const mergedValue = prompt('Enter merged value:');
    if (!mergedValue) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        resolution: resolution,
        merged_value: mergedValue,
        resolution_notes: 'Conflict resolved by merging values',
        confidence_score: 0.85,
        update_target: true,
        new_evidence: [],
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${cardId}/merge`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card merged successfully');
        fetchValidationCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to merge validation card');
      }
    } catch (error) {
      console.error('Error merging validation card:', error);
      toast.error('Failed to merge validation card');
    }
  };

  // Escalate validation card
  const handleEscalate = async (cardId: string) => {
    const escalationReason = prompt('Enter escalation reason:');
    if (!escalationReason) return;
    
    const escalateTo = prompt('Enter tier to escalate to (tier_1, tier_2, tier_3):');
    if (!escalateTo || !['tier_1', 'tier_2', 'tier_3'].includes(escalateTo)) {
      toast.error('Invalid tier');
      return;
    }
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        escalation_reason: escalationReason,
        escalate_to: escalateTo,
        escalation_notes: 'Escalated for higher-level review',
        urgency: 'normal',
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${cardId}/escalate`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card escalated successfully');
        fetchValidationCards();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to escalate validation card');
      }
    } catch (error) {
      console.error('Error escalating validation card:', error);
      toast.error('Failed to escalate validation card');
    }
  };

  // Delete validation card
  const handleDelete = async (cardId: string) => {
    if (!confirm('Are you sure you want to delete this validation card?')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${cardId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Validation card deleted successfully');
        fetchValidationCards();
      } else {
        toast.error('Failed to delete validation card');
      }
    } catch (error) {
      console.error('Error deleting validation card:', error);
      toast.error('Failed to delete validation card');
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
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

  // Get sensitivity color
  const getSensitivityColor = (sensitivity: string) => {
    switch (sensitivity) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  // Get target display name
  const getTargetDisplay = (type: string, id: string) => {
    if (type === 'block') {
      const block = wikiBlocks.find(b => b.id === id);
      return block ? `${block.section_name} (Block)` : `${id} (Block)`;
    } else if (type === 'card') {
      const card = knowledgeCards.find(c => c.id === id);
      return card ? `${card.title} (Card)` : `${id} (Card)`;
    } else {
      return `${id} (${type})`;
    }
  };

  if (isLoading && validationCards.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p>Loading validation cards...</p>
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
            <h1 className="text-3xl font-bold">Validation Dashboard</h1>
            <p className="text-muted-foreground">Manage content conflicts and resolutions</p>
          </div>
          <div className="flex gap-2">
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => {
                  setFormData({
                    target_type: 'block',
                    target_id: '',
                    card_id: '',
                    current_value: '',
                    proposed_value: '',
                    diff: '',
                    sensitivity: 'medium',
                    assigned_tier: '',
                    confidence_score: '',
                    evidence: '',
                    source_reliability: '',
                    contradiction_type: '',
                  });
                }}>
                  <Plus className="mr-2 h-4 w-4" /> Create Validation Card
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Create Validation Card</DialogTitle>
                  <DialogDescription>
                    Document a content conflict for review and resolution
                  </DialogDescription>
                </DialogHeader>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Target Type */}
                  <div className="space-y-2">
                    <Label htmlFor="target_type">Target Type *</Label>
                    <Select
                      value={formData.target_type}
                      onValueChange={(value) => handleFormChange('target_type', value)}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select target type" />
                      </SelectTrigger>
                      <SelectContent>
                        {TARGET_TYPES.map(type => (
                          <SelectItem key={type} value={type}>{type}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Target ID */}
                  <div className="space-y-2">
                    <Label htmlFor="target_id">Target ID *</Label>
                    {formData.target_type === 'block' && wikiBlocks.length > 0 ? (
                      <Select
                        value={formData.target_id}
                        onValueChange={(value) => handleFormChange('target_id', value)}
                        required
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select block" />
                        </SelectTrigger>
                        <SelectContent>
                          {wikiBlocks.map(block => (
                            <SelectItem key={block.id} value={block.id}>
                              {block.section_name} ({block.id})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : formData.target_type === 'card' && knowledgeCards.length > 0 ? (
                      <Select
                        value={formData.target_id}
                        onValueChange={(value) => handleFormChange('target_id', value)}
                        required
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select card" />
                        </SelectTrigger>
                        <SelectContent>
                          {knowledgeCards.map(card => (
                            <SelectItem key={card.id} value={card.id}>
                              {card.title} ({card.id})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      <Input
                        id="target_id"
                        value={formData.target_id}
                        onChange={(e) => handleFormChange('target_id', e.target.value)}
                        placeholder="Enter target ID"
                        required
                      />
                    )}
                  </div>

                  {/* Card ID (for blocks) */}
                  {formData.target_type === 'block' && (
                    <div className="space-y-2">
                      <Label htmlFor="card_id">Card ID *</Label>
                      <Select
                        value={formData.card_id}
                        onValueChange={(value) => handleFormChange('card_id', value)}
                        required
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select card" />
                        </SelectTrigger>
                        <SelectContent>
                          {knowledgeCards.map(card => (
                            <SelectItem key={card.id} value={card.id}>
                              {card.title} ({card.id})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  {/* Current Value */}
                  <div className="space-y-2">
                    <Label htmlFor="current_value">Current Value</Label>
                    <textarea
                      id="current_value"
                      value={formData.current_value}
                      onChange={(e) => handleFormChange('current_value', e.target.value)}
                      className="w-full min-h-[100px] p-2 border rounded-md"
                      placeholder="Current content value"
                    />
                  </div>

                  {/* Proposed Value */}
                  <div className="space-y-2">
                    <Label htmlFor="proposed_value">Proposed Value</Label>
                    <textarea
                      id="proposed_value"
                      value={formData.proposed_value}
                      onChange={(e) => handleFormChange('proposed_value', e.target.value)}
                      className="w-full min-h-[100px] p-2 border rounded-md"
                      placeholder="Proposed content value"
                    />
                  </div>

                  {/* Diff */}
                  <div className="space-y-2">
                    <Label htmlFor="diff">Diff</Label>
                    <textarea
                      id="diff"
                      value={formData.diff}
                      onChange={(e) => handleFormChange('diff', e.target.value)}
                      className="w-full min-h-[100px] p-2 border rounded-md"
                      placeholder="Difference between values"
                    />
                  </div>

                  {/* Sensitivity */}
                  <div className="space-y-2">
                    <Label htmlFor="sensitivity">Sensitivity *</Label>
                    <Select
                      value={formData.sensitivity}
                      onValueChange={(value) => handleFormChange('sensitivity', value)}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select sensitivity" />
                      </SelectTrigger>
                      <SelectContent>
                        {SENSITIVITY_LEVELS.map(level => (
                          <SelectItem key={level} value={level}>{level}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Evidence */}
                  <div className="space-y-2">
                    <Label htmlFor="evidence">Evidence (comma separated URLs)</Label>
                    <Input
                      id="evidence"
                      value={formData.evidence}
                      onChange={(e) => handleFormChange('evidence', e.target.value)}
                      placeholder="https://source1.com, https://source2.com"
                    />
                  </div>

                  {/* Source Reliability */}
                  <div className="space-y-2">
                    <Label htmlFor="source_reliability">Source Reliability</Label>
                    <Select
                      value={formData.source_reliability}
                      onValueChange={(value) => handleFormChange('source_reliability', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select reliability" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="trusted">Trusted</SelectItem>
                        <SelectItem value="reliable">Reliable</SelectItem>
                        <SelectItem value="unverified">Unverified</SelectItem>
                        <SelectItem value="questionable">Questionable</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Contradiction Type */}
                  <div className="space-y-2">
                    <Label htmlFor="contradiction_type">Contradiction Type</Label>
                    <Select
                      value={formData.contradiction_type}
                      onValueChange={(value) => handleFormChange('contradiction_type', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select contradiction type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="factual">Factual</SelectItem>
                        <SelectItem value="temporal">Temporal</SelectItem>
                        <SelectItem value="interpretive">Interpretive</SelectItem>
                        <SelectItem value="methodological">Methodological</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Confidence Score */}
                  <div className="space-y-2">
                    <Label htmlFor="confidence_score">Confidence Score (0-1)</Label>
                    <Input
                      id="confidence_score"
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={formData.confidence_score}
                      onChange={(e) => handleFormChange('confidence_score', e.target.value)}
                      placeholder="0.75"
                    />
                  </div>

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={!formData.target_type || !formData.target_id}>
                      Create Validation Card
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
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search validation cards..."
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
                  {VALIDATION_STATUSES.map(status => (
                    <SelectItem key={status} value={status}>{status}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Sensitivity Filter */}
              <Select value={sensitivityFilter} onValueChange={setSensitivityFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Sensitivity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  {SENSITIVITY_LEVELS.map(level => (
                    <SelectItem key={level} value={level}>{level}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Tier Filter */}
              <Select value={tierFilter} onValueChange={setTierFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Tier" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Tiers</SelectItem>
                  {TIER_LEVELS.map(tier => (
                    <SelectItem key={tier} value={tier}>{tier}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Target Type Filter */}
              <Select value={targetTypeFilter} onValueChange={setTargetTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Target Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {TARGET_TYPES.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Assigned To Filter */}
              <Select value={assignedToFilter} onValueChange={setAssignedToFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Assigned To" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Users</SelectItem>
                  <SelectItem value="unassigned">Unassigned</SelectItem>
                  {/* In a real app, you would fetch actual users */}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Validation Cards Table */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Cards</CardTitle>
            <CardDescription>
              {total} validation cards found
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
                    <TableHead>Confidence</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {validationCards.map(card => (
                    <TableRow key={card.id}>
                      <TableCell className="font-medium">{card.id}</TableCell>
                      <TableCell>
                        <div className="text-sm font-medium">
                          {getTargetDisplay(card.target_type, card.target_id)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {card.target_type}: {card.target_id}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(card.status)}>
                          {card.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getSensitivityColor(card.sensitivity)}>
                          {card.sensitivity}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {card.assigned_to ? (
                          <div className="text-sm">
                            {card.assigned_to}
                            {card.assigned_tier && (
                              <div className="text-xs text-muted-foreground">
                                Tier {card.assigned_tier}
                              </div>
                            )}
                            {card.due_date && (
                              <div className="text-xs text-muted-foreground">
                                Due: {formatDate(card.due_date)}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground">Unassigned</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {card.confidence_score ? (
                          <div className="text-sm font-medium">
                            {Math.round(card.confidence_score * 100)}%
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground">N/A</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => navigate(`/validation/${card.id}`)}
                            title="View details"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          {card.status === 'open' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleAssign(card.id)}
                              title="Assign"
                            >
                              <User className="h-4 w-4 text-blue-500" />
                            </Button>
                          )}
                          {card.status === 'under_review' && (
                            <>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleApprove(card.id)}
                                title="Approve"
                              >
                                <Check className="h-4 w-4 text-green-500" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleReject(card.id)}
                                title="Reject"
                              >
                                <X className="h-4 w-4 text-red-500" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleMerge(card.id)}
                                title="Merge"
                              >
                                <GitMerge className="h-4 w-4 text-purple-500" />
                              </Button>
                            </>
                          )}
                          {(card.status === 'open' || card.status === 'under_review') && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleEscalate(card.id)}
                              title="Escalate"
                            >
                              <ArrowUp className="h-4 w-4 text-yellow-500" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-red-500 hover:text-red-700"
                            onClick={() => handleDelete(card.id)}
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
      </div>
    </div>
  );
};

// Export with Loader2 import
import { Loader2 } from 'lucide-react';
export default ValidationDashboard;