"use client"

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Search, Filter, SlidersHorizontal, Clock, CheckCircle, Tag, Database } from 'lucide-react'

interface SearchResult {
  id: string
  type: string
  score: number
  document_id: string
  metadata?: Record<string, any>
}

export default function AdvancedSearch() {
  const [searchType, setSearchType] = useState('hybrid')
  const [query, setQuery] = useState('')
  const [limit, setLimit] = useState(10)
  const [bm25Weight, setBm25Weight] = useState(40)
  const [semanticWeight, setSemanticWeight] = useState(60)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<SearchResult[]>([])
  const [error, setError] = useState<string | null>(null)
  const [metadataFilters, setMetadataFilters] = useState<Record<string, any>>({})
  const [metadataWeights, setMetadataWeights] = useState<Record<string, number>>({})
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query')
      return
    }

    setLoading(true)
    setError(null)
    setResults([])

    try {
      const endpoint = searchType === 'bm25' ? '/api/v1/search/bm25' : searchType === 'semantic' ? '/api/v1/search/semantic' : '/api/v1/search/advanced'
      
      const payload = searchType === 'bm25' ? {
        query,
        limit,
        metadata_filters: Object.keys(metadataFilters).length > 0 ? metadataFilters : undefined,
        metadata_weights: Object.keys(metadataWeights).length > 0 ? metadataWeights : undefined
      } : {
        query,
        search_type: searchType,
        limit,
        bm25_weight: bm25Weight / 100,
        semantic_weight: semanticWeight / 100,
        metadata_filters: Object.keys(metadataFilters).length > 0 ? metadataFilters : undefined,
        metadata_weights: Object.keys(metadataWeights).length > 0 ? metadataWeights : undefined
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`)
      }

      const data = await response.json()
      if (data.success && Array.isArray(data.results)) {
        setResults(data.results)
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      console.error('Search error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleMetadataFilterChange = (key: string, value: any) => {
    setMetadataFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleMetadataWeightChange = (key: string, value: number) => {
    setMetadataWeights(prev => ({ ...prev, [key]: value }))
  }

  const clearFilters = () => {
    setMetadataFilters({})
    setMetadataWeights({})
  }

  const getCardTypeName = (type: string) => {
    const types: Record<string, string> = {
      'KC-1': 'Donor Intelligence',
      'KC-2': 'Field Context',
      'KC-3': 'Outcome Evidence',
      'KC-4': 'Partner Capacity',
      'KC-5': 'Track Record',
      'KC-6': 'Crisis Political Economy'
    }
    return types[type] || type
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Search className="w-6 h-6" />
            Advanced Search
          </h1>
          <p className="text-muted-foreground">Powerful search with BM25, semantic, and hybrid capabilities</p>
        </div>
        
        <div className="flex gap-2">
          <Button onClick={handleSearch} disabled={loading || !query.trim()}>
            {loading ? 'Searching...' : 'Search'}
          </Button>
          <Button variant="outline" onClick={clearFilters}>
            Clear Filters
          </Button>
        </div>
      </div>

      <Separator />

      <Tabs value={searchType} onValueChange={setSearchType} className="space-y-4">
        <TabsList>
          <TabsTrigger value="bm25">BM25 Search</TabsTrigger>
          <TabsTrigger value="hybrid">Hybrid Search</TabsTrigger>
          <TabsTrigger value="semantic">Semantic Search</TabsTrigger>
        </TabsList>

        <TabsContent value="bm25">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                BM25 Keyword Search
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="query">Search Query</Label>
                <Input
                  id="query"
                  placeholder="Enter keywords to search..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="mt-1"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Search for specific keywords and terms using BM25 ranking algorithm
                </p>
              </div>

              <div>
                <Label htmlFor="limit">Results Limit</Label>
                <Input
                  id="limit"
                  type="number"
                  min="1"
                  max="100"
                  value={limit}
                  onChange={(e) => setLimit(Math.min(100, Math.max(1, parseInt(e.target.value) || 1)))}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="hybrid">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SlidersHorizontal className="w-5 h-5" />
                Hybrid Search Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="query">Search Query</Label>
                <Input
                  id="query"
                  placeholder="Enter keywords to search..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="mt-1"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Combined BM25 and semantic search for optimal results
                </p>
              </div>

              <div>
                <Label>Search Weights</Label>
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex-1">
                    <Label className="text-sm">BM25 Weight: {bm25Weight}%</Label>
                    <Slider
                      value={[bm25Weight]}
                      onValueChange={([val]) => {
                        setBm25Weight(val)
                        setSemanticWeight(100 - val)
                      }}
                      min={0}
                      max={100}
                      step={10}
                      className="mt-2"
                    />
                  </div>
                  <div className="flex-1">
                    <Label className="text-sm">Semantic Weight: {semanticWeight}%</Label>
                    <Slider
                      value={[semanticWeight]}
                      onValueChange={([val]) => {
                        setSemanticWeight(val)
                        setBm25Weight(100 - val)
                      }}
                      min={0}
                      max={100}
                      step={10}
                      className="mt-2"
                    />
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Adjust the balance between keyword-based (BM25) and semantic similarity search
                </p>
              </div>

              <div>
                <Label htmlFor="limit">Results Limit</Label>
                <Input
                  id="limit"
                  type="number"
                  min="1"
                  max="100"
                  value={limit}
                  onChange={(e) => setLimit(Math.min(100, Math.max(1, parseInt(e.target.value) || 1)))}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="semantic">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SlidersHorizontal className="w-5 h-5" />
                Semantic Search
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="query">Search Query</Label>
                  <Input
                    id="query"
                    placeholder="Enter text for semantic search..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="mt-1"
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Semantic search uses vector embeddings to find conceptually similar content
                  </p>
                </div>

                <div>
                  <Label htmlFor="limit">Results Limit</Label>
                  <Input
                    id="limit"
                    type="number"
                    min="1"
                    max="100"
                    value={limit}
                    onChange={(e) => setLimit(Math.min(100, Math.max(1, parseInt(e.target.value) || 1)))}
                    className="mt-1"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Advanced Options */}
      <Card>
        <CardHeader className="cursor-pointer" onClick={() => setShowAdvanced(!showAdvanced)}>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="w-5 h-5" />
              <span>Advanced Options</span>
            </div>
            <Button variant="ghost" size="sm">
              {showAdvanced ? 'Hide' : 'Show'} Advanced Options
            </Button>
          </CardTitle>
        </CardHeader>
        
        {showAdvanced && (
          <CardContent className="space-y-6">
            {/* Metadata Filters */}
            <div>
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Metadata Filters
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                Filter results based on document attributes
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Card Type Filter */}
                <div className="space-y-2">
                  <Label>Card Type</Label>
                  <Select
                    value={metadataFilters.card_type || ''}
                    onValueChange={(value) => handleMetadataFilterChange('card_type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All types</SelectItem>
                      <SelectItem value="KC-1">Donor Intelligence</SelectItem>
                      <SelectItem value="KC-2">Field Context</SelectItem>
                      <SelectItem value="KC-3">Outcome Evidence</SelectItem>
                      <SelectItem value="KC-4">Partner Capacity</SelectItem>
                      <SelectItem value="KC-5">Track Record</SelectItem>
                      <SelectItem value="KC-6">Crisis Political Economy</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Status Filter */}
                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select
                    value={metadataFilters.status || ''}
                    onValueChange={(value) => handleMetadataFilterChange('status', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All statuses" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All statuses</SelectItem>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="under_review">Under Review</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                      <SelectItem value="rejected">Rejected</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Date Range Filter */}
                <div className="space-y-2">
                  <Label>Date Range</Label>
                  <Select
                    value={metadataFilters.created_at?.gte || ''}
                    onValueChange={(value) => handleMetadataFilterChange('created_at', { gte: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All time" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All time</SelectItem>
                      <SelectItem value="2024-01-01">Since 2024</SelectItem>
                      <SelectItem value="2023-01-01">Since 2023</SelectItem>
                      <SelectItem value="2022-01-01">Since 2022</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Tags Filter */}
                <div className="space-y-2">
                  <Label>Tags</Label>
                  <Select
                    value={metadataFilters.tags?.in?.[0] || ''}
                    onValueChange={(value) => handleMetadataFilterChange('tags', { in: [value] })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All tags" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All tags</SelectItem>
                      <SelectItem value="humanitarian">Humanitarian</SelectItem>
                      <SelectItem value="conflict">Conflict</SelectItem>
                      <SelectItem value="economic">Economic</SelectItem>
                      <SelectItem value="development">Development</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <Separator />

            {/* Metadata Reranking */}
            <div>
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <SlidersHorizontal className="w-5 h-5" />
                Metadata Reranking
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                Boost results based on document attributes (values represent weighting importance)
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Confidence Boost */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-blue-500" />
                    Confidence Score
                  </Label>
                  <Slider
                    value={[metadataWeights.confidence_score || 0]}
                    onValueChange={([val]) => handleMetadataWeightChange('confidence_score', val)}
                    min={0}
                    max={1}
                    step={0.1}
                  />
                  <div className="text-sm text-muted-foreground">
                    Current: {metadataWeights.confidence_score || 0}
                  </div>
                </div>

                {/* Recency Boost */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-green-500" />
                    Recency
                  </Label>
                  <Slider
                    value={[metadataWeights.created_at || 0]}
                    onValueChange={([val]) => handleMetadataWeightChange('created_at', val)}
                    min={0}
                    max={1}
                    step={0.1}
                  />
                  <div className="text-sm text-muted-foreground">
                    Current: {metadataWeights.created_at || 0}
                  </div>
                </div>

                {/* Status Boost */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-purple-500" />
                    Approval Status
                  </Label>
                  <Slider
                    value={[metadataWeights.status || 0]}
                    onValueChange={([val]) => handleMetadataWeightChange('status', val)}
                    min={0}
                    max={1}
                    step={0.1}
                  />
                  <div className="text-sm text-muted-foreground">
                    Current: {metadataWeights.status || 0}
                  </div>
                </div>

                {/* Card Type Boost */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Tag className="w-4 h-4 text-yellow-500" />
                    Card Type
                  </Label>
                  <Slider
                    value={[metadataWeights.card_type || 0]}
                    onValueChange={([val]) => handleMetadataWeightChange('card_type', val)}
                    min={0}
                    max={1}
                    step={0.1}
                  />
                  <div className="text-sm text-muted-foreground">
                    Current: {metadataWeights.card_type || 0}
                  </div>
                </div>

                {/* Tags Boost */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Tag className="w-4 h-4 text-indigo-500" />
                    Tags
                  </Label>
                  <Slider
                    value={[metadataWeights.tags || 0]}
                    onValueChange={([val]) => handleMetadataWeightChange('tags', val)}
                    min={0}
                    max={1}
                    step={0.1}
                  />
                  <div className="text-sm text-muted-foreground">
                    Current: {metadataWeights.tags || 0}
                  </div>
                </div>
              </div>

              <p className="text-sm text-muted-foreground mt-4">
                <strong>Note:</strong> Higher values give more importance to that attribute in ranking results.
              </p>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Active Filters Display */}
      {(Object.keys(metadataFilters).length > 0 || Object.keys(metadataWeights).length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="w-5 h-5" />
              Active Filters & Weights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-4">
              {Object.entries(metadataFilters).map(([key, value]) => (
                <Badge key={key} variant="secondary" className="flex items-center gap-1">
                  {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                  <button 
                    onClick={() => {
                      const newFilters = { ...metadataFilters }
                      delete newFilters[key]
                      setMetadataFilters(newFilters)
                    }}
                    className="ml-1 text-xs hover:text-red-500"
                  >
                    ×
                  </button>
                </Badge>
              ))}
              
              {Object.entries(metadataWeights).map(([key, value]) => (
                <Badge key={key} variant="outline" className="flex items-center gap-1">
                  {key}: {value}
                  <button 
                    onClick={() => {
                      const newWeights = { ...metadataWeights }
                      delete newWeights[key]
                      setMetadataWeights(newWeights)
                    }}
                    className="ml-1 text-xs hover:text-red-500"
                  >
                    ×
                  </button>
                </Badge>
              ))}
            </div>

            <Button variant="outline" size="sm" onClick={clearFilters}>
              Clear All Filters
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="w-5 h-5" />
              Search Results ({results.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.map((result, index) => (
                <div key={result.id} className="p-4 border rounded-lg hover:bg-accent">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold text-blue-600">
                        {result.type === 'card' ? 'Knowledge Card' : result.type === 'block' ? 'Wiki Block' : 'Website'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        ID: {result.document_id} | Score: {result.score.toFixed(2)}
                      </div>
                    </div>
                    <Badge variant={result.score >= 5 ? 'default' : 'secondary'}>
                      {result.score >= 5 ? 'High Relevance' : 'Medium Relevance'}
                    </Badge>
                  </div>

                  {result.metadata && (
                    <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                      {result.metadata.card_type && (
                        <div className="flex items-center gap-1">
                          <Tag className="w-3 h-3" />
                          <span>{getCardTypeName(result.metadata.card_type)}</span>
                        </div>
                      )}
                      {result.metadata.status && (
                        <div className="flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" />
                          <span className="capitalize">{result.metadata.status}</span>
                        </div>
                      )}
                      {result.metadata.confidence_score !== undefined && (
                        <div className="flex items-center gap-1">
                          <span>Confidence: {(result.metadata.confidence_score * 100).toFixed(0)}%</span>
                        </div>
                      )}
                      {result.metadata.created_at && (
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>{new Date(result.metadata.created_at).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={handleSearch} disabled={loading}>
              Load More
            </Button>
            <div className="text-sm text-muted-foreground">
              Showing {results.length} of {results.length} results
            </div>
          </CardFooter>
        </Card>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Search Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}