"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { BarChart, LineChart, PieChart, DonutChart } from '@/components/Analytics/Charts'
import { Info, AlertTriangle, CheckCircle, TrendingUp, Database, FileText, Users, MessageSquare, Server } from 'lucide-react'

interface ContentQualityMetrics {
  total_cards: number
  status_distribution: Record<string, number>
  card_type_distribution: Record<string, number>
  average_confidence_score: number
  confidence_distribution: Record<string, number>
  average_source_count: number
  source_distribution: Record<string, number>
  temporal_coverage: {
    time_span_days: number
    oldest_content: string | null
    newest_content: string | null
    distribution: Record<string, number>
  }
}

interface SystemUsageStats {
  content_stats: Record<string, number>
  user_stats: Record<string, number>
  collaboration_stats: Record<string, number>
  ingestion_stats: Record<string, number>
}

interface ValidationMetrics {
  total_validations: number
  status_distribution: Record<string, number>
  processing_times: Record<string, number | string>
  validation_quality: Record<string, number | string>
}

interface DiscussionMetrics {
  total_threads: number
  total_comments: number
  activity_metrics: Record<string, number>
  resolution_metrics: Record<string, number | string>
  comment_quality: Record<string, number>
}

interface IngestionMetrics {
  website_stats: {
    total_websites: number
    by_status: Record<string, number>
    by_scrape_frequency: Record<string, number>
    total_files_discovered: number
    total_files_ingested: number
    ingestion_rate: number
  }
  scraping_stats: Record<string, number | string>
  ingestion_stats: Record<string, number | string>
}

interface ContentTrends {
  time_range: Record<string, string | number>
  daily_stats: Array<Record<string, any>>
  totals: Record<string, number | string>
}

interface ComprehensiveDashboard {
  timestamp: string
  overall_health_score: number
  content_quality: ContentQualityMetrics
  wiki_quality: any
  system_usage: SystemUsageStats
  validation_workflow: ValidationMetrics
  discussion_activity: DiscussionMetrics
  ingestion_pipeline: IngestionMetrics
  trends: {
    content_growth: ContentTrends
    validation_activity: ContentTrends
  }
  key_insights: string[]
}

export default function AnalyticsDashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dashboardData, setDashboardData] = useState<ComprehensiveDashboard | null>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [timeRange, setTimeRange] = useState(30)

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch comprehensive dashboard data
      const response = await fetch('/api/v1/analytics/dashboard')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      if (data.success && data.data) {
        setDashboardData(data.data)
      } else {
        throw new Error('Invalid data format')
      }
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const fetchTrendsData = async () => {
    try {
      // Fetch content growth trends
      const contentResponse = await fetch('/api/v1/analytics/trends/content', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({days: timeRange})
      })

      // Fetch validation activity trends
      const validationResponse = await fetch('/api/v1/analytics/trends/validation', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({days: timeRange})
      })

      if (contentResponse.ok && validationResponse.ok) {
        const contentData = await contentResponse.json()
        const validationData = await validationResponse.json()
        
        if (dashboardData) {
          setDashboardData({
            ...dashboardData,
            trends: {
              content_growth: contentData.data,
              validation_activity: validationData.data
            }
          })
        }
      }
    } catch (err) {
      console.error('Failed to fetch trends data:', err)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    fetchTrendsData()
  }, [timeRange])

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    if (score >= 40) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const getHealthText = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Needs Attention'
  }

  if (loading && !dashboardData) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array(4).fill(0).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-6">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Error Loading Analytics</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
        <Button onClick={fetchDashboardData} className="mt-4" variant="outline">
          Retry
        </Button>
      </Alert>
    )
  }

  if (!dashboardData) {
    return (
      <Alert className="m-6">
        <Info className="h-4 w-4" />
        <AlertTitle>No Data Available</AlertTitle>
        <AlertDescription>Analytics data is not available yet.</AlertDescription>
      </Alert>
    )
  }

  // Prepare chart data
  const contentStatusData = Object.entries(dashboardData.content_quality.status_distribution || {}).map(
    ([name, value]) => ({ name, value })
  )

  const cardTypeData = Object.entries(dashboardData.content_quality.card_type_distribution || {}).map(
    ([name, value]) => ({ name, value })
  )

  const confidenceData = Object.entries(dashboardData.content_quality.confidence_distribution || {}).map(
    ([name, value]) => ({ name, value })
  )

  const contentGrowthData = dashboardData.trends?.content_growth?.daily_stats?.map(day => ({
    date: day.date,
    cards: day.knowledge_cards,
    blocks: day.wiki_blocks
  })) || []

  const validationTrendsData = dashboardData.trends?.validation_activity?.daily_stats?.map(day => ({
    date: day.date,
    total: day.total,
    approved: day.approved
  })) || []

  return (
    <div className="p-6 space-y-6">
      {/* Header with Health Score */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <TrendingUp className="w-6 h-6" />
            Analytics Dashboard
          </h1>
          <p className="text-muted-foreground">Comprehensive system insights and performance metrics</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-sm text-muted-foreground">System Health</div>
            <div className="flex items-center gap-2">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl ${getHealthColor(dashboardData.overall_health_score)}`}>
                {Math.round(dashboardData.overall_health_score)}
              </div>
              <div>
                <div className="font-semibold">{getHealthText(dashboardData.overall_health_score)}</div>
                <div className="text-xs text-muted-foreground">
                  Updated: {new Date(dashboardData.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setTimeRange(7)}>
              7 Days
            </Button>
            <Button variant="outline" size="sm" onClick={() => setTimeRange(30)}>
              30 Days
            </Button>
            <Button variant="outline" size="sm" onClick={() => setTimeRange(90)}>
              90 Days
            </Button>
            <Button onClick={fetchDashboardData} size="sm">
              Refresh
            </Button>
          </div>
        </div>
      </div>

      <Separator />

      {/* Key Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="w-5 h-5" />
              Key Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboardData.key_insights?.length ? (
                dashboardData.key_insights.map((insight, index) => (
                  <div key={index} className="flex items-start gap-2 p-3 bg-secondary rounded-lg">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                    <span className="text-sm">{insight}</span>
                  </div>
                ))
              ) : (
                <div className="text-muted-foreground text-sm">
                  No insights available. More data needed.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              Content Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{dashboardData.content_quality.total_cards}</div>
                <div className="text-xs text-muted-foreground">Knowledge Cards</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{dashboardData.wiki_quality.total_blocks || 0}</div>
                <div className="text-xs text-muted-foreground">Wiki Blocks</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{dashboardData.system_usage.content_stats.websites}</div>
                <div className="text-xs text-muted-foreground">Websites</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{dashboardData.system_usage.content_stats.discovered_files}</div>
                <div className="text-xs text-muted-foreground">Files</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              User Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{dashboardData.system_usage.user_stats.total_users}</div>
                <div className="text-xs text-muted-foreground">Users</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{dashboardData.system_usage.user_stats.total_teams}</div>
                <div className="text-xs text-muted-foreground">Teams</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{dashboardData.system_usage.collaboration_stats.validation_cards}</div>
                <div className="text-xs text-muted-foreground">Validations</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{dashboardData.system_usage.collaboration_stats.discussion_threads}</div>
                <div className="text-xs text-muted-foreground">Discussions</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="content">Content Quality</TabsTrigger>
          <TabsTrigger value="workflow">Workflows</TabsTrigger>
          <TabsTrigger value="ingestion">Ingestion</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Content Quality Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Content Quality Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm text-muted-foreground">Average Confidence</span>
                      <Badge variant={dashboardData.content_quality.average_confidence_score >= 0.8 ? 'default' : 'secondary'}>
                        {dashboardData.content_quality.average_confidence_score.toFixed(2)}
                      </Badge>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${dashboardData.content_quality.average_confidence_score * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm text-muted-foreground">Approval Rate</span>
                      <Badge variant="default">
                        {((dashboardData.content_quality.status_distribution.approved || 0) / dashboardData.content_quality.total_cards * 100).toFixed(1)}%
                      </Badge>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{ width: `${((dashboardData.content_quality.status_distribution.approved || 0) / dashboardData.content_quality.total_cards * 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm text-muted-foreground">Average Sources</span>
                      <Badge variant="default">
                        {dashboardData.content_quality.average_source_count.toFixed(1)}
                      </Badge>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full" 
                        style={{ width: `${Math.min(100, dashboardData.content_quality.average_source_count * 20)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Health Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="w-5 h-5" />
                  System Health Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Content Quality</span>
                    <Badge variant="outline">40% weight</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Validation Workflow</span>
                    <Badge variant="outline">30% weight</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Ingestion Pipeline</span>
                    <Badge variant="outline">30% weight</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="content">
          <div className="space-y-6">
            {/* Content Status Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Content Status Distribution</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                <PieChart 
                  data={contentStatusData} 
                  category="name" 
                  value="value" 
                  title="Status Distribution"
                />
              </CardContent>
            </Card>

            {/* Card Type Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Knowledge Card Types</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                <DonutChart 
                  data={cardTypeData} 
                  category="name" 
                  value="value" 
                  title="Card Type Distribution"
                />
              </CardContent>
            </Card>

            {/* Confidence Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Confidence Score Distribution</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                <BarChart 
                  data={confidenceData} 
                  category="name" 
                  value="value" 
                  title="Confidence Levels"
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="workflow">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Validation Workflow */}
            <Card>
              <CardHeader>
                <CardTitle>Validation Workflow Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-4 bg-secondary rounded-lg">
                      <div className="text-2xl font-bold">{dashboardData.validation_workflow.total_validations}</div>
                      <div className="text-xs text-muted-foreground">Total Validations</div>
                    </div>
                    <div className="text-center p-4 bg-secondary rounded-lg">
                      <div className="text-2xl font-bold">
                        {dashboardData.validation_workflow.validation_quality.validation_success_rate ? 
                         `${(dashboardData.validation_workflow.validation_quality.validation_success_rate * 100).toFixed(1)}%` : 'N/A'}
                      </div>
                      <div className="text-xs text-muted-foreground">Success Rate</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Processing Times</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Average:</span>
                        <span className="font-mono">
                          {dashboardData.validation_workflow.processing_times.average_hours?.toFixed(1)} hours
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Median:</span>
                        <span className="font-mono">
                          {dashboardData.validation_workflow.processing_times.median_hours?.toFixed(1)} hours
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Discussion Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Discussion Activity Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-4 bg-secondary rounded-lg">
                      <div className="text-2xl font-bold">{dashboardData.discussion_activity.total_threads}</div>
                      <div className="text-xs text-muted-foreground">Total Threads</div>
                    </div>
                    <div className="text-center p-4 bg-secondary rounded-lg">
                      <div className="text-2xl font-bold">{dashboardData.discussion_activity.total_comments}</div>
                      <div className="text-xs text-muted-foreground">Total Comments</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Resolution Metrics</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Resolved:</span>
                        <span className="font-mono">
                          {dashboardData.discussion_activity.resolution_metrics.resolved_threads}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Resolution Rate:</span>
                        <span className="font-mono">
                          {dashboardData.discussion_activity.resolution_metrics.resolution_rate ? 
                           `${(dashboardData.discussion_activity.resolution_metrics.resolution_rate * 100).toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="ingestion">
          <div className="space-y-6">
            {/* Ingestion Pipeline */}
            <Card>
              <CardHeader>
                <CardTitle>Ingestion Pipeline Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-4 bg-secondary rounded-lg">
                    <div className="text-2xl font-bold">{dashboardData.ingestion_pipeline.website_stats.total_websites}</div>
                    <div className="text-xs text-muted-foreground">Total Websites</div>
                  </div>
                  <div className="text-center p-4 bg-secondary rounded-lg">
                    <div className="text-2xl font-bold">{dashboardData.ingestion_pipeline.website_stats.total_files_discovered}</div>
                    <div className="text-xs text-muted-foreground">Files Discovered</div>
                  </div>
                  <div className="text-center p-4 bg-secondary rounded-lg">
                    <div className="text-2xl font-bold">{dashboardData.ingestion_pipeline.website_stats.total_files_ingested}</div>
                    <div className="text-xs text-muted-foreground">Files Ingested</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-2">Website Status</h4>
                    <div className="space-y-2">
                      {Object.entries(dashboardData.ingestion_pipeline.website_stats.by_status).map(([status, count]) => (
                        <div key={status} className="flex justify-between">
                          <span className="text-sm capitalize">{status}:</span>
                          <span className="font-mono">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Scrape Frequency</h4>
                    <div className="space-y-2">
                      {Object.entries(dashboardData.ingestion_pipeline.website_stats.by_scrape_frequency).map(([freq, count]) => (
                        <div key={freq} className="flex justify-between">
                          <span className="text-sm capitalize">{freq}:</span>
                          <span className="font-mono">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-2">Scraping Performance</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Success Rate:</span>
                        <span className="font-mono">
                          {dashboardData.ingestion_pipeline.scraping_stats.success_rate ? 
                           `${(dashboardData.ingestion_pipeline.scraping_stats.success_rate * 100).toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Avg Duration:</span>
                        <span className="font-mono">
                          {dashboardData.ingestion_pipeline.scraping_stats.average_duration_minutes} minutes
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Ingestion Performance</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Success Rate:</span>
                        <span className="font-mono">
                          {dashboardData.ingestion_pipeline.ingestion_stats.success_rate ? 
                           `${(dashboardData.ingestion_pipeline.ingestion_stats.success_rate * 100).toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Avg Duration:</span>
                        <span className="font-mono">
                          {dashboardData.ingestion_pipeline.ingestion_stats.average_duration_minutes} minutes
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends">
          <div className="space-y-6">
            {/* Content Growth Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Content Growth Trends (Last {timeRange} Days)</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                <LineChart
                  data={contentGrowthData}
                  xAxis="date"
                  yAxis={[
                    { key: 'cards', name: 'Knowledge Cards' },
                    { key: 'blocks', name: 'Wiki Blocks' }
                  ]}
                  title="Daily Content Creation"
                />
              </CardContent>
            </Card>

            {/* Validation Activity Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Validation Activity Trends (Last {timeRange} Days)</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                <LineChart
                  data={validationTrendsData}
                  xAxis="date"
                  yAxis={[
                    { key: 'total', name: 'Total Validations' },
                    { key: 'approved', name: 'Approved' }
                  ]}
                  title="Daily Validation Activity"
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}