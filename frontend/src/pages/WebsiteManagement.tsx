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
import { Plus, Trash2, Edit2, PlayCircle, StopCircle, FileText, CheckSquare, Square, Loader2, Eye, Search } from 'lucide-react';
import { toast } from 'sonner';

// Types
interface Website {
  id: number;
  url: string;
  domain: string;
  title: string | null;
  description: string | null;
  status: 'pending' | 'active' | 'paused' | 'completed' | 'error' | 'deleted';
  scrape_frequency: string | null;
  max_pages: number;
  max_depth: number;
  respect_robots: boolean;
  crawl_delay: number;
  same_domain_only: boolean;
  cf_access_client_id: string | null;
  cf_token_url: string | null;
  last_scraped_at: string | null;
  next_scrape_at: string | null;
  total_files_discovered: number;
  total_files_ingested: number;
  created_at: string;
  updated_at: string;
}

interface DiscoveredFile {
  id: number;
  website_id: number;
  url: string;
  file_name: string | null;
  file_type: string;
  file_extension: string | null;
  file_size: number | null;
  path: string | null;
  title: string | null;
  author: string | null;
  language: string | null;
  status: string;
  is_selected: boolean;
  discovered_at: string;
  scrape_session_id: number | null;
}

interface ScrapeSession {
  id: number;
  website_id: number;
  session_name: string | null;
  status: string;
  pages_crawled: number;
  files_discovered: number;
  files_selected: number;
  files_ingested: number;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  created_at: string;
}

interface Topic {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  category: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const WebsiteManagement: React.FC = () => {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [files, setFiles] = useState<DiscoveredFile[]>([]);
  const [sessions, setSessions] = useState<ScrapeSession[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedWebsite, setSelectedWebsite] = useState<Website | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [fileTypeFilter, setFileTypeFilter] = useState<string>('all');
  const [showSelectedOnly, setShowSelectedOnly] = useState<boolean>(false);

  // Form state for creating/editing website
  const [formData, setFormData] = useState({
    url: '',
    title: '',
    description: '',
    scrape_frequency: 'manual',
    max_pages: 100,
    max_depth: 5,
    respect_robots: true,
    crawl_delay: 0.5,
    same_domain_only: true,
    cf_access_client_id: '',
    cf_token_url: '',
    topic_ids: [] as number[],
  });

  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [editingWebsite, setEditingWebsite] = useState<Website | null>(null);

  // Fetch all data
  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Fetch websites
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const [websitesRes, topicsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/websites`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/topics`, { headers }),
      ]);
      
      if (websitesRes.ok) {
        setWebsites(await websitesRes.json());
      }
      if (topicsRes.ok) {
        setTopics(await topicsRes.json());
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

  // Fetch files and sessions for selected website
  const fetchWebsiteDetails = useCallback(async (websiteId: number) => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const [filesRes, sessionsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/websites/${websiteId}/files`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/websites/${websiteId}/sessions`, { headers }),
      ]);
      
      if (filesRes.ok) {
        setFiles(await filesRes.json());
      }
      if (sessionsRes.ok) {
        setSessions(await sessionsRes.json());
      }
    } catch (error) {
      console.error('Error fetching website details:', error);
      toast.error('Failed to fetch website details');
    }
  }, []);

  useEffect(() => {
    if (selectedWebsite) {
      fetchWebsiteDetails(selectedWebsite.id);
    } else {
      setFiles([]);
      setSessions([]);
    }
  }, [selectedWebsite, fetchWebsiteDetails]);

  // Handle form changes
  const handleFormChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle topic selection
  const handleTopicToggle = (topicId: number) => {
    setFormData(prev => {
      const topicIds = prev.topic_ids.includes(topicId)
        ? prev.topic_ids.filter(id => id !== topicId)
        : [...prev.topic_ids, topicId];
      return { ...prev, topic_ids: topicIds };
    });
  };

  // Create or update website
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        url: formData.url,
        title: formData.title || undefined,
        description: formData.description || undefined,
        scrape_frequency: formData.scrape_frequency,
        max_pages: formData.max_pages,
        max_depth: formData.max_depth,
        respect_robots: formData.respect_robots,
        crawl_delay: formData.crawl_delay,
        same_domain_only: formData.same_domain_only,
        cf_access_client_id: formData.cf_access_client_id || undefined,
        cf_token_url: formData.cf_token_url || undefined,
        topic_ids: formData.topic_ids,
      };
      
      let response;
      if (editingWebsite) {
        response = await fetch(`${API_BASE_URL}/api/v1/websites/${editingWebsite.id}`, {
          method: 'PUT',
          headers,
          body: JSON.stringify(payload),
        });
      } else {
        response = await fetch(`${API_BASE_URL}/api/v1/websites`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        });
      }
      
      if (response.ok) {
        toast.success(editingWebsite ? 'Website updated successfully' : 'Website created successfully');
        setIsDialogOpen(false);
        setEditingWebsite(null);
        setFormData({
          url: '',
          title: '',
          description: '',
          scrape_frequency: 'manual',
          max_pages: 100,
          max_depth: 5,
          respect_robots: true,
          crawl_delay: 0.5,
          same_domain_only: true,
          cf_access_client_id: '',
          cf_token_url: '',
          topic_ids: [],
        });
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save website');
      }
    } catch (error) {
      console.error('Error saving website:', error);
      toast.error('Failed to save website');
    }
  };

  // Delete website
  const handleDeleteWebsite = async (websiteId: number) => {
    if (!confirm('Are you sure you want to delete this website and all its data?')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/websites/${websiteId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Website deleted successfully');
        fetchData();
        if (selectedWebsite?.id === websiteId) {
          setSelectedWebsite(null);
          setFiles([]);
          setSessions([]);
        }
      } else {
        toast.error('Failed to delete website');
      }
    } catch (error) {
      console.error('Error deleting website:', error);
      toast.error('Failed to delete website');
    }
  };

  // Trigger scrape
  const handleTriggerScrape = async (websiteId: number) => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/websites/${websiteId}/scrape`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          max_pages: selectedWebsite?.max_pages,
          max_depth: selectedWebsite?.max_depth,
          crawl_delay: selectedWebsite?.crawl_delay,
        }),
      });
      
      if (response.ok) {
        toast.success('Scrape started successfully');
        fetchWebsiteDetails(websiteId);
      } else {
        toast.error('Failed to start scrape');
      }
    } catch (error) {
      console.error('Error starting scrape:', error);
      toast.error('Failed to start scrape');
    }
  };

  // Select/deselect files
  const handleSelectFiles = async (fileIds: number[], select: boolean) => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/websites/${selectedWebsite?.id}/files/${select ? 'select' : 'deselect'}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ file_ids: fileIds, select }),
      });
      
      if (response.ok) {
        toast.success(`${fileIds.length} file(s) ${select ? 'selected' : 'deselected'} successfully`);
        fetchWebsiteDetails(selectedWebsite!.id);
      } else {
        toast.error('Failed to update file selection');
      }
    } catch (error) {
      console.error('Error updating file selection:', error);
      toast.error('Failed to update file selection');
    }
  };

  // Trigger ingestion
  const handleTriggerIngestion = async () => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/websites/${selectedWebsite?.id}/ingest`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ job_type: 'full' }),
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success(`Ingestion started: ${data.jobs_created} jobs created`);
        fetchWebsiteDetails(selectedWebsite!.id);
      } else {
        toast.error('Failed to start ingestion');
      }
    } catch (error) {
      console.error('Error starting ingestion:', error);
      toast.error('Failed to start ingestion');
    }
  };

  // Open edit dialog
  const openEditDialog = (website: Website) => {
    setEditingWebsite(website);
    setFormData({
      url: website.url,
      title: website.title || '',
      description: website.description || '',
      scrape_frequency: website.scrape_frequency || 'manual',
      max_pages: website.max_pages,
      max_depth: website.max_depth,
      respect_robots: website.respect_robots,
      crawl_delay: website.crawl_delay,
      same_domain_only: website.same_domain_only,
      cf_access_client_id: website.cf_access_client_id || '',
      cf_token_url: website.cf_token_url || '',
      topic_ids: [], // Will be populated from website.topics
    });
    setIsDialogOpen(true);
  };

  // Filter files
  const filteredFiles = files.filter(file => {
    // Search filter
    if (searchQuery && !file.url.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !file.file_name?.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Type filter
    if (fileTypeFilter !== 'all' && file.file_type !== fileTypeFilter) {
      return false;
    }
    
    // Selected filter
    if (showSelectedOnly && !file.is_selected) {
      return false;
    }
    
    return true;
  });

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'pending':
      case 'queued':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-purple-100 text-purple-800';
      case 'error':
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'paused':
      case 'cancelled':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get file type icon
  const getFileTypeIcon = (fileType: string) => {
    switch (fileType) {
      case 'pdf': return '📄';
      case 'doc':
      case 'docx': return '📝';
      case 'xls':
      case 'xlsx': return '📊';
      case 'ppt':
      case 'pptx': return '📑';
      case 'html':
      case 'htm': return '🌐';
      case 'txt': return '📃';
      case 'json': return '📋';
      default: return '📁';
    }
  };

  if (isLoading && websites.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p>Loading...</p>
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
            <h1 className="text-3xl font-bold">Website Management</h1>
            <p className="text-muted-foreground">Manage websites, crawling, and file discovery</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => {
                setEditingWebsite(null);
                setFormData({
                  url: '',
                  title: '',
                  description: '',
                  scrape_frequency: 'manual',
                  max_pages: 100,
                  max_depth: 5,
                  respect_robots: true,
                  crawl_delay: 0.5,
                  same_domain_only: true,
                  cf_access_client_id: '',
                  cf_token_url: '',
                  topic_ids: [],
                });
              }}>
                <Plus className="mr-2 h-4 w-4" /> Add Website
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{editingWebsite ? 'Edit Website' : 'Add New Website'}</DialogTitle>
                <DialogDescription>
                  Configure a website for scraping and knowledge extraction
                </DialogDescription>
              </DialogHeader>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* URL */}
                <div className="space-y-2">
                  <Label htmlFor="url">Website URL *</Label>
                  <Input
                    id="url"
                    type="url"
                    value={formData.url}
                    onChange={(e) => handleFormChange('url', e.target.value)}
                    placeholder="https://example.com"
                    required
                  />
                </div>

                {/* Title */}
                <div className="space-y-2">
                  <Label htmlFor="title">Title</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => handleFormChange('title', e.target.value)}
                    placeholder="My Website"
                  />
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleFormChange('description', e.target.value)}
                    placeholder="A brief description of the website"
                  />
                </div>

                {/* Topics */}
                {topics.length > 0 && (
                  <div className="space-y-2">
                    <Label>Topics</Label>
                    <div className="flex flex-wrap gap-2">
                      {topics.map(topic => (
                        <Button
                          key={topic.id}
                          type="button"
                          variant={formData.topic_ids.includes(topic.id) ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => handleTopicToggle(topic.id)}
                        >
                          {topic.name}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Scraping Configuration */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="scrape_frequency">Scrape Frequency</Label>
                    <Select
                      value={formData.scrape_frequency}
                      onValueChange={(value) => handleFormChange('scrape_frequency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select frequency" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="manual">Manual</SelectItem>
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="max_pages">Max Pages</Label>
                    <Input
                      id="max_pages"
                      type="number"
                      value={formData.max_pages}
                      onChange={(e) => handleFormChange('max_pages', parseInt(e.target.value) || 0)}
                      min="1"
                      max="10000"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="max_depth">Max Depth</Label>
                    <Input
                      id="max_depth"
                      type="number"
                      value={formData.max_depth}
                      onChange={(e) => handleFormChange('max_depth', parseInt(e.target.value) || 0)}
                      min="1"
                      max="10"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="crawl_delay">Crawl Delay (seconds)</Label>
                    <Input
                      id="crawl_delay"
                      type="number"
                      step="0.1"
                      value={formData.crawl_delay}
                      onChange={(e) => handleFormChange('crawl_delay', parseFloat(e.target.value) || 0)}
                      min="0"
                      max="10"
                    />
                  </div>
                </div>

                {/* Boolean Options */}
                <div className="flex gap-6">
                  <label className="flex items-center gap-2">
                    <Checkbox
                      checked={formData.respect_robots}
                      onCheckedChange={(checked) => handleFormChange('respect_robots', checked)}
                    />
                    <span>Respect robots.txt</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <Checkbox
                      checked={formData.same_domain_only}
                      onCheckedChange={(checked) => handleFormChange('same_domain_only', checked)}
                    />
                    <span>Same domain only</span>
                  </label>
                </div>

                {/* Cloudflare Authentication */}
                <div className="border rounded-lg p-4">
                  <h3 className="font-semibold mb-3">Cloudflare Authentication (Optional)</h3>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <Label htmlFor="cf_client_id">Client ID</Label>
                      <Input
                        id="cf_client_id"
                        type="password"
                        value={formData.cf_access_client_id}
                        onChange={(e) => handleFormChange('cf_access_client_id', e.target.value)}
                        placeholder="Your Cloudflare Access Client ID"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="cf_client_secret">Client Secret</Label>
                        <Input
                          id="cf_client_secret"
                          type="password"
                          value={formData.cf_access_client_secret}
                          onChange={(e) => handleFormChange('cf_access_client_secret', e.target.value)}
                          placeholder="Your Client Secret"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="cf_token_url">Token URL</Label>
                        <Input
                          id="cf_token_url"
                          type="url"
                          value={formData.cf_token_url}
                          onChange={(e) => handleFormChange('cf_token_url', e.target.value)}
                          placeholder="https://team.cloudflareaccess.com/cdn-cgi/access/cfaccess"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={!formData.url}>
                    {editingWebsite ? 'Update Website' : 'Create Website'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <Tabs defaultValue="websites" className="w-full">
          <TabsList className="grid grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            <TabsTrigger value="websites">Websites</TabsTrigger>
            <TabsTrigger value="files" disabled={!selectedWebsite}>Files</TabsTrigger>
            <TabsTrigger value="sessions" disabled={!selectedWebsite}>Sessions</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Websites Tab */}
          <TabsContent value="websites">
            <Card>
              <CardHeader>
                <CardTitle>Websites</CardTitle>
                <CardDescription>
                  Manage all configured websites for scraping
                </CardDescription>
              </CardHeader>
              <CardContent>
                {websites.length === 0 ? (
                  <Alert>
                    <AlertTitle>No websites found</AlertTitle>
                    <AlertDescription>
                      Add your first website to start scraping and extracting knowledge
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Domain</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Files</TableHead>
                        <TableHead>Last Scraped</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {websites.map(website => (
                        <TableRow
                          key={website.id}
                          onClick={() => setSelectedWebsite(website)}
                          className="cursor-pointer hover:bg-muted/50"
                        >
                          <TableCell>{website.id}</TableCell>
                          <TableCell className="font-medium">
                            <div>
                              <div className="font-semibold">{website.domain}</div>
                              <div className="text-sm text-muted-foreground truncate max-w-xs">{website.url}</div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(website.status)}>
                              {website.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              <span className="font-semibold">{website.total_files_discovered}</span>
                              <span className="text-muted-foreground"> / {website.total_files_ingested} ingested</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            {website.last_scraped_at ? new Date(website.last_scraped_at).toLocaleDateString() : 'Never'}
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2" onClick={e => e.stopPropagation()}>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleTriggerScrape(website.id)}
                              >
                                <PlayCircle className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => openEditDialog(website)}
                              >
                                <Edit2 className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-red-500 hover:text-red-700"
                                onClick={() => handleDeleteWebsite(website.id)}
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

          {/* Files Tab */}
          <TabsContent value="files">
            {selectedWebsite && (
              <Card>
                <CardHeader className="flex flex-row justify-between items-center">
                  <div>
                    <CardTitle>Discovered Files</CardTitle>
                    <CardDescription>
                      Files discovered from {selectedWebsite.domain}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleSelectFiles(
                        filteredFiles.filter(f => !f.is_selected).map(f => f.id),
                        true
                      )}
                      disabled={filteredFiles.filter(f => !f.is_selected).length === 0}
                    >
                      <CheckSquare className="h-4 w-4 mr-1" /> Select All
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleSelectFiles(
                        filteredFiles.filter(f => f.is_selected).map(f => f.id),
                        false
                      )}
                      disabled={filteredFiles.filter(f => f.is_selected).length === 0}
                    >
                      <Square className="h-4 w-4 mr-1" /> Deselect All
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleTriggerIngestion}
                      disabled={filteredFiles.filter(f => f.is_selected).length === 0}
                    >
                      <FileText className="h-4 w-4 mr-1" /> Ingest Selected
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Filters */}
                  <div className="flex gap-4 mb-4">
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search files..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-8"
                      />
                    </div>
                    <Select value={fileTypeFilter} onValueChange={setFileTypeFilter}>
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="All types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="pdf">PDF</SelectItem>
                        <SelectItem value="docx">Word</SelectItem>
                        <SelectItem value="xlsx">Excel</SelectItem>
                        <SelectItem value="pptx">PowerPoint</SelectItem>
                        <SelectItem value="html">HTML</SelectItem>
                        <SelectItem value="txt">Text</SelectItem>
                      </SelectContent>
                    </Select>
                    <label className="flex items-center gap-2">
                      <Checkbox
                        checked={showSelectedOnly}
                        onCheckedChange={setShowSelectedOnly}
                      />
                      <span className="text-sm">Selected only</span>
                    </label>
                  </div>

                  {/* File Stats */}
                  <div className="flex gap-6 mb-4 text-sm">
                    <div>
                      <span className="font-semibold">{filteredFiles.length}</span> files matching filters
                    </div>
                    <div>
                      <span className="font-semibold">{filteredFiles.filter(f => f.is_selected).length}</span> selected
                    </div>
                  </div>

                  {files.length === 0 ? (
                    <Alert>
                      <AlertTitle>No files discovered yet</AlertTitle>
                      <AlertDescription>
                        Trigger a scrape to discover files from this website
                      </AlertDescription>
                    </Alert>
                  ) : filteredFiles.length === 0 ? (
                    <Alert>
                      <AlertTitle>No files match your filters</AlertTitle>
                    </Alert>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-12"></TableHead>
                          <TableHead>File</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Path</TableHead>
                          <TableHead>Size</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="w-12"></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredFiles.map(file => (
                          <TableRow key={file.id}>
                            <TableCell>
                              <Checkbox
                                checked={file.is_selected}
                                onCheckedChange={(checked) => handleSelectFiles([file.id], checked)}
                              />
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <span>{getFileTypeIcon(file.file_type)}</span>
                                <div>
                                  <div className="font-medium">{file.file_name || 'Untitled'}</div>
                                  <div className="text-sm text-muted-foreground truncate max-w-xs">{file.url}</div>
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className="text-center">{file.file_type.toUpperCase()}</TableCell>
                            <TableCell className="text-sm text-muted-foreground">{file.path || '/'}</TableCell>
                            <TableCell className="text-sm text-center">
                              {file.file_size ? (file.file_size < 1024 ? `${file.file_size} B` : 
                                file.file_size < 1024 * 1024 ? `${(file.file_size / 1024).toFixed(1)} KB` : 
                                `${(file.file_size / (1024 * 1024)).toFixed(1)} MB`) : 'Unknown'}
                            </TableCell>
                            <TableCell>
                              <Badge variant={file.is_selected ? 'default' : 'outline'}>
                                {file.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Button size="sm" variant="ghost" asChild>
                                <a href={file.url} target="_blank" rel="noopener noreferrer">
                                  <Eye className="h-4 w-4" />
                                </a>
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Sessions Tab */}
          <TabsContent value="sessions">
            {selectedWebsite && (
              <Card>
                <CardHeader>
                  <CardTitle>Scrape Sessions</CardTitle>
                  <CardDescription>
                    History of scrape sessions for {selectedWebsite.domain}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {sessions.length === 0 ? (
                    <Alert>
                      <AlertTitle>No scrape sessions yet</AlertTitle>
                      <AlertDescription>
                        Trigger a scrape to start collecting data
                      </AlertDescription>
                    </Alert>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>ID</TableHead>
                          <TableHead>Name</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Pages Crawled</TableHead>
                          <TableHead>Files Found</TableHead>
                          <TableHead>Started</TableHead>
                          <TableHead>Duration</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {sessions.map(session => (
                          <TableRow key={session.id}>
                            <TableCell>{session.id}</TableCell>
                            <TableCell>{session.session_name || `Session ${session.id}`}</TableCell>
                            <TableCell>
                              <Badge className={getStatusColor(session.status)}>
                                {session.status}
                              </Badge>
                            </TableCell>
                            <TableCell>{session.pages_crawled}</TableCell>
                            <TableCell>{session.files_discovered}</TableCell>
                            <TableCell>
                              {session.started_at ? new Date(session.started_at).toLocaleString() : 'N/A'}
                            </TableCell>
                            <TableCell>
                              {session.duration_seconds ? `${session.duration_seconds.toFixed(1)}s` : 'N/A'}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Settings</CardTitle>
                <CardDescription>
                  Application settings for website crawling
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Alert>
                  <AlertTitle>Settings UI</AlertTitle>
                  <AlertDescription>
                    Settings configuration will be available here. For now, configure settings via API or environment variables.
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

export default WebsiteManagement;
