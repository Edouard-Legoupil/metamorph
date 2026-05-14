import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, Trash2, Edit2, Tag, Layers, Loader2, Palette, Type, Hash } from 'lucide-react';
import { toast } from 'sonner';

// Types
interface Topic {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  category: 'general' | 'business' | 'technology' | 'health' | 'science' | 'education' | 'finance' | 'legal' | 'policy' | 'environment' | 'social' | 'custom';
  parent_id: number | null;
  color: string | null;
  icon: string | null;
  order_index: number;
  is_active: boolean;
  is_system: boolean;
  website_count: number;
  file_count: number;
  created_at: string;
  updated_at: string;
}

interface WebsiteTopic {
  id: number;
  website_id: number;
  topic_id: number;
  created_at: string;
}

interface Website {
  id: number;
  url: string;
  domain: string;
  title: string | null;
  description: string | null;
  status: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const categoryColors: Record<string, string> = {
  general: 'bg-gray-100 text-gray-800',
  business: 'bg-blue-100 text-blue-800',
  technology: 'bg-purple-100 text-purple-800',
  health: 'bg-red-100 text-red-800',
  science: 'bg-green-100 text-green-800',
  education: 'bg-yellow-100 text-yellow-800',
  finance: 'bg-emerald-100 text-emerald-800',
  legal: 'bg-amber-100 text-amber-800',
  policy: 'bg-cyan-100 text-cyan-800',
  environment: 'bg-teal-100 text-teal-800',
  social: 'bg-pink-100 text-pink-800',
  custom: 'bg-indigo-100 text-indigo-800',
};

const categoryIcons: Record<string, string> = {
  general: '📋',
  business: '💼',
  technology: '💻',
  health: '⚕️',
  science: '🔬',
  education: '🎓',
  finance: '💰',
  legal: '⚖️',
  policy: '📜',
  environment: '🌍',
  social: '👥',
  custom: '✨',
};

const categoryLabels: Record<string, string> = {
  general: 'General',
  business: 'Business',
  technology: 'Technology',
  health: 'Health',
  science: 'Science',
  education: 'Education',
  finance: 'Finance',
  legal: 'Legal',
  policy: 'Policy',
  environment: 'Environment',
  social: 'Social',
  custom: 'Custom',
};

// Predefined color palette
const colorPalette = [
  '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
  '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
  '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
  '#ec4899', '#f43f5e', '#ef4444',
];

const TopicManagement: React.FC = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [websiteTopics, setWebsiteTopics] = useState<WebsiteTopic[]>([]);
  const [websites, setWebsites] = useState<Website[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [activeTab, setActiveTab] = useState<string>('topics');

  // Form state for creating/editing topic
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    category: 'general' as Topic['category'],
    parent_id: null as number | null,
    color: '#3b82f6',
    icon: '',
    order_index: 0,
    is_active: true,
    is_system: false,
  });

  // Form state for website-topic association
  const [associationFormData, setAssociationFormData] = useState({
    website_id: null as number | null,
    topic_id: null as number | null,
  });

  const [isTopicDialogOpen, setIsTopicDialogOpen] = useState<boolean>(false);
  const [isAssociationDialogOpen, setIsAssociationDialogOpen] = useState<boolean>(false);
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);

  // Fetch all data
  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const [topicsRes, websiteTopicsRes, websitesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/topics`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/website-topics`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/websites`, { headers }),
      ]);
      
      if (topicsRes.ok) {
        setTopics(await topicsRes.json());
      }
      if (websiteTopicsRes.ok) {
        setWebsiteTopics(await websiteTopicsRes.json());
      }
      if (websitesRes.ok) {
        setWebsites(await websitesRes.json());
      }
      
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to fetch data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle form changes
  const handleFormChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleAssociationFormChange = (field: string, value: any) => {
    setAssociationFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Create or update topic
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        name: formData.name,
        slug: formData.slug || formData.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''),
        description: formData.description || null,
        category: formData.category,
        parent_id: formData.parent_id,
        color: formData.color,
        icon: formData.icon || null,
        order_index: formData.order_index,
        is_active: formData.is_active,
        is_system: formData.is_system,
      };
      
      let response;
      if (editingTopic) {
        response = await fetch(`${API_BASE_URL}/api/v1/topics/${editingTopic.id}`, {
          method: 'PUT',
          headers,
          body: JSON.stringify(payload),
        });
      } else {
        response = await fetch(`${API_BASE_URL}/api/v1/topics`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        });
      }
      
      if (response.ok) {
        toast.success(editingTopic ? 'Topic updated successfully' : 'Topic created successfully');
        setIsTopicDialogOpen(false);
        resetForm();
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save topic');
      }
    } catch (error) {
      console.error('Error saving topic:', error);
      toast.error('Failed to save topic');
    }
  };

  // Create website-topic association
  const handleCreateAssociation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      if (!associationFormData.website_id || !associationFormData.topic_id) return;
      
      const payload = {
        website_id: associationFormData.website_id,
        topic_id: associationFormData.topic_id,
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/website-topics`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Association created successfully');
        setIsAssociationDialogOpen(false);
        setAssociationFormData({ website_id: null, topic_id: null });
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to create association');
      }
    } catch (error) {
      console.error('Error creating association:', error);
      toast.error('Failed to create association');
    }
  };

  // Delete topic
  const handleDeleteTopic = async (topicId: number) => {
    if (!confirm('Are you sure you want to delete this topic? All associations will be removed.')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/topics/${topicId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Topic deleted successfully');
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to delete topic');
      }
    } catch (error) {
      console.error('Error deleting topic:', error);
      toast.error('Failed to delete topic');
    }
  };

  // Remove website-topic association
  const handleRemoveAssociation = async (associationId: number) => {
    if (!confirm('Are you sure you want to remove this association?')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/website-topics/${associationId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Association removed successfully');
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to remove association');
      }
    } catch (error) {
      console.error('Error removing association:', error);
      toast.error('Failed to remove association');
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      slug: '',
      description: '',
      category: 'general',
      parent_id: null,
      color: '#3b82f6',
      icon: '',
      order_index: 0,
      is_active: true,
      is_system: false,
    });
    setEditingTopic(null);
  };

  // Open edit dialog
  const openEditDialog = (topic: Topic) => {
    setEditingTopic(topic);
    setFormData({
      name: topic.name,
      slug: topic.slug,
      description: topic.description || '',
      category: topic.category,
      parent_id: topic.parent_id,
      color: topic.color || '#3b82f6',
      icon: topic.icon || '',
      order_index: topic.order_index,
      is_active: topic.is_active,
      is_system: topic.is_system,
    });
    setIsTopicDialogOpen(true);
  };

  // Open create dialog
  const openCreateDialog = () => {
    setEditingTopic(null);
    resetForm();
    setIsTopicDialogOpen(true);
  };

  // Open association dialog
  const openAssociationDialog = (topic: Topic) => {
    setSelectedTopic(topic);
    setAssociationFormData({
      website_id: null,
      topic_id: topic.id,
    });
    setIsAssociationDialogOpen(true);
  };

  // Get root topics (no parent)
  const getRootTopics = () => {
    return topics.filter(t => t.parent_id === null);
  };

  // Get child topics for a parent
  const getChildTopics = (parentId: number) => {
    return topics.filter(t => t.parent_id === parentId);
  };

  // Get topics for a website
  const getWebsiteTopics = (websiteId: number) => {
    const associations = websiteTopics.filter(a => a.website_id === websiteId);
    return associations.map(a => topics.find(t => t.id === a.topic_id)).filter(Boolean) as Topic[];
  };

  // Get websites for a topic
  const getTopicWebsites = (topicId: number) => {
    const associations = websiteTopics.filter(a => a.topic_id === topicId);
    return associations.map(a => websites.find(w => w.id === a.website_id)).filter(Boolean) as Website[];
  };

  // Get available websites to associate with topic
  const getAvailableWebsites = (topicId: number) => {
    const associatedWebsiteIds = websiteTopics
      .filter(a => a.topic_id === topicId)
      .map(a => a.website_id);
    return websites.filter(w => !associatedWebsiteIds.includes(w.id));
  };

  // Build topic hierarchy
  const buildTopicTree = (topics: Topic[], parentId: number | null = null, level = 0) => {
    const children = topics.filter(t => t.parent_id === parentId);
    return children.map(topic => ({
      topic,
      level,
      children: buildTopicTree(topics, topic.id, level + 1),
    }));
  };

  const topicTree = buildTopicTree(topics);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-3">Loading topics...</span>
      </div>
    );
  }

  // Render topic row with indentation
  const renderTopicRow = (node: any, index: number) => {
    const { topic, level, children } = node;
    const websiteCount = getTopicWebsites(topic.id).length;
    const fileCount = topic.file_count;
    
    return (
      <React.Fragment key={topic.id}>
        <TableRow>
          <TableCell style={{ paddingLeft: `${level * 2}rem` }}>
            <div className="flex items-center gap-2">
              {categoryIcons[topic.category] || '📌'}
              <div>
                <div className="font-medium">{topic.name}</div>
                {topic.slug && (
                  <div className="text-sm text-muted-foreground">{topic.slug}</div>
                )}
              </div>
            </div>
          </TableCell>
          <TableCell>
            <Badge className={categoryColors[topic.category]}>
              {categoryLabels[topic.category]}
            </Badge>
          </TableCell>
          <TableCell>
            {topic.description ? (
              <span className="line-clamp-1">{topic.description}</span>
            ) : (
              <span className="text-muted-foreground">No description</span>
            )}
          </TableCell>
          <TableCell>
            <div className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: topic.color || '#3b82f6' }}
              />
              <span className="text-sm font-mono">{topic.color || '#3b82f6'}</span>
            </div>
          </TableCell>
          <TableCell>
            <div className="text-center">
              <Badge variant={topic.is_active ? 'default' : 'secondary'}>
                {topic.is_active ? 'Active' : 'Inactive'}
              </Badge>
              {topic.is_system && (
                <Badge variant="outline" className="ml-1">
                  System
                </Badge>
              )}
            </div>
          </TableCell>
          <TableCell className="text-center">{websiteCount}</TableCell>
          <TableCell className="text-center">{fileCount}</TableCell>
          <TableCell className="text-right">
            <div className="flex items-center justify-end gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => openAssociationDialog(topic)}
                title="Associate with website"
              >
                <Tag className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => openEditDialog(topic)}
                title="Edit"
              >
                <Edit2 className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDeleteTopic(topic.id)}
                title="Delete"
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </TableCell>
        </TableRow>
        {children.map(renderTopicRow)}
      </React.Fragment>
    );
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Topic Management</h1>
          <p className="text-muted-foreground">
            Organize and categorize content using topics for better discovery and filtering.
          </p>
        </div>

        <Tabs defaultValue="topics" value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="topics">Topics</TabsTrigger>
            <TabsTrigger value="associations">Website Associations</TabsTrigger>
          </TabsList>

          {/* Topics Tab */}
          <TabsContent value="topics">
            <Card>
              <CardHeader>
                <CardTitle>Topics</CardTitle>
                <CardDescription>
                  Create and manage content topics with hierarchical organization.
                </CardDescription>
                <div className="flex justify-end">
                  <Dialog open={isTopicDialogOpen} onOpenChange={setIsTopicDialogOpen}>
                    <DialogTrigger asChild>
                      <Button onClick={openCreateDialog}>
                        <Plus className="mr-2 h-4 w-4" />
                        Create Topic
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[600px]">
                      <DialogHeader>
                        <DialogTitle>
                          {editingTopic ? 'Edit Topic' : 'Create New Topic'}
                        </DialogTitle>
                        <DialogDescription>
                          {editingTopic 
                            ? `Editing topic: ${editingTopic.name}`
                            : 'Create a new topic for categorizing content'}
                        </DialogDescription>
                      </DialogHeader>
                      
                      <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="name">Topic Name *</Label>
                          <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) => {
                              handleFormChange('name', e.target.value);
                              if (!formData.slug || editingTopic) {
                                const slug = e.target.value
                                  .toLowerCase()
                                  .replace(/\s+/g, '-')
                                  .replace(/[^a-z0-9-]/g, '');
                                handleFormChange('slug', slug);
                              }
                            }}
                            required
                            placeholder="Artificial Intelligence"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="slug">Slug</Label>
                          <Input
                            id="slug"
                            value={formData.slug}
                            onChange={(e) => handleFormChange('slug', e.target.value)}
                            placeholder="artificial-intelligence"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="description">Description</Label>
                          <Input
                            id="description"
                            value={formData.description}
                            onChange={(e) => handleFormChange('description', e.target.value)}
                            placeholder="Topics related to AI and machine learning technologies"
                          />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="category">Category</Label>
                            <Select
                              value={formData.category}
                              onValueChange={(value) => handleFormChange('category', value as Topic['category'])}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Select category" />
                              </SelectTrigger>
                              <SelectContent>
                                {Object.entries(categoryLabels).map(([value, label]) => (
                                  <SelectItem key={value} value={value}>
                                    <div className="flex items-center gap-2">
                                      <span>{categoryIcons[value]}</span>
                                      <span>{label}</span>
                                    </div>
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="parent_id">Parent Topic</Label>
                            <Select
                              value={formData.parent_id?.toString() || ''}
                              onValueChange={(value) => handleFormChange('parent_id', value ? parseInt(value) : null)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="No parent (root level)" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="">No parent (root level)</SelectItem>
                                {topics
                                  .filter(t => t.id !== editingTopic?.id && !getChildTopics(t.id).some(ct => ct.id === editingTopic?.id))
                                  .map(topic => (
                                    <SelectItem key={topic.id} value={topic.id.toString()}>
                                      {topic.name}
                                    </SelectItem>
                                  ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="color">Color</Label>
                          <div className="flex items-center gap-2">
                            <div
                              className="w-6 h-6 rounded-full cursor-pointer border"
                              style={{ backgroundColor: formData.color }}
                              onClick={() => {
                                // Simple color picker - cycle through palette
                                const currentIndex = colorPalette.indexOf(formData.color);
                                const nextIndex = (currentIndex + 1) % colorPalette.length;
                                handleFormChange('color', colorPalette[nextIndex]);
                              }}
                            />
                            <Input
                              id="color"
                              type="color"
                              value={formData.color}
                              onChange={(e) => handleFormChange('color', e.target.value)}
                              className="w-20 h-10 p-1"
                            />
                            <Input
                              value={formData.color}
                              onChange={(e) => handleFormChange('color', e.target.value)}
                              className="flex-1"
                              placeholder="#3b82f6"
                            />
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="icon">Icon</Label>
                            <Input
                              id="icon"
                              value={formData.icon}
                              onChange={(e) => handleFormChange('icon', e.target.value)}
                              placeholder="🤖"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="order_index">Order Index</Label>
                            <Input
                              id="order_index"
                              type="number"
                              value={formData.order_index}
                              onChange={(e) => handleFormChange('order_index', parseInt(e.target.value) || 0)}
                              placeholder="0"
                              min={0}
                            />
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="is_active">Active</Label>
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                id="is_active"
                                checked={formData.is_active}
                                onCheckedChange={(checked) => handleFormChange('is_active', checked)}
                              />
                              <Label htmlFor="is_active" className="text-sm font-normal">
                                Topic is active and visible
                              </Label>
                            </div>
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="is_system">System Topic</Label>
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                id="is_system"
                                checked={formData.is_system}
                                onCheckedChange={(checked) => handleFormChange('is_system', checked)}
                                disabled={!!editingTopic?.is_system}
                              />
                              <Label htmlFor="is_system" className="text-sm font-normal">
                                Built-in system topic
                              </Label>
                            </div>
                          </div>
                        </div>
                        
                        <DialogFooter>
                          <Button type="button" variant="secondary" onClick={() => setIsTopicDialogOpen(false)}>
                            Cancel
                          </Button>
                          <Button type="submit" disabled={!formData.name}>
                            {editingTopic ? 'Update Topic' : 'Create Topic'}
                          </Button>
                        </DialogFooter>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              
              <CardContent>
                {topics.length === 0 ? (
                  <Alert>
                    <AlertTitle>No topics found</AlertTitle>
                    <AlertDescription>
                      Create your first topic to get started.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Topic</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Description</TableHead>
                          <TableHead>Color</TableHead>
                          <TableHead className="text-center">Status</TableHead>
                          <TableHead className="text-center">Websites</TableHead>
                          <TableHead className="text-center">Files</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {topicTree.map(renderTopicRow)}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Color palette reference */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Color Palette</CardTitle>
                <CardDescription>
                  Click the color circle to cycle through available colors.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {colorPalette.map(color => (
                    <div
                      key={color}
                      className="w-8 h-8 rounded-full cursor-pointer hover:scale-110 transition-transform"
                      style={{ backgroundColor: color }}
                      title={color}
                      onClick={() => {
                        if (editingTopic) {
                          setFormData(prev => ({ ...prev, color }));
                        }
                      }}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Associations Tab */}
          <TabsContent value="associations">
            <Card>
              <CardHeader>
                <CardTitle>Website-Topic Associations</CardTitle>
                <CardDescription>
                  View and manage which topics are associated with which websites.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {websiteTopics.length === 0 ? (
                  <Alert>
                    <AlertTitle>No associations found</AlertTitle>
                    <AlertDescription>
                      No websites have been associated with topics yet.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Website</TableHead>
                          <TableHead>Topic</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {websiteTopics.map((association) => {
                          const website = websites.find(w => w.id === association.website_id);
                          const topic = topics.find(t => t.id === association.topic_id);
                          
                          return (
                            <TableRow key={association.id}>
                              <TableCell>
                                {website ? (
                                  <div>
                                    <div className="font-medium">{website.title || website.domain}</div>
                                    <div className="text-sm text-muted-foreground">{website.url}</div>
                                  </div>
                                ) : (
                                  <span className="text-muted-foreground">Unknown Website</span>
                                )}
                              </TableCell>
                              <TableCell>
                                {topic ? (
                                  <div className="flex items-center gap-2">
                                    <span>{categoryIcons[topic.category] || '📌'}</span>
                                    <span className="font-medium">{topic.name}</span>
                                  </div>
                                ) : (
                                  <span className="text-muted-foreground">Unknown Topic</span>
                                )}
                              </TableCell>
                              <TableCell>
                                {topic && (
                                  <Badge className={categoryColors[topic.category]}>
                                    {categoryLabels[topic.category]}
                                  </Badge>
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleRemoveAssociation(association.id)}
                                  className="text-red-600 hover:text-red-700"
                                >
                                  Remove
                                </Button>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Association Dialog */}
            <Dialog open={isAssociationDialogOpen} onOpenChange={setIsAssociationDialogOpen}>
              <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                  <DialogTitle>Associate with Website</DialogTitle>
                  <DialogDescription>
                    {selectedTopic && (
                      `Associate topic "${selectedTopic.name}" with a website`
                    )}
                  </DialogDescription>
                </DialogHeader>
                
                <form onSubmit={handleCreateAssociation} className="space-y-4">
                  {selectedTopic && (
                    <div className="p-4 bg-muted rounded-lg">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-10 h-10 rounded-lg flex items-center justify-center"
                          style={{ backgroundColor: selectedTopic.color || '#3b82f6' }}
                        >
                          <span className="text-xl">{categoryIcons[selectedTopic.category] || '📌'}</span>
                        </div>
                        <div>
                          <div className="font-medium">{selectedTopic.name}</div>
                          <Badge className={categoryColors[selectedTopic.category]}>
                            {categoryLabels[selectedTopic.category]}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className="space-y-2">
                    <Label htmlFor="website_id">Website *</Label>
                    <Select
                      value={associationFormData.website_id?.toString() || ''}
                      onValueChange={(value) => handleAssociationFormChange('website_id', value ? parseInt(value) : null)}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select website" />
                      </SelectTrigger>
                      <SelectContent>
                        {selectedTopic && getAvailableWebsites(selectedTopic.id).map(website => (
                          <SelectItem key={website.id} value={website.id.toString()}>
                            <div>
                              <div className="font-medium">{website.title || website.domain}</div>
                              <div className="text-sm text-muted-foreground">{website.url}</div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <DialogFooter>
                    <Button type="button" variant="secondary" onClick={() => setIsAssociationDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={!associationFormData.website_id}>
                      Create Association
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default TopicManagement;
