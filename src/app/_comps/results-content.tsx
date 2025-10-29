"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
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

// Types for ML prediction results
interface PredictionResult {
  prediction_id: string
  filename: string
  result: {
    class_name: string
    confidence: number
    description: string
    is_malignant: boolean
    risk_level: string
    all_predictions: Array<{
      class_name: string
      confidence: number
      description: string
    }>
  }
  image_info: {
    width: number
    height: number
    format: string
    size_bytes: number
  }
  processing_time: number
  timestamp: string
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
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null)
  const [imageUrl, setImageUrl] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [noData, setNoData] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // First check session storage for current prediction
    const storedResult = sessionStorage.getItem('currentPrediction')
    
    if (storedResult) {
      const result = JSON.parse(storedResult)
      setPredictionResult(result)
      // Create image URL for display
      setImageUrl(`http://localhost:5000/api/image/${result.filename}`)
      setLoading(false)
    } else {
      // If no session data, try to get the latest prediction from backend
      fetch('http://localhost:5000/api/predictions')
        .then(response => response.json())
        .then(data => {
          if (data.predictions && data.predictions.length > 0) {
            // Get the most recent prediction
            const latestPrediction = data.predictions[0]
            setPredictionResult(latestPrediction)
            setImageUrl(`http://localhost:5000/api/image/${latestPrediction.filename}`)
          } else {
            // No predictions found, show empty state
            setNoData(true)
          }
          setLoading(false)
        })
        .catch(error => {
          console.error('Error fetching predictions:', error)
          setNoData(true)
          setLoading(false)
        })
    }
  }, [router])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getRecommendations = (ismalignant: boolean, confidence: number) => {
    const baseRecommendations = []
    
    if (ismalignant || confidence > 0.7) {
      baseRecommendations.push({
        priority: "urgent",
        action: "Consult a dermatologist immediately",
        description: "Schedule an appointment within 1-2 weeks for professional evaluation"
      })
      
      if (ismalignant) {
        baseRecommendations.push({
          priority: "important", 
          action: "Biopsy may be recommended",
          description: "A tissue sample may be needed for definitive diagnosis"
        })
      }
    } else {
      baseRecommendations.push({
        priority: "important",
        action: "Monitor the lesion regularly", 
        description: "Take photos monthly to track any changes in size, shape, or color"
      })
    }
    
    baseRecommendations.push({
      priority: "monitor",
      action: "Follow ABCDE rule",
      description: "Watch for Asymmetry, Border irregularity, Color variation, Diameter >6mm, Evolution"
    })
    
    return baseRecommendations
  }

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-gray-500">Loading results...</div>
        </div>
      </div>
    )
  }

  if (noData || !predictionResult) {
    return (
      <div className="p-6 space-y-6">
        <div className="text-center py-12">
          <div className="mb-6">
            <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Analysis Results</h2>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            {noData 
              ? "No skin lesion analyses have been performed yet. Upload an image to get started with AI-powered dermatological analysis."
              : "Please upload and analyze an image first."
            }
          </p>
          <div className="space-x-4">
            <Link href="/upload">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Upload className="h-4 w-4 mr-2" />
                Start Analysis
              </Button>
            </Link>
            <Link href="/history">
              <Button variant="outline">
                <Eye className="h-4 w-4 mr-2" />
                View History
              </Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const result = predictionResult.result
  const recommendations = getRecommendations(result.is_malignant, result.confidence)
  const RiskIcon = getRiskIcon(result.risk_level.toLowerCase())

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <p className="text-gray-600 mt-1">AI-powered skin condition analysis completed</p>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            className="flex items-center gap-2 bg-transparent"
            onClick={() => {
              window.open(`http://localhost:5000/api/report/${predictionResult.prediction_id}`, '_blank')
            }}
          >
            <Download className="h-4 w-4" />
            Download PDF Report
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
                    Scan ID: {predictionResult.prediction_id} • {formatDate(predictionResult.timestamp)}
                  </CardDescription>
                </div>
                <Badge className={getRiskColor(result.risk_level.toLowerCase())}>
                  <RiskIcon className="h-3 w-3 mr-1" />
                  {result.risk_level.toUpperCase()} RISK
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="relative aspect-square rounded-lg overflow-hidden bg-gray-100">
                  <Image
                    src={imageUrl || "/placeholder.svg"}
                    alt="Analyzed skin lesion"
                    fill
                    className="object-cover"
                  />
                </div>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      {result.class_name}
                    </h3>
                    <p className="text-gray-600 mb-4">{result.description}</p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Confidence Level</span>
                      <span className="text-sm font-bold text-gray-900">
                        {(result.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={result.confidence * 100} className="h-2" />
                  </div>

                  <div className="pt-4 border-t">
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                      <Zap className="h-4 w-4" />
                      <span>Analysis powered by DenseNet201 v1.0</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Clock className="h-4 w-4" />
                      <span>Processed in {predictionResult.processing_time.toFixed(2)} seconds</span>
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
                {result.all_predictions
                  .filter(pred => pred.class_name !== result.class_name)
                  .slice(0, 4)
                  .map((prediction, index) => {
                    // Determine risk level based on class name and confidence
                    const riskLevel = prediction.class_name.toLowerCase().includes('melanoma') ? 'high' : 
                                     prediction.confidence > 0.5 ? 'medium' : 'low'
                    const AltRiskIcon = getRiskIcon(riskLevel)
                    return (
                      <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-full ${getRiskColor(riskLevel)}`}>
                            <AltRiskIcon className="h-4 w-4" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{prediction.class_name}</p>
                            <p className="text-sm text-gray-500 capitalize">{riskLevel} risk</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-gray-900">{(prediction.confidence * 100).toFixed(1)}%</p>
                          <div className="w-16 mt-1">
                            <Progress value={prediction.confidence * 100} className="h-1" />
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
              {recommendations.map((rec, index) => (
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
                <span className="text-gray-600">Image Size:</span>
                <span className="font-medium">{predictionResult.image_info.width}×{predictionResult.image_info.height}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Model Version:</span>
                <span className="font-medium">DenseNet201 v1.0</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Processing Time:</span>
                <span className="font-medium">{predictionResult.processing_time.toFixed(2)}s</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">File Size:</span>
                <span className="font-medium">{(predictionResult.image_info.size_bytes / 1024).toFixed(1)} KB</span>
              </div>
              <div className="pt-3 border-t">
                <p className="text-xs text-gray-500">Deep learning analysis with DenseNet201 architecture (19.3M parameters)</p>
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
