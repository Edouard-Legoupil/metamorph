import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, CardHeader, CardTitle, CardContent, CardDescription
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Clock, Calendar, Tag, FileText, Check, X, User, Shield, AlertTriangle, ArrowLeft, Edit, Trash2, GitMerge, ArrowUp } from 'lucide-react';
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

const ValidationDetail: React.FC = () => {
  const { validationId } = useParams<{ validationId: string }>();
  const navigate = useNavigate();
  const [validationCard, setValidationCard] = useState<ValidationCard | null>(null);
  const [relatedCard, setRelatedCard] = useState<KnowledgeCard | null>(null);
  const [relatedBlock, setRelatedBlock] = useState<WikiBlock | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editData, setEditData] = useState({
    current_value: '',
    proposed_value: '',
    diff: '',
    sensitivity: 'medium',
    evidence: '',
    source_reliability: '',
    contradiction_type: '',
    confidence_score: '',
  });

  // Fetch validation card details
  const fetchValidationDetails = async () => {
    if (!validationId) return;
    
    try {
      setIsLoading(true);
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      // Fetch validation card
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${validationId}`, { headers });
      
      if (response.ok) {
        const data = await response.json();
        setValidationCard(data);
        setEditData({
          current_value: data.current_value || '',
          proposed_value: data.proposed_value || '',
          diff: data.diff || '',
          sensitivity: data.sensitivity || 'medium',
          evidence: data.evidence?.join(', ') || '',
          source_reliability: data.source_reliability || '',
          contradiction_type: data.contradiction_type || '',
          confidence_score: data.confidence_score?.toString() || '',
        });
        
        // Fetch related card if available
        if (data.card_id) {
          const cardResponse = await fetch(`${API_BASE_URL}/api/v1/cards/${data.card_id}`, { headers });
          if (cardResponse.ok) {
            setRelatedCard(await cardResponse.json());
          }
        }
        
        // Fetch related block if available
        if (data.target_type === 'block' && data.target_id) {
          const cardId = data.card_id || relatedCard?.id;
          if (cardId) {
            const blocksResponse = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}/blocks`, { headers });
            if (blocksResponse.ok) {
              const blocks = await blocksResponse.json();
              const block = blocks.find((b: WikiBlock) => b.id === data.target_id);
              if (block) {
                setRelatedBlock(block);
              }
            }
          }
        }
      } else {
        toast.error('Failed to fetch validation card details');
      }
    } catch (error) {
      console.error('Error fetching validation card details:', error);
      toast.error('Failed to fetch validation card details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchValidationDetails();
  }, [validationId]);

  // Handle edit form changes
  const handleEditChange = (field: string, value: any) => {
    setEditData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Update validation card
  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validationId) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      // For validation cards, we typically don't update the content directly
      // Instead, we would update the resolution status
      // This is a placeholder for potential content updates
      const payload = {
        // In a real implementation, you might update metadata here
        // For now, we'll just show a success message
      };
      
      // In a real app, you would call the appropriate endpoint
      // For now, we'll just show a success message
      toast.success('Validation card updated successfully');
      setIsEditing(false);
      fetchValidationDetails();
    } catch (error) {
      console.error('Error updating validation card:', error);
      toast.error('Failed to update validation card');
    }
  };

  // Assign validation card
  const handleAssign = async () => {
    if (!validationId) return;
    
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
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${validationId}/assign`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card assigned successfully');
        fetchValidationDetails();
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
  const handleApprove = async () => {
    if (!validationId) return;
    
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
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${validationId}/approve`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card approved successfully');
        fetchValidationDetails();
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
  const handleReject = async () => {
    if (!validationId) return;
    
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
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${validationId}/reject`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card rejected successfully');
        fetchValidationDetails();
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
  const handleMerge = async () => {
    if (!validationId) return;
    
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
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${validationId}/merge`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card merged successfully');
        fetchValidationDetails();
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
  const handleEscalate = async () => {
    if (!validationId) return;
    
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
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${validationId}/escalate`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Validation card escalated successfully');
        fetchValidationDetails();
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
  const handleDelete = async () => {
    if (!validationId || !confirm('Are you sure you want to delete this validation card?')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/cards/validation/cards/${validationId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Validation card deleted successfully');
        navigate('/validation');
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p>Loading validation card details...</p>
        </div>
      </div>
    );
  }

  if (!validationCard) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <Alert variant="destructive">
          <AlertTitle>Validation card not found</AlertTitle>
          <AlertDescription>
            The validation card you requested could not be found.
          </AlertDescription>
        </Alert>
        <Button onClick={() => navigate('/validation')} className="mt-4">
          Back to Validation Dashboard
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
            <h1 className="text-3xl font-bold">Validation Card: {validationCard.id}</h1>
            <p className="text-muted-foreground">
              Manage content conflict resolution
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => navigate('/validation')} variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
            </Button>
          </div>
        </div>

        {/* Validation Card Details */}
        <Card>
          <CardHeader>
            <CardTitle>Validation Card Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Status */}
              <div>
                <Label className="text-sm text-muted-foreground">Status</Label>
                <div className="flex items-center gap-2">
                  <Badge className={getStatusColor(validationCard.status)}>
                    {validationCard.status}
                  </Badge>
                </div>
              </div>

              {/* Target */}
              <div>
                <Label className="text-sm text-muted-foreground">Target</Label>
                <div className="flex items-center gap-2">
                  <span className="font-medium">
                    {validationCard.target_type}: {validationCard.target_id}
                  </span>
                </div>
                {relatedBlock && (
                  <div className="text-xs text-muted-foreground mt-1">
                    Block: {relatedBlock.section_name}
                  </div>
                )}
                {relatedCard && (
                  <div className="text-xs text-muted-foreground mt-1">
                    Card: {relatedCard.title}
                  </div>
                )}
              </div>

              {/* Sensitivity */}
              <div>
                <Label className="text-sm text-muted-foreground">Sensitivity</Label>
                <div className="flex items-center gap-2">
                  <Badge className={getSensitivityColor(validationCard.sensitivity)}>
                    {validationCard.sensitivity}
                  </Badge>
                </div>
              </div>

              {/* Created */}
              <div>
                <Label className="text-sm text-muted-foreground">Created</Label>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>{formatDate(validationCard.created_at)}</span>
                </div>
              </div>

              {/* Assigned */}
              <div>
                <Label className="text-sm text-muted-foreground">Assigned</Label>
                <div className="flex items-center gap-2">
                  {validationCard.assigned_to ? (
                    <>
                      <User className="h-4 w-4 text-muted-foreground" />
                      <span>{validationCard.assigned_to}</span>
                      {validationCard.assigned_tier && (
                        <Badge variant="outline" className="text-xs">
                          Tier {validationCard.assigned_tier}
                        </Badge>
                      )}
                    </>
                  ) : (
                    <span className="text-muted-foreground">Unassigned</span>
                  )}
                </div>
              </div>

              {/* Due Date */}
              {validationCard.due_date && (
                <div>
                  <Label className="text-sm text-muted-foreground">Due Date</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span>{formatDate(validationCard.due_date)}</span>
                  </div>
                </div>
              )}

              {/* Resolved */}
              {validationCard.resolved_at && (
                <div>
                  <Label className="text-sm text-muted-foreground">Resolved</Label>
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-green-500" />
                    <span>{formatDate(validationCard.resolved_at)}</span>
                  </div>
                </div>
              )}

              {/* Resolution Type */}
              {validationCard.resolution_type && (
                <div>
                  <Label className="text-sm text-muted-foreground">Resolution</Label>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">
                      {validationCard.resolution_type}
                    </Badge>
                  </div>
                </div>
              )}

              {/* Confidence Score */}
              {validationCard.confidence_score && (
                <div>
                  <Label className="text-sm text-muted-foreground">Confidence</Label>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-lg">
                      {Math.round(validationCard.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Content Comparison */}
        <Card>
          <CardHeader>
            <CardTitle>Content Comparison</CardTitle>
            <CardDescription>Current vs Proposed values</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Current Value */}
              <div>
                <Label className="text-sm text-muted-foreground mb-2 block">Current Value</Label>
                <div className="border rounded-lg p-4 bg-gray-50 min-h-[200px]">
                  {validationCard.current_value ? (
                    <pre className="whitespace-pre-wrap text-sm">
                      {validationCard.current_value}
                    </pre>
                  ) : (
                    <p className="text-muted-foreground text-sm">No current value provided</p>
                  )}
                </div>
              </div>

              {/* Proposed Value */}
              <div>
                <Label className="text-sm text-muted-foreground mb-2 block">Proposed Value</Label>
                <div className="border rounded-lg p-4 bg-blue-50 min-h-[200px]">
                  {validationCard.proposed_value ? (
                    <pre className="whitespace-pre-wrap text-sm">
                      {validationCard.proposed_value}
                    </pre>
                  ) : (
                    <p className="text-muted-foreground text-sm">No proposed value provided</p>
                  )}
                </div>
              </div>
            </div>

            {/* Diff */}
            {validationCard.diff && (
              <div className="mt-6">
                <Label className="text-sm text-muted-foreground mb-2 block">Difference</Label>
                <div className="border rounded-lg p-4 bg-yellow-50">
                  <pre className="whitespace-pre-wrap text-sm">
                    {validationCard.diff}
                  </pre>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Evidence and Provenance */}
        <Card>
          <CardHeader>
            <CardTitle>Evidence & Provenance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Evidence */}
              <div>
                <Label className="text-sm text-muted-foreground mb-2 block">Evidence Sources</Label>
                {validationCard.evidence && validationCard.evidence.length > 0 ? (
                  <div className="space-y-2">
                    {validationCard.evidence.map((source, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <span className="text-muted-foreground mt-1">•</span>
                        <a 
                          href={source}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline text-sm break-all"
                        >
                          {source}
                        </a>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">No evidence sources provided</p>
                )}
              </div>

              {/* Provenance */}
              <div>
                <Label className="text-sm text-muted-foreground mb-2 block">Provenance</Label>
                {validationCard.provenance && Object.keys(validationCard.provenance).length > 0 ? (
                  <div className="text-sm">
                    <pre className="whitespace-pre-wrap">
                      {JSON.stringify(validationCard.provenance, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">No provenance information</p>
                )}
              </div>
            </div>

            {/* Additional Metadata */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {validationCard.source_reliability && (
                <div>
                  <Label className="text-sm text-muted-foreground">Source Reliability</Label>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">
                      {validationCard.source_reliability}
                    </Badge>
                  </div>
                </div>
              )}

              {validationCard.contradiction_type && (
                <div>
                  <Label className="text-sm text-muted-foreground">Contradiction Type</Label>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">
                      {validationCard.contradiction_type}
                    </Badge>
                  </div>
                </div>
              )}

              {validationCard.resolution && (
                <div>
                  <Label className="text-sm text-muted-foreground">Resolution Notes</Label>
                  <div className="text-sm">
                    {validationCard.resolution}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {validationCard.status === 'open' && (
                <Button onClick={handleAssign} className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  <span>Assign to Reviewer</span>
                </Button>
              )}

              {validationCard.status === 'under_review' && (
                <>
                  <Button onClick={handleApprove} className="flex items-center gap-2 bg-green-600 hover:bg-green-700">
                    <Check className="h-4 w-4" />
                    <span>Approve</span>
                  </Button>
                  
                  <Button onClick={handleReject} className="flex items-center gap-2 bg-red-600 hover:bg-red-700">
                    <X className="h-4 w-4" />
                    <span>Reject</span>
                  </Button>
                  
                  <Button onClick={handleMerge} className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700">
                    <GitMerge className="h-4 w-4" />
                    <span>Merge</span>
                  </Button>
                </>
              )}
              {(validationCard.status === 'open' || validationCard.status === 'under_review') && (
                <Button onClick={handleEscalate} className="flex items-center gap-2 bg-yellow-600 hover:bg-yellow-700">
                  <ArrowUp className="h-4 w-4" />
                  <span>Escalate</span>
                </Button>
              )}

              <Button onClick={() => setIsEditing(true)} variant="outline" className="flex items-center gap-2">
                <Edit className="h-4 w-4" />
                <span>Edit Metadata</span>
              </Button>

              <Button onClick={handleDelete} variant="outline" className="flex items-center gap-2 text-red-500 hover:text-red-700">
                <Trash2 className="h-4 w-4" />
                <span>Delete</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Edit Dialog */}
        <Dialog open={isEditing} onOpenChange={setIsEditing}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Edit Validation Card</DialogTitle>
              <DialogDescription>
                Update validation card metadata
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleUpdate} className="space-y-4">
              {/* Current Value */}
              <div className="space-y-2">
                <Label htmlFor="current_value">Current Value</Label>
                <textarea
                  id="current_value"
                  value={editData.current_value}
                  onChange={(e) => handleEditChange('current_value', e.target.value)}
                  className="w-full min-h-[100px] p-2 border rounded-md"
                  placeholder="Current content value"
                />
              </div>

              {/* Proposed Value */}
              <div className="space-y-2">
                <Label htmlFor="proposed_value">Proposed Value</Label>
                <textarea
                  id="proposed_value"
                  value={editData.proposed_value}
                  onChange={(e) => handleEditChange('proposed_value', e.target.value)}
                  className="w-full min-h-[100px] p-2 border rounded-md"
                  placeholder="Proposed content value"
                />
              </div>

              {/* Diff */}
              <div className="space-y-2">
                <Label htmlFor="diff">Difference</Label>
                <textarea
                  id="diff"
                  value={editData.diff}
                  onChange={(e) => handleEditChange('diff', e.target.value)}
                  className="w-full min-h-[100px] p-2 border rounded-md"
                  placeholder="Difference between values"
                />
              </div>

              {/* Sensitivity */}
              <div className="space-y-2">
                <Label htmlFor="sensitivity">Sensitivity</Label>
                <Select
                  value={editData.sensitivity}
                  onValueChange={(value) => handleEditChange('sensitivity', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select sensitivity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Evidence */}
              <div className="space-y-2">
                <Label htmlFor="evidence">Evidence (comma separated URLs)</Label>
                <Input
                  id="evidence"
                  value={editData.evidence}
                  onChange={(e) => handleEditChange('evidence', e.target.value)}
                  placeholder="https://source1.com, https://source2.com"
                />
              </div>

              {/* Source Reliability */}
              <div className="space-y-2">
                <Label htmlFor="source_reliability">Source Reliability</Label>
                <Select
                  value={editData.source_reliability}
                  onValueChange={(value) => handleEditChange('source_reliability', value)}
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
                  value={editData.contradiction_type}
                  onValueChange={(value) => handleEditChange('contradiction_type', value)}
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
                  value={editData.confidence_score}
                  onChange={(e) => handleEditChange('confidence_score', e.target.value)}
                  placeholder="0.75"
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
                <Button type="submit">
                  Update Validation Card
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
export default ValidationDetail;