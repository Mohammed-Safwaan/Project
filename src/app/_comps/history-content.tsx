"use client"

import { useState } from "react"
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

// Mock data - in real app this would come from API
const historyData = [
  {
    id: "scan_001",
    date: "2024-01-15T10:30:00Z",
    image: "/placeholder.svg?key=hist1",
    condition: "Melanoma",
    confidence: 87,
    riskLevel: "high",
    status: "completed",
    notes: "Irregular borders detected",
  },
  {
    id: "scan_002",
    date: "2024-01-12T14:15:00Z",
    image: "/placeholder.svg?key=hist2",
    condition: "Benign Mole",
    confidence: 94,
    riskLevel: "low",
    status: "completed",
    notes: "Regular pattern, no concerns",
  },
  {
    id: "scan_003",
    date: "2024-01-10T09:45:00Z",
    image: "/placeholder.svg?key=hist3",
    condition: "Atypical Nevus",
    confidence: 76,
    riskLevel: "medium",
    status: "completed",
    notes: "Monitor for changes",
  },
  {
    id: "scan_004",
    date: "2024-01-08T16:20:00Z",
    image: "/placeholder.svg?key=hist4",
    condition: "Seborrheic Keratosis",
    confidence: 89,
    riskLevel: "low",
    status: "completed",
    notes: "Benign skin growth",
  },
  {
    id: "scan_005",
    date: "2024-01-05T11:10:00Z",
    image: "/placeholder.svg?key=hist5",
    condition: "Basal Cell Carcinoma",
    confidence: 82,
    riskLevel: "high",
    status: "completed",
    notes: "Requires immediate attention",
  },
  {
    id: "scan_006",
    date: "2024-01-03T13:30:00Z",
    image: "/placeholder.svg?key=hist6",
    condition: "Dermatofibroma",
    confidence: 91,
    riskLevel: "low",
    status: "completed",
    notes: "Common benign lesion",
  },
]

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

  const filteredData = historyData
    .filter((item) => {
      const matchesSearch =
        item.condition.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.notes.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.id.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesFilter = filterRisk === "all" || item.riskLevel === filterRisk
      return matchesSearch && matchesFilter
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "date":
          return new Date(b.date).getTime() - new Date(a.date).getTime()
        case "condition":
          return a.condition.localeCompare(b.condition)
        case "confidence":
          return b.confidence - a.confidence
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
    high: historyData.filter((item) => item.riskLevel === "high").length,
    medium: historyData.filter((item) => item.riskLevel === "medium").length,
    low: historyData.filter((item) => item.riskLevel === "low").length,
    total: historyData.length,
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
                {filteredData.length} of {historyData.length} scans shown
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
                {filteredData.map((scan) => {
                  const RiskIcon = getRiskIcon(scan.riskLevel)
                  return (
                    <TableRow key={scan.id} className="hover:bg-gray-50">
                      <TableCell>
                        <div className="relative w-12 h-12 rounded-lg overflow-hidden bg-gray-100">
                          <Image
                            src={scan.image || "/placeholder.svg"}
                            alt={`Scan ${scan.id}`}
                            fill
                            className="object-cover"
                          />
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">{scan.id}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 text-sm">
                          <Calendar className="h-4 w-4 text-gray-400" />
                          {formatDate(scan.date)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{scan.condition}</span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{scan.confidence}%</span>
                          <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${scan.confidence}%` }} />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getRiskColor(scan.riskLevel)}>
                          <RiskIcon className="h-3 w-3 mr-1" />
                          {scan.riskLevel.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-600">{scan.notes}</span>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem className="flex items-center gap-2">
                              <Eye className="h-4 w-4" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem className="flex items-center gap-2">
                              <Download className="h-4 w-4" />
                              Download Report
                            </DropdownMenuItem>
                            <DropdownMenuItem className="flex items-center gap-2">
                              <Share2 className="h-4 w-4" />
                              Share Results
                            </DropdownMenuItem>
                            <DropdownMenuItem className="flex items-center gap-2 text-red-600">
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
