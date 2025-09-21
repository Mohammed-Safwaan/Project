"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  AlertTriangle,
  CheckCircle2,
  Info,
  Download,
  Share2,
  Calendar,
  Clock,
  User,
  FileText,
  Stethoscope,
  AlertCircle,
  TrendingUp,
  Eye,
  Zap,
  Upload,
} from "lucide-react"
import Image from "next/image"
import Link from "next/link"

// Mock data - in real app this would come from API
const analysisResult = {
  id: "scan_001",
  timestamp: "2024-01-15T10:30:00Z",
  image: "/skin-lesion-medical-scan.jpg",
  primaryDiagnosis: {
    condition: "Melanoma",
    confidence: 87,
    riskLevel: "high",
    description: "Suspicious pigmented lesion with irregular borders and color variation",
  },
  alternativeDiagnoses: [
    { condition: "Atypical Nevus", confidence: 23, riskLevel: "medium" },
    { condition: "Seborrheic Keratosis", confidence: 15, riskLevel: "low" },
    { condition: "Benign Mole", confidence: 8, riskLevel: "low" },
  ],
  recommendations: [
    {
      priority: "urgent",
      action: "Consult a dermatologist immediately",
      description: "Schedule an appointment within 1-2 weeks for professional evaluation",
    },
    {
      priority: "important",
      action: "Biopsy recommended",
      description: "A tissue sample may be needed for definitive diagnosis",
    },
    {
      priority: "monitor",
      action: "Regular monitoring",
      description: "Take photos monthly to track any changes in size, shape, or color",
    },
  ],
  technicalDetails: {
    imageQuality: "Excellent",
    processingTime: "2.3 seconds",
    modelVersion: "SkinAI v3.2",
    analysisDepth: "Deep learning with 15 layer CNN",
  },
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

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case "urgent":
      return "bg-red-500"
    case "important":
      return "bg-yellow-500"
    case "monitor":
      return "bg-blue-500"
    default:
      return "bg-gray-500"
  }
}

export function ResultsContent() {
  const [activeTab, setActiveTab] = useState<"overview" | "detailed" | "recommendations">("overview")

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const RiskIcon = getRiskIcon(analysisResult.primaryDiagnosis.riskLevel)

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <p className="text-gray-600 mt-1">AI-powered skin condition analysis completed</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="flex items-center gap-2 bg-transparent">
            <Download className="h-4 w-4" />
            Download Report
          </Button>
          <Button variant="outline" className="flex items-center gap-2 bg-transparent">
            <Share2 className="h-4 w-4" />
            Share Results
          </Button>
          <Link href="/upload">
            <Button className="bg-blue-600 hover:bg-blue-700">New Analysis</Button>
          </Link>
        </div>
      </div>

      {/* Analysis Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Image and Primary Result */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="h-5 w-5" />
                    Primary Analysis
                  </CardTitle>
                  <CardDescription>
                    Scan ID: {analysisResult.id} • {formatDate(analysisResult.timestamp)}
                  </CardDescription>
                </div>
                <Badge className={getRiskColor(analysisResult.primaryDiagnosis.riskLevel)}>
                  <RiskIcon className="h-3 w-3 mr-1" />
                  {analysisResult.primaryDiagnosis.riskLevel.toUpperCase()} RISK
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="relative aspect-square rounded-lg overflow-hidden bg-gray-100">
                  <Image
                    src={analysisResult.image || "/placeholder.svg"}
                    alt="Analyzed skin lesion"
                    fill
                    className="object-cover"
                  />
                </div>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      {analysisResult.primaryDiagnosis.condition}
                    </h3>
                    <p className="text-gray-600 mb-4">{analysisResult.primaryDiagnosis.description}</p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Confidence Level</span>
                      <span className="text-sm font-bold text-gray-900">
                        {analysisResult.primaryDiagnosis.confidence}%
                      </span>
                    </div>
                    <Progress value={analysisResult.primaryDiagnosis.confidence} className="h-2" />
                  </div>

                  <div className="pt-4 border-t">
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                      <Zap className="h-4 w-4" />
                      <span>Analysis powered by {analysisResult.technicalDetails.modelVersion}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Clock className="h-4 w-4" />
                      <span>Processed in {analysisResult.technicalDetails.processingTime}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alternative Diagnoses */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Alternative Diagnoses
              </CardTitle>
              <CardDescription>Other possible conditions considered by the AI model</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysisResult.alternativeDiagnoses.map((diagnosis, index) => {
                  const AltRiskIcon = getRiskIcon(diagnosis.riskLevel)
                  return (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full ${getRiskColor(diagnosis.riskLevel)}`}>
                          <AltRiskIcon className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{diagnosis.condition}</p>
                          <p className="text-sm text-gray-500 capitalize">{diagnosis.riskLevel} risk</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-gray-900">{diagnosis.confidence}%</p>
                        <div className="w-16 mt-1">
                          <Progress value={diagnosis.confidence} className="h-1" />
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recommendations Sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Stethoscope className="h-5 w-5" />
                Recommendations
              </CardTitle>
              <CardDescription>Suggested next steps based on analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {analysisResult.recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg border-l-4"
                  style={{ borderLeftColor: getPriorityColor(rec.priority).replace("bg-", "#") }}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-1 rounded-full ${getPriorityColor(rec.priority)}`}>
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">{rec.action}</h4>
                      <p className="text-sm text-gray-600">{rec.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Technical Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Image Quality:</span>
                <span className="font-medium">{analysisResult.technicalDetails.imageQuality}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Model Version:</span>
                <span className="font-medium">{analysisResult.technicalDetails.modelVersion}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Processing Time:</span>
                <span className="font-medium">{analysisResult.technicalDetails.processingTime}</span>
              </div>
              <div className="pt-3 border-t">
                <p className="text-xs text-gray-500">{analysisResult.technicalDetails.analysisDepth}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-yellow-600">
                <AlertCircle className="h-5 w-5" />
                Important Notice
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 leading-relaxed">
                This AI analysis is for informational purposes only and should not replace professional medical advice.
                Always consult with a qualified dermatologist for proper diagnosis and treatment.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Action Buttons */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-3 justify-center">
            <Link href="/upload">
              <Button variant="outline" className="flex items-center gap-2 bg-transparent">
                <Upload className="h-4 w-4" />
                Analyze Another Image
              </Button>
            </Link>
            <Link href="/history">
              <Button variant="outline" className="flex items-center gap-2 bg-transparent">
                <Calendar className="h-4 w-4" />
                View History
              </Button>
            </Link>
            <Button className="flex items-center gap-2 bg-green-600 hover:bg-green-700">
              <User className="h-4 w-4" />
              Find Dermatologist
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
