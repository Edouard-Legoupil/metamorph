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
import { Plus, Trash2, Edit2, Users, UserPlus, Settings, Loader2, Crown } from 'lucide-react';
import { toast } from 'sonner';

// Types
interface Team {
  id: number;
  name: string;
  description: string | null;
  slug: string;
  is_public: boolean;
  max_members: number | null;
  max_websites: number | null;
  total_storage_gb: number;
  total_websites: number;
  total_files: number;
  owner_id: number | null;
  created_at: string;
  updated_at: string;
}

interface User {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  display_name: string | null;
  role: 'admin' | 'editor' | 'viewer' | 'guest';
  status: 'active' | 'inactive' | 'suspended' | 'deleted';
  avatar_url: string | null;
}

interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  role: 'admin' | 'editor' | 'viewer' | 'guest';
  is_active: boolean;
  invited_at: string | null;
  joined_at: string | null;
  invited_by_id: number | null;
}

interface CrawlerSettings {
  id: number;
  user_id: number | null;
  team_id: number | null;
  default_max_pages: number;
  default_max_depth: number;
  default_crawl_delay: number;
  default_respect_robots: boolean;
  default_same_domain_only: boolean;
  rate_limit_enabled: boolean;
  rate_limit_requests_per_minute: number;
  custom_user_agent: string | null;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const roleColors: Record<string, string> = {
  admin: 'bg-red-100 text-red-800',
  editor: 'bg-blue-100 text-blue-800',
  viewer: 'bg-green-100 text-green-800',
  guest: 'bg-gray-100 text-gray-800',
};

const roleLabels: Record<string, string> = {
  admin: 'Admin',
  editor: 'Editor',
  viewer: 'Viewer',
  guest: 'Guest',
};

const TeamManagement: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [crawlerSettings, setCrawlerSettings] = useState<CrawlerSettings[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [activeTab, setActiveTab] = useState<string>('teams');

  // Form state for creating/editing team
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    slug: '',
    is_public: false,
    max_members: null as number | null,
    max_websites: null as number | null,
    total_storage_gb: 10,
    owner_id: null as number | null,
  });

  // Form state for adding team members
  const [memberFormData, setMemberFormData] = useState({
    user_id: null as number | null,
    role: 'viewer' as 'admin' | 'editor' | 'viewer' | 'guest',
  });

  const [isTeamDialogOpen, setIsTeamDialogOpen] = useState<boolean>(false);
  const [isMemberDialogOpen, setIsMemberDialogOpen] = useState<boolean>(false);
  const [editingTeam, setEditingTeam] = useState<Team | null>(null);

  // Fetch all data
  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const [teamsRes, usersRes, membersRes, settingsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/teams`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/users`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/team-members`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/crawler-settings`, { headers }),
      ]);
      
      if (teamsRes.ok) {
        setTeams(await teamsRes.json());
      }
      if (usersRes.ok) {
        setUsers(await usersRes.json());
      }
      if (membersRes.ok) {
        setTeamMembers(await membersRes.json());
      }
      if (settingsRes.ok) {
        setCrawlerSettings(await settingsRes.json());
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

  const handleMemberFormChange = (field: string, value: any) => {
    setMemberFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  // Create or update team
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
        description: formData.description || null,
        slug: formData.slug || formData.name.toLowerCase().replace(/\s+/g, '-'),
        is_public: formData.is_public,
        max_members: formData.max_members,
        max_websites: formData.max_websites,
        total_storage_gb: formData.total_storage_gb,
        owner_id: formData.owner_id,
      };
      
      let response;
      if (editingTeam) {
        response = await fetch(`${API_BASE_URL}/api/v1/teams/${editingTeam.id}`, {
          method: 'PUT',
          headers,
          body: JSON.stringify(payload),
        });
      } else {
        response = await fetch(`${API_BASE_URL}/api/v1/teams`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        });
      }
      
      if (response.ok) {
        toast.success(editingTeam ? 'Team updated successfully' : 'Team created successfully');
        setIsTeamDialogOpen(false);
        resetForm();
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save team');
      }
    } catch (error) {
      console.error('Error saving team:', error);
      toast.error('Failed to save team');
    }
  };

  // Add team member
  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      if (!selectedTeam || !memberFormData.user_id) return;
      
      const payload = {
        team_id: selectedTeam.id,
        user_id: memberFormData.user_id,
        role: memberFormData.role,
        is_active: true,
      };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/team-members`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      
      if (response.ok) {
        toast.success('Member added successfully');
        setIsMemberDialogOpen(false);
        setMemberFormData({ user_id: null, role: 'viewer' });
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to add member');
      }
    } catch (error) {
      console.error('Error adding member:', error);
      toast.error('Failed to add member');
    }
  };

  // Delete team
  const handleDeleteTeam = async (teamId: number) => {
    if (!confirm('Are you sure you want to delete this team? All members will be removed.')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/teams/${teamId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Team deleted successfully');
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to delete team');
      }
    } catch (error) {
      console.error('Error deleting team:', error);
      toast.error('Failed to delete team');
    }
  };

  // Remove team member
  const handleRemoveMember = async (memberId: number) => {
    if (!confirm('Are you sure you want to remove this member from the team?')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/team-members/${memberId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('Member removed successfully');
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to remove member');
      }
    } catch (error) {
      console.error('Error removing member:', error);
      toast.error('Failed to remove member');
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      slug: '',
      is_public: false,
      max_members: null,
      max_websites: null,
      total_storage_gb: 10,
      owner_id: null,
    });
    setEditingTeam(null);
  };

  // Open edit dialog
  const openEditDialog = (team: Team) => {
    setEditingTeam(team);
    setFormData({
      name: team.name,
      description: team.description || '',
      slug: team.slug,
      is_public: team.is_public,
      max_members: team.max_members,
      max_websites: team.max_websites,
      total_storage_gb: team.total_storage_gb,
      owner_id: team.owner_id,
    });
    setIsTeamDialogOpen(true);
  };

  // Open create dialog
  const openCreateDialog = () => {
    setEditingTeam(null);
    resetForm();
    setIsTeamDialogOpen(true);
  };

  // Open add member dialog
  const openAddMemberDialog = (team: Team) => {
    setSelectedTeam(team);
    setMemberFormData({ user_id: null, role: 'viewer' });
    setIsMemberDialogOpen(true);
  };

  // Get team owner
  const getTeamOwner = (team: Team) => {
    return users.find(u => u.id === team.owner_id);
  };

  // Get team members for a specific team
  const getTeamMembers = (teamId: number) => {
    return teamMembers
      .filter(m => m.team_id === teamId && m.is_active)
      .map(member => {
        const user = users.find(u => u.id === member.user_id);
        return { ...member, user };
      });
  };

  // Get available users to add to team (not already members)
  const getAvailableUsers = (teamId: number) => {
    const currentMemberIds = teamMembers
      .filter(m => m.team_id === teamId)
      .map(m => m.user_id);
    return users.filter(u => !currentMemberIds.includes(u.id));
  };

  // Get team crawler settings
  const getTeamCrawlerSettings = (teamId: number) => {
    return crawlerSettings.find(s => s.team_id === teamId);
  };

  const getFullName = (user: User | null) => {
    if (!user) return 'None';
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user.display_name || user.email;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-3">Loading teams...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Team Management</h1>
          <p className="text-muted-foreground">
            Create and manage teams, add members, and configure team settings.
          </p>
        </div>

        <Tabs defaultValue="teams" value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="teams">Teams</TabsTrigger>
            <TabsTrigger value="members">All Members</TabsTrigger>
          </TabsList>

          {/* Teams Tab */}
          <TabsContent value="teams">
            <Card>
              <CardHeader>
                <CardTitle>Teams</CardTitle>
                <CardDescription>
                  Create and manage teams for organizing users.
                </CardDescription>
                <div className="flex justify-end">
                  <Dialog open={isTeamDialogOpen} onOpenChange={setIsTeamDialogOpen}>
                    <DialogTrigger asChild>
                      <Button onClick={openCreateDialog}>
                        <Plus className="mr-2 h-4 w-4" />
                        Create Team
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[600px]">
                      <DialogHeader>
                        <DialogTitle>
                          {editingTeam ? 'Edit Team' : 'Create New Team'}
                        </DialogTitle>
                        <DialogDescription>
                          {editingTeam 
                            ? `Editing team: ${editingTeam.name}`
                            : 'Create a new team'}
                        </DialogDescription>
                      </DialogHeader>
                      
                      <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="name">Team Name *</Label>
                          <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) => handleFormChange('name', e.target.value)}
                            required
                            placeholder="Marketing Team"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="description">Description</Label>
                          <Input
                            id="description"
                            value={formData.description}
                            onChange={(e) => handleFormChange('description', e.target.value)}
                            placeholder="Team responsible for marketing activities"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="slug">Slug</Label>
                          <Input
                            id="slug"
                            value={formData.slug}
                            onChange={(e) => handleFormChange('slug', e.target.value)}
                            placeholder="marketing-team"
                          />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="owner_id">Team Owner</Label>
                            <Select
                              value={formData.owner_id?.toString() || ''}
                              onValueChange={(value) => handleFormChange('owner_id', value ? parseInt(value) : null)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Select owner" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="">No owner</SelectItem>
                                {users.map(user => (
                                  <SelectItem key={user.id} value={user.id.toString()}>
                                    {getFullName(user)} ({user.email})
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="is_public">Public Team</Label>
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                id="is_public"
                                checked={formData.is_public}
                                onCheckedChange={(checked) => handleFormChange('is_public', checked)}
                              />
                              <Label htmlFor="is_public" className="text-sm font-normal">
                                Anyone can join
                              </Label>
                            </div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="max_members">Max Members</Label>
                            <Input
                              id="max_members"
                              type="number"
                              value={formData.max_members || ''}
                              onChange={(e) => handleFormChange('max_members', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="Unlimited"
                              min={0}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="max_websites">Max Websites</Label>
                            <Input
                              id="max_websites"
                              type="number"
                              value={formData.max_websites || ''}
                              onChange={(e) => handleFormChange('max_websites', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="Unlimited"
                              min={0}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="total_storage_gb">Storage (GB)</Label>
                            <Input
                              id="total_storage_gb"
                              type="number"
                              value={formData.total_storage_gb}
                              onChange={(e) => handleFormChange('total_storage_gb', parseInt(e.target.value) || 0)}
                              placeholder="10"
                              min={0}
                            />
                          </div>
                        </div>
                        
                        <DialogFooter>
                          <Button type="button" variant="secondary" onClick={() => setIsTeamDialogOpen(false)}>
                            Cancel
                          </Button>
                          <Button type="submit" disabled={!formData.name}>
                            {editingTeam ? 'Update Team' : 'Create Team'}
                          </Button>
                        </DialogFooter>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              
              <CardContent>
                {teams.length === 0 ? (
                  <Alert>
                    <AlertTitle>No teams found</AlertTitle>
                    <AlertDescription>
                      Create your first team to get started.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="space-y-4">
                    {teams.map((team) => {
                      const owner = getTeamOwner(team);
                      const members = getTeamMembers(team.id);
                      const settings = getTeamCrawlerSettings(team.id);
                      
                      return (
                        <Card key={team.id} className="border">
                          <CardHeader>
                            <div className="flex items-center justify-between">
                              <div>
                                <CardTitle>{team.name}</CardTitle>
                                <CardDescription>
                                  {team.description || `Team slug: ${team.slug}`}
                                </CardDescription>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => openAddMemberDialog(team)}
                                >
                                  <UserPlus className="mr-2 h-4 w-4" />
                                  Add Member
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => openEditDialog(team)}
                                >
                                  <Edit2 className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleDeleteTeam(team.id)}
                                  className="text-red-600 hover:text-red-700"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          </CardHeader>
                          
                          <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                              <div>
                                <Label className="text-sm font-medium">Owner</Label>
                                <div className="text-sm text-muted-foreground">
                                  {getFullName(owner)}
                                </div>
                              </div>
                              <div>
                                <Label className="text-sm font-medium">Members</Label>
                                <div className="text-sm text-muted-foreground">
                                  {members.length}
                                </div>
                              </div>
                              <div>
                                <Label className="text-sm font-medium">Websites</Label>
                                <div className="text-sm text-muted-foreground">
                                  {team.total_websites} / {team.max_websites || '∞'}
                                </div>
                              </div>
                              <div>
                                <Label className="text-sm font-medium">Storage</Label>
                                <div className="text-sm text-muted-foreground">
                                  {team.total_storage_gb} GB
                                </div>
                              </div>
                            </div>
                            
                            {members.length > 0 && (
                              <div className="rounded-md border">
                                <Table>
                                  <TableHeader>
                                    <TableRow>
                                      <TableHead>Member</TableHead>
                                      <TableHead>Email</TableHead>
                                      <TableHead>Role</TableHead>
                                      <TableHead>Joined</TableHead>
                                      <TableHead className="text-right">Actions</TableHead>
                                    </TableRow>
                                  </TableHeader>
                                  <TableBody>
                                    {members.map(({ ...member, user }) => (
                                      <TableRow key={member.id}>
                                        <TableCell>
                                          {user && (
                                            <div>
                                              <div className="font-medium">
                                                {getFullName(user)}
                                              </div>
                                              {member.user_id === team.owner_id && (
                                                <Badge variant="secondary" className="text-xs mt-1">
                                                  <Crown className="h-2 w-2 mr-1" />
                                                  Owner
                                                </Badge>
                                              )}
                                            </div>
                                          )}
                                        </TableCell>
                                        <TableCell>{user?.email}</TableCell>
                                        <TableCell>
                                          <Badge className={roleColors[member.role]}>
                                            {roleLabels[member.role]}
                                          </Badge>
                                        </TableCell>
                                        <TableCell>
                                          {member.joined_at 
                                            ? new Date(member.joined_at).toLocaleDateString()
                                            : 'Pending'}
                                        </TableCell>
                                        <TableCell className="text-right">
                                          <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleRemoveMember(member.id)}
                                            className="text-red-600 hover:text-red-700"
                                          >
                                            Remove
                                          </Button>
                                        </TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Add Member Dialog */}
            <Dialog open={isMemberDialogOpen} onOpenChange={setIsMemberDialogOpen}>
              <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                  <DialogTitle>Add Member to {selectedTeam?.name}</DialogTitle>
                  <DialogDescription>
                    Add a new member to this team and assign a role.
                  </DialogDescription>
                </DialogHeader>
                
                <form onSubmit={handleAddMember} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="user_id">User *</Label>
                    <Select
                      value={memberFormData.user_id?.toString() || ''}
                      onValueChange={(value) => handleMemberFormChange('user_id', value ? parseInt(value) : null)}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select user" />
                      </SelectTrigger>
                      <SelectContent>
                        {selectedTeam && getAvailableUsers(selectedTeam.id).map(user => (
                          <SelectItem key={user.id} value={user.id.toString()}>
                            {getFullName(user)} ({user.email})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="role">Role *</Label>
                    <Select
                      value={memberFormData.role}
                      onValueChange={(value) => handleMemberFormChange('role', value as typeof memberFormData.role)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select role" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(roleLabels).map(([value, label]) => (
                          <SelectItem key={value} value={value}>{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <DialogFooter>
                    <Button type="button" variant="secondary" onClick={() => setIsMemberDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={!memberFormData.user_id}>
                      Add Member
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </TabsContent>

          {/* All Members Tab */}
          <TabsContent value="members">
            <Card>
              <CardHeader>
                <CardTitle>All Team Members</CardTitle>
                <CardDescription>
                  View all team memberships across all teams.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {teamMembers.length === 0 ? (
                  <Alert>
                    <AlertTitle>No team members found</AlertTitle>
                    <AlertDescription>
                      No users have been added to any teams yet.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>User</TableHead>
                          <TableHead>Team</TableHead>
                          <TableHead>Role</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Joined</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {teamMembers.map((member) => {
                          const user = users.find(u => u.id === member.user_id);
                          const team = teams.find(t => t.id === member.team_id);
                          
                          return (
                            <TableRow key={member.id}>
                              <TableCell>
                                <div className="font-medium">{getFullName(user)}</div>
                                <div className="text-sm text-muted-foreground">{user?.email}</div>
                              </TableCell>
                              <TableCell>
                                {team ? (
                                  <div>
                                    <div className="font-medium">{team.name}</div>
                                    <div className="text-sm text-muted-foreground">{team.slug}</div>
                                  </div>
                                ) : (
                                  <span className="text-muted-foreground">Unknown Team</span>
                                )}
                              </TableCell>
                              <TableCell>
                                <Badge className={roleColors[member.role]}>
                                  {roleLabels[member.role]}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge variant={member.is_active ? 'default' : 'secondary'}>
                                  {member.is_active ? 'Active' : 'Inactive'}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                {member.joined_at 
                                  ? new Date(member.joined_at).toLocaleDateString()
                                  : 'Pending'}
                              </TableCell>
                              <TableCell className="text-right">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleRemoveMember(member.id)}
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
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default TeamManagement;
