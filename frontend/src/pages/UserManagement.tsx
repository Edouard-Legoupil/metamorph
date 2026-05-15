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
import { Plus, Trash2, Edit2, Users, Shield, Mail, Loader2, Eye, EyeOff, UserPlus } from 'lucide-react';
import { toast } from 'sonner';

// Types
interface User {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  display_name: string | null;
  role: 'admin' | 'editor' | 'viewer' | 'guest';
  status: 'active' | 'inactive' | 'suspended' | 'deleted';
  avatar_url: string | null;
  api_key: string | null;
  max_websites: number | null;
  max_storage_gb: number | null;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

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

interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  role: 'admin' | 'editor' | 'viewer' | 'guest';
  is_active: boolean;
  invited_at: string | null;
  joined_at: string | null;
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
  default_discover_files: boolean;
  default_file_types: string[];
  rate_limit_enabled: boolean;
  rate_limit_requests_per_minute: number;
  custom_user_agent: string | null;
  created_at: string;
  updated_at: string;
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

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  suspended: 'bg-yellow-100 text-yellow-800',
  deleted: 'bg-red-100 text-red-800',
};

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [crawlerSettings, setCrawlerSettings] = useState<CrawlerSettings[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<string>('users');

  // Form state for creating/editing user
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    display_name: '',
    role: 'viewer' as 'admin' | 'editor' | 'viewer' | 'guest',
    status: 'active' as 'active' | 'inactive' | 'suspended' | 'deleted',
    max_websites: null as number | null,
    max_storage_gb: null as number | null,
  });

  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  // Fetch all data
  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const [usersRes, teamsRes, membersRes, settingsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/users`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/teams`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/team-members`, { headers }),
        fetch(`${API_BASE_URL}/api/v1/crawler-settings`, { headers }),
      ]);
      
      if (usersRes.ok) {
        setUsers(await usersRes.json());
      }
      if (teamsRes.ok) {
        setTeams(await teamsRes.json());
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

  // Create or update user
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 
        'Content-Type': 'application/json',
        'x-api-key': apiKey || '' 
      };
      
      const payload = {
        email: formData.email,
        ...(formData.password && { password: formData.password }),
        first_name: formData.first_name || null,
        last_name: formData.last_name || null,
        display_name: formData.display_name || null,
        role: formData.role,
        status: formData.status,
        max_websites: formData.max_websites,
        max_storage_gb: formData.max_storage_gb,
      };
      
      let response;
      if (editingUser) {
        response = await fetch(`${API_BASE_URL}/api/v1/users/${editingUser.id}`, {
          method: 'PUT',
          headers,
          body: JSON.stringify(payload),
        });
      } else {
        response = await fetch(`${API_BASE_URL}/api/v1/users`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        });
      }
      
      if (response.ok) {
        toast.success(editingUser ? 'User updated successfully' : 'User created successfully');
        setIsDialogOpen(false);
        setFormData({
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          display_name: '',
          role: 'viewer',
          status: 'active',
          max_websites: null,
          max_storage_gb: null,
        });
        setEditingUser(null);
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save user');
      }
    } catch (error) {
      console.error('Error saving user:', error);
      toast.error('Failed to save user');
    }
  };

  // Delete user
  const handleDelete = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        toast.success('User deleted successfully');
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to delete user');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error('Failed to delete user');
    }
  };

  // Open edit dialog
  const openEditDialog = (user: User) => {
    setEditingUser(user);
    setFormData({
      email: user.email,
      password: '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      display_name: user.display_name || '',
      role: user.role,
      status: user.status,
      max_websites: user.max_websites,
      max_storage_gb: user.max_storage_gb,
    });
    setIsDialogOpen(true);
  };

  // Open create dialog
  const openCreateDialog = () => {
    setEditingUser(null);
    setFormData({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      display_name: '',
      role: 'viewer',
      status: 'active',
      max_websites: null,
      max_storage_gb: null,
    });
    setIsDialogOpen(true);
  };

  // Generate API key for user
  const handleGenerateApiKey = async (userId: number) => {
    try {
      const apiKey = localStorage.getItem('API_KEY');
      const headers = { 'x-api-key': apiKey || '' };
      
      const response = await fetch(`${API_BASE_URL}/api/v1/users/${userId}/generate-api-key`, {
        method: 'POST',
        headers,
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success('API key generated successfully');
        fetchData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to generate API key');
      }
    } catch (error) {
      console.error('Error generating API key:', error);
      toast.error('Failed to generate API key');
    }
  };

  // Get user's teams
  const getUserTeams = (userId: number) => {
    return teams.filter(t => t.owner_id === userId)
      .concat(teamMembers.filter(m => m.user_id === userId && m.is_active)
        .map(m => teams.find(t => t.id === m.team_id))
        .filter(Boolean) as Team[]);
  };

  // Get user's crawler settings
  const getUserCrawlerSettings = (userId: number) => {
    return crawlerSettings.find(s => s.user_id === userId);
  };

  const getFullName = (user: User) => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user.display_name || user.email;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-3">Loading users...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
          <p className="text-muted-foreground">
            Manage users, their roles, permissions, and team memberships.
          </p>
        </div>

        <Tabs defaultValue="users" value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="teams">Teams</TabsTrigger>
            <TabsTrigger value="settings">Crawler Settings</TabsTrigger>
          </TabsList>

          {/* Users Tab */}
          <TabsContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>Users</CardTitle>
                <CardDescription>
                  Manage application users and their permissions.
                </CardDescription>
                <div className="flex justify-end">
                  <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                      <Button onClick={openCreateDialog}>
                        <UserPlus className="mr-2 h-4 w-4" />
                        Add User
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[600px]">
                      <DialogHeader>
                        <DialogTitle>
                          {editingUser ? 'Edit User' : 'Create New User'}
                        </DialogTitle>
                        <DialogDescription>
                          {editingUser 
                            ? `Editing user: ${getFullName(editingUser)}`
                            : 'Create a new user account'}
                        </DialogDescription>
                      </DialogHeader>
                      
                      <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="email">Email *</Label>
                            <Input
                              id="email"
                              type="email"
                              value={formData.email}
                              onChange={(e) => handleFormChange('email', e.target.value)}
                              required
                              placeholder="user@example.com"
                            />
                          </div>
                          {(!editingUser || !editingUser.id) && (
                            <div className="space-y-2">
                              <Label htmlFor="password">Password *</Label>
                              <Input
                                id="password"
                                type="password"
                                value={formData.password}
                                onChange={(e) => handleFormChange('password', e.target.value)}
                                required={!editingUser}
                                placeholder="••••••••"
                                minLength={8}
                              />
                            </div>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="first_name">First Name</Label>
                            <Input
                              id="first_name"
                              value={formData.first_name}
                              onChange={(e) => handleFormChange('first_name', e.target.value)}
                              placeholder="John"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="last_name">Last Name</Label>
                            <Input
                              id="last_name"
                              value={formData.last_name}
                              onChange={(e) => handleFormChange('last_name', e.target.value)}
                              placeholder="Doe"
                            />
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="display_name">Display Name</Label>
                          <Input
                            id="display_name"
                            value={formData.display_name}
                            onChange={(e) => handleFormChange('display_name', e.target.value)}
                            placeholder="John Doe"
                          />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="role">Role</Label>
                            <Select
                              value={formData.role}
                              onValueChange={(value) => handleFormChange('role', value as typeof formData.role)}
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
                          <div className="space-y-2">
                            <Label htmlFor="status">Status</Label>
                            <Select
                              value={formData.status}
                              onValueChange={(value) => handleFormChange('status', value as typeof formData.status)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Select status" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="active">Active</SelectItem>
                                <SelectItem value="inactive">Inactive</SelectItem>
                                <SelectItem value="suspended">Suspended</SelectItem>
                                <SelectItem value="deleted">Deleted</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
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
                            <Label htmlFor="max_storage_gb">Max Storage (GB)</Label>
                            <Input
                              id="max_storage_gb"
                              type="number"
                              value={formData.max_storage_gb || ''}
                              onChange={(e) => handleFormChange('max_storage_gb', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="Unlimited"
                              min={0}
                            />
                          </div>
                        </div>
                        
                        <DialogFooter>
                          <Button type="button" variant="secondary" onClick={() => setIsDialogOpen(false)}>
                            Cancel
                          </Button>
                          <Button type="submit" disabled={!formData.email}>
                            {isLoading ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : editingUser ? (
                              'Update User'
                            ) : (
                              'Create User'
                            )}
                          </Button>
                        </DialogFooter>
                      </form>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              
              <CardContent>
                {users.length === 0 ? (
                  <Alert>
                    <AlertTitle>No users found</AlertTitle>
                    <AlertDescription>
                      Create your first user to get started.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>User</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Role</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Websites</TableHead>
                          <TableHead>Storage</TableHead>
                          <TableHead>Last Login</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {users.map((user) => (
                          <TableRow key={user.id}>
                            <TableCell>
                              <div className="font-medium">{getFullName(user)}</div>
                              {user.api_key && (
                                <Badge variant="secondary" className="text-xs mt-1">
                                  Has API Key
                                </Badge>
                              )}
                            </TableCell>
                            <TableCell>{user.email}</TableCell>
                            <TableCell>
                              <Badge className={roleColors[user.role]}>
                                {roleLabels[user.role]}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge className={statusColors[user.status]}>
                                {user.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {user.max_websites ? `${user.max_websites}` : 'Unlimited'}
                            </TableCell>
                            <TableCell>
                              {user.max_storage_gb ? `${user.max_storage_gb} GB` : 'Unlimited'}
                            </TableCell>
                            <TableCell>
                              {user.last_login_at 
                                ? new Date(user.last_login_at).toLocaleDateString()
                                : 'Never'}
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex items-center justify-end gap-2">
                                {!user.api_key && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleGenerateApiKey(user.id)}
                                    title="Generate API Key"
                                  >
                                    <Shield className="h-4 w-4" />
                                  </Button>
                                )}
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => openEditDialog(user)}
                                  title="Edit"
                                >
                                  <Edit2 className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleDelete(user.id)}
                                  title="Delete"
                                  className="text-red-600 hover:text-red-700"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Teams Tab */}
          <TabsContent value="teams">
            <Card>
              <CardHeader>
                <CardTitle>Teams</CardTitle>
                <CardDescription>
                  Manage teams and their members.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Alert className="mb-6">
                  <AlertTitle>Teams management coming soon!</AlertTitle>
                  <AlertDescription>
                    Team management functionality will be added in the next iteration.
                    For now, view the list of existing teams below.
                  </AlertDescription>
                </Alert>
                
                {teams.length === 0 ? (
                  <Alert>
                    <AlertTitle>No teams found</AlertTitle>
                    <AlertDescription>
                      No teams have been created yet.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Slug</TableHead>
                          <TableHead>Owner</TableHead>
                          <TableHead>Members</TableHead>
                          <TableHead>Websites</TableHead>
                          <TableHead>Storage</TableHead>
                          <TableHead>Created</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {teams.map((team) => {
                          const owner = users.find(u => u.id === team.owner_id);
                          const memberCount = teamMembers.filter(m => m.team_id === team.id && m.is_active).length;
                          
                          return (
                            <TableRow key={team.id}>
                              <TableCell className="font-medium">{team.name}</TableCell>
                              <TableCell>{team.slug}</TableCell>
                              <TableCell>
                                {owner ? getFullName(owner) : 'None'}
                              </TableCell>
                              <TableCell>{memberCount}</TableCell>
                              <TableCell>
                                {team.max_websites ? `${team.total_websites}/${team.max_websites}` : team.total_websites}
                              </TableCell>
                              <TableCell>{team.total_storage_gb} GB</TableCell>
                              <TableCell>
                                {new Date(team.created_at).toLocaleDateString()}
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

          {/* Crawler Settings Tab */}
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Crawler Settings</CardTitle>
                <CardDescription>
                  User-specific crawler configuration overrides.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Alert className="mb-6">
                  <AlertTitle>Crawler settings management coming soon!</AlertTitle>
                  <AlertDescription>
                    Crawler settings configuration will be added in the next iteration.
                    For now, view the current crawler settings below.
                  </AlertDescription>
                </Alert>
                
                {crawlerSettings.length === 0 ? (
                  <Alert>
                    <AlertTitle>No custom crawler settings found</AlertTitle>
                    <AlertDescription>
                      No users have custom crawler settings. Global defaults are being used.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>User</TableHead>
                          <TableHead>Team</TableHead>
                          <TableHead>Max Pages</TableHead>
                          <TableHead>Max Depth</TableHead>
                          <TableHead>Crawl Delay</TableHead>
                          <TableHead>Respect Robots</TableHead>
                          <TableHead>Rate Limited</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {crawlerSettings.map((setting) => {
                          const user = users.find(u => u.id === setting.user_id);
                          const team = teams.find(t => t.id === setting.team_id);
                          
                          return (
                            <TableRow key={setting.id}>
                              <TableCell>
                                {user ? getFullName(user) : 'Global'}
                              </TableCell>
                              <TableCell>
                                {team ? team.name : 'None'}
                              </TableCell>
                              <TableCell>{setting.default_max_pages}</TableCell>
                              <TableCell>{setting.default_max_depth}</TableCell>
                              <TableCell>{setting.default_crawl_delay}s</TableCell>
                              <TableCell>
                                <Checkbox
                                  checked={setting.default_respect_robots}
                                  disabled
                                />
                              </TableCell>
                              <TableCell>
                                <Checkbox
                                  checked={setting.rate_limit_enabled}
                                  disabled
                                />
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

export default UserManagement;
