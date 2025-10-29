"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import {
  Search,
  Filter,
  Download,
  Eye,
  MoreHorizontal,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Info,
  Trash2,
  Share2,
  FileText,
  TrendingUp,
  Upload,
} from "lucide-react"
import Image from "next/image"
import Link from "next/link"

// Types for prediction history
interface PredictionHistory {
  prediction_id: string
  filename: string
  timestamp: string
  result: {
    class_name: string
    confidence: number
    description: string
    is_malignant: boolean
    risk_level: string
  }
  processing_time: number
  image_info: {
    width: number
    height: number
    format: string
    size_bytes: number
  }
}



const getRiskColor = (riskLevel: string) => {
  switch (riskLevel) {
    case "high":
      return "text-red-600 bg-red-50 border-red-200"
    case "medium":
      return "text-yellow-600 bg-yellow-50 border-yellow-200"
    case "low":
      return "text-green-600 bg-green-50 border-green-200"
    default:
      return "text-gray-600 bg-gray-50 border-gray-200"
  }
}

const getRiskIcon = (riskLevel: string) => {
  switch (riskLevel) {
    case "high":
      return AlertTriangle
    case "medium":
      return Info
    case "low":
      return CheckCircle2
    default:
      return Info
  }
}

export function HistoryContent() {
  const [searchTerm, setSearchTerm] = useState("")
  const [filterRisk, setFilterRisk] = useState<string>("all")
  const [sortBy, setSortBy] = useState<"date" | "condition" | "confidence">("date")
  const [historyData, setHistoryData] = useState<PredictionHistory[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  // Fetch prediction history from API
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true)
        const response = await fetch('http://localhost:5000/api/predictions')
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        setHistoryData(data.predictions || [])
        setError(null)
      } catch (err) {
        console.error('Error fetching history:', err)
        setError('Failed to load scan history. Please ensure the backend server is running.')
        setHistoryData([])
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [])

  const filteredData = historyData
    .filter((item) => {
      const matchesSearch =
        item.result.class_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.result.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.prediction_id.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesFilter = filterRisk === "all" || item.result.risk_level.toLowerCase() === filterRisk
      return matchesSearch && matchesFilter
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "date":
          return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        case "condition":
          return a.result.class_name.localeCompare(b.result.class_name)
        case "confidence":
          return b.result.confidence - a.result.confidence
        default:
          return 0
      }
    })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const riskCounts = {
    high: historyData.filter((item) => item.result.risk_level.toLowerCase() === "high").length,
    medium: historyData.filter((item) => item.result.risk_level.toLowerCase() === "medium").length,
    low: historyData.filter((item) => item.result.risk_level.toLowerCase() === "low").length,
    total: historyData.length,
  }

  const handleViewDetails = (prediction: PredictionHistory) => {
    // Store prediction result in session storage for results page
    sessionStorage.setItem('currentPrediction', JSON.stringify(prediction))
    router.push('/results')
  }

  const handleDeleteScan = async (predictionId: string) => {
    if (!confirm('Are you sure you want to delete this scan? This action cannot be undone.')) {
      return
    }
    
    try {
      const response = await fetch(`http://localhost:5000/api/predictions/${predictionId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Remove from local state
      setHistoryData(prev => prev.filter(item => item.prediction_id !== predictionId))
    } catch (err) {
      console.error('Error deleting scan:', err)
      alert('Failed to delete scan. Please try again.')
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scan History</h1>
          <p className="text-gray-600 mt-1">View and manage your previous skin analysis results</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="flex items-center gap-2 bg-transparent">
            <Download className="h-4 w-4" />
            Export All
          </Button>
          <Link href="/upload">
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Upload className="h-4 w-4 mr-2" />
              New Scan
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Scans</p>
                <p className="text-2xl font-bold text-gray-900">{riskCounts.total}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Risk</p>
                <p className="text-2xl font-bold text-red-600">{riskCounts.high}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Medium Risk</p>
                <p className="text-2xl font-bold text-yellow-600">{riskCounts.medium}</p>
              </div>
              <Info className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Low Risk</p>
                <p className="text-2xl font-bold text-green-600">{riskCounts.low}</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div>
              <CardTitle>Analysis History</CardTitle>
              <CardDescription>
                {loading ? "Loading..." : `${filteredData.length} of ${historyData.length} scans shown`}
              </CardDescription>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search scans..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-full sm:w-64"
                />
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="flex items-center gap-2 bg-transparent">
                    <Filter className="h-4 w-4" />
                    Risk Level
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setFilterRisk("all")}>All Levels</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterRisk("high")}>High Risk</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterRisk("medium")}>Medium Risk</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterRisk("low")}>Low Risk</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="flex items-center gap-2 bg-transparent">
                    <TrendingUp className="h-4 w-4" />
                    Sort By
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setSortBy("date")}>Date (Newest)</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy("condition")}>Condition (A-Z)</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy("confidence")}>Confidence (High-Low)</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">Image</TableHead>
                  <TableHead>Scan ID</TableHead>
                  <TableHead>Date & Time</TableHead>
                  <TableHead>Condition</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead>Notes</TableHead>
                  <TableHead className="w-16">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8">
                      Loading scan history...
                    </TableCell>
                  </TableRow>
                ) : error ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-red-600">
                      {error}
                    </TableCell>
                  </TableRow>
                ) : filteredData.map((scan) => {
                  const RiskIcon = getRiskIcon(scan.result.risk_level.toLowerCase())
                  const imageUrl = `http://localhost:5000/api/image/${scan.filename}`
                  return (
                    <TableRow key={scan.prediction_id} className="hover:bg-gray-50">
                      <TableCell>
                        <div className="relative w-12 h-12 rounded-lg overflow-hidden bg-gray-100">
                          <Image
                            src={imageUrl || "/placeholder.svg"}
                            alt={`Scan ${scan.prediction_id}`}
                            fill
                            className="object-cover"
                          />
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">{scan.prediction_id}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 text-sm">
                          <Calendar className="h-4 w-4 text-gray-400" />
                          {formatDate(scan.timestamp)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{scan.result.class_name}</span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{(scan.result.confidence * 100).toFixed(1)}%</span>
                          <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${scan.result.confidence * 100}%` }} />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getRiskColor(scan.result.risk_level.toLowerCase())}>
                          <RiskIcon className="h-3 w-3 mr-1" />
                          {scan.result.risk_level.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-600">{scan.result.description}</span>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem 
                              className="flex items-center gap-2"
                              onClick={() => handleViewDetails(scan)}
                            >
                              <Eye className="h-4 w-4" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                              className="flex items-center gap-2"
                              onClick={() => {
                                window.open(`http://localhost:5000/api/report/${scan.prediction_id}`, '_blank')
                              }}
                            >
                              <Download className="h-4 w-4" />
                              Download PDF Report
                            </DropdownMenuItem>
                            <DropdownMenuItem className="flex items-center gap-2">
                              <Share2 className="h-4 w-4" />
                              Share Results
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                              className="flex items-center gap-2 text-red-600"
                              onClick={() => handleDeleteScan(scan.prediction_id)}
                            >
                              <Trash2 className="h-4 w-4" />
                              Delete Scan
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>

          {filteredData.length === 0 && (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No scans found</h3>
              <p className="text-gray-500 mb-4">
                {searchTerm || filterRisk !== "all"
                  ? "Try adjusting your search or filter criteria"
                  : "Start by uploading your first skin image for analysis"}
              </p>
              {!searchTerm && filterRisk === "all" && (
                <Link href="/upload">
                  <Button className="bg-blue-600 hover:bg-blue-700">Upload First Image</Button>
                </Link>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
