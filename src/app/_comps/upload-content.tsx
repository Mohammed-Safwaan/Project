"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Upload, CloudUpload, X, FileImage, AlertCircle, CheckCircle2, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import Image from "next/image"
import { useRouter } from "next/navigation"

interface UploadedFile {
  file: File
  preview: string
  id: string
  progress: number
  status: "uploading" | "completed" | "error" | "analyzing"
  predictionResult?: PredictionResult
  error?: string
}

interface PredictionResult {
  prediction_id: number
  result: {
    predicted_class: number
    class_name: string
    confidence: number
    risk_level: string
    risk_color: string
    description: string
    is_malignant: boolean
    all_probabilities: Record<string, number>
  }
  image_info: {
    width: number
    height: number
    format: string
    size_bytes: number
  }
  display_image_url: string
  processing_time: number
  timestamp: string
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

export function UploadContent() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null)
  const router = useRouter()

  // Upload file to backend
  const uploadFileToBackend = async (file: File, fileId: string) => {
    try {
      const formData = new FormData()
      formData.append('image', file)

      console.log('Uploading to:', `${API_BASE_URL}/api/predict`)
      console.log('File:', file.name, 'Size:', file.size)

      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        mode: 'cors',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const result: PredictionResult = await response.json()
      
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? { 
                ...f, 
                progress: 100, 
                status: "completed", 
                predictionResult: result 
              }
            : f
        )
      )

      return result

    } catch (error) {
      console.error('Upload error:', error)
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? { 
                ...f, 
                status: "error", 
                error: error instanceof Error ? error.message : 'Upload failed' 
              }
            : f
        )
      )
      throw error
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36).substr(2, 9),
      progress: 0,
      status: "uploading" as const,
    }))

    setUploadedFiles((prev) => [...prev, ...newFiles])

    // Upload each file to backend
    newFiles.forEach(async (uploadFile) => {
      // Simulate upload progress for UI
      const progressInterval = setInterval(() => {
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id && f.status === "uploading"
              ? {
                  ...f,
                  progress: Math.min(f.progress + Math.random() * 15, 85),
                }
              : f,
          ),
        )
      }, 300)

      try {
        // Upload to backend
        await uploadFileToBackend(uploadFile.file, uploadFile.id)
        clearInterval(progressInterval)
      } catch (error) {
        clearInterval(progressInterval)
        console.error('Failed to upload file:', uploadFile.file.name, error)
      }
    })
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".webp"],
    },
    multiple: true,
  })

  const removeFile = (id: string) => {
    setUploadedFiles((prev) => {
      const updated = prev.filter((f) => f.id !== id)
      if (selectedFile?.id === id) {
        setSelectedFile(null)
      }
      return updated
    })
  }

  const handleAnalyzeAgain = async (fileId: string) => {
    const file = uploadedFiles.find(f => f.id === fileId)
    if (!file) return

    setUploadedFiles((prev) =>
      prev.map((f) =>
        f.id === fileId
          ? { ...f, status: "analyzing", progress: 0, predictionResult: undefined, error: undefined }
          : f
      )
    )

    try {
      await uploadFileToBackend(file.file, fileId)
    } catch (error) {
      console.error('Re-analysis failed:', error)
    }
  }

  const completedFiles = uploadedFiles.filter((f) => f.status === "completed")

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Upload Skin Images</h1>
          <p className="text-gray-600 mt-1">Upload high-quality images for AI-powered skin analysis</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload files
              </CardTitle>
              <CardDescription>Drag & drop your skin images here or click to browse</CardDescription>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={cn(
                  "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
                  isDragActive
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-300 hover:border-blue-400 hover:bg-gray-50",
                )}
              >
                <input {...getInputProps()} />
                <CloudUpload className="h-12 w-12 text-blue-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {isDragActive ? "Drop your files here" : "Drag & drop your files here"}
                </h3>
                <p className="text-gray-500 mb-4">or</p>
                <Button variant="outline" className="text-blue-600 border-blue-200 hover:bg-blue-50 bg-transparent">
                  Choose files from your computer
                </Button>
                <p className="text-xs text-gray-400 mt-4">Supports: JPG, PNG, GIF, BMP, WEBP (Max 10MB per file)</p>
              </div>
            </CardContent>
          </Card>

          {/* Upload Progress */}
          {uploadedFiles.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5" />
                  Upload progress
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {uploadedFiles.map((file) => (
                  <div key={file.id} className="flex items-center gap-3 p-3 rounded-lg border">
                    <div className="flex-shrink-0">
                      {file.status === "completed" && file.predictionResult ? (
                        <div className={cn(
                          "p-2 rounded",
                          file.predictionResult.result.is_malignant 
                            ? "bg-red-100" 
                            : "bg-green-100"
                        )}>
                          <CheckCircle2 className={cn(
                            "h-4 w-4",
                            file.predictionResult.result.is_malignant 
                              ? "text-red-600" 
                              : "text-green-600"
                          )} />
                        </div>
                      ) : file.status === "completed" ? (
                        <div className="p-2 rounded bg-green-100">
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        </div>
                      ) : file.status === "error" ? (
                        <div className="p-2 rounded bg-red-100">
                          <AlertCircle className="h-4 w-4 text-red-600" />
                        </div>
                      ) : file.status === "analyzing" ? (
                        <div className="p-2 rounded bg-purple-100">
                          <Loader2 className="h-4 w-4 text-purple-600 animate-spin" />
                        </div>
                      ) : (
                        <div className="p-2 rounded bg-blue-100">
                          <FileImage className="h-4 w-4 text-blue-600" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">{file.file.name}</p>
                      <div className="flex items-center gap-2">
                        <p className="text-xs text-gray-500">{(file.file.size / 1024 / 1024).toFixed(2)} MB</p>
                        {file.predictionResult && (
                          <span className={cn(
                            "text-xs px-2 py-0.5 rounded-full font-medium",
                            file.predictionResult.result.is_malignant 
                              ? "bg-red-100 text-red-700"
                              : "bg-green-100 text-green-700"
                          )}>
                            {file.predictionResult.result.class_name}
                          </span>
                        )}
                      </div>
                      {file.status === "uploading" && <Progress value={file.progress} className="mt-2 h-1" />}
                      {file.status === "analyzing" && <Progress value={75} className="mt-2 h-1" />}
                      {file.error && (
                        <p className="text-xs text-red-500 mt-1">{file.error}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {file.status === "completed" && file.predictionResult ? (
                        <div className="flex flex-col items-end gap-1">
                          <span className="text-xs font-medium text-gray-700">
                            {(file.predictionResult.result.confidence * 100).toFixed(1)}%
                          </span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              sessionStorage.setItem('currentPrediction', JSON.stringify(file.predictionResult))
                              router.push("/results")
                            }}
                            className="text-blue-600 hover:text-blue-800 text-xs px-2 py-1 h-auto"
                          >
                            View Results
                          </Button>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-500">
                          {file.status === "completed" ? "100%" : 
                           file.status === "analyzing" ? "Analyzing..." :
                           file.status === "error" ? "Error" :
                           `${file.progress}%`}
                        </span>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(file.id)}
                        className="text-gray-400 hover:text-red-500"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Preview and Analysis Section */}
        <div className="space-y-6">
          {completedFiles.length > 0 && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Select Image for Analysis</CardTitle>
                  <CardDescription>Choose an uploaded image to analyze for skin conditions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {completedFiles.map((file) => (
                      <div
                        key={file.id}
                        onClick={() => setSelectedFile(file)}
                        className={cn(
                          "relative aspect-square rounded-lg overflow-hidden cursor-pointer border-2 transition-all",
                          selectedFile?.id === file.id
                            ? "border-blue-500 ring-2 ring-blue-200"
                            : "border-gray-200 hover:border-blue-300",
                        )}
                      >
                        <Image
                          src={file.preview || "/placeholder.svg"}
                          alt={file.file.name}
                          fill
                          className="object-cover"
                        />
                        {selectedFile?.id === file.id && (
                          <div className="absolute inset-0 bg-blue-500 bg-opacity-20 flex items-center justify-center">
                            <CheckCircle2 className="h-8 w-8 text-blue-600" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {selectedFile && (
                <Card>
                  <CardHeader>
                    <CardTitle>Image Preview</CardTitle>
                    <CardDescription>Selected image: {selectedFile.file.name}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="relative aspect-video rounded-lg overflow-hidden bg-gray-100 mb-4">
                      <Image
                        src={selectedFile.preview || "/placeholder.svg"}
                        alt={selectedFile.file.name}
                        fill
                        className="object-contain"
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">File size:</span>
                        <span>{(selectedFile.file.size / 1024 / 1024).toFixed(2)} MB</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">File type:</span>
                        <span>{selectedFile.file.type}</span>
                      </div>
                      {selectedFile?.predictionResult ? (
                        <div className="space-y-3">
                          <div className={cn(
                            "p-4 rounded-lg border-2",
                            selectedFile.predictionResult.result.is_malignant 
                              ? "border-red-200 bg-red-50"
                              : "border-green-200 bg-green-50"
                          )}>
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium text-sm">Analysis Result</span>
                              <span className={cn(
                                "text-xs px-2 py-1 rounded-full font-medium",
                                selectedFile.predictionResult.result.is_malignant 
                                  ? "bg-red-100 text-red-700"
                                  : "bg-green-100 text-green-700"
                              )}>
                                {selectedFile.predictionResult.result.risk_level}
                              </span>
                            </div>
                            <p className="font-semibold text-sm mb-1">
                              {selectedFile.predictionResult.result.class_name}
                            </p>
                            <p className="text-xs text-gray-600 mb-2">
                              {selectedFile.predictionResult.result.description}
                            </p>
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-gray-600">
                                Confidence: {(selectedFile.predictionResult.result.confidence * 100).toFixed(1)}%
                              </span>
                              <span className="text-xs text-gray-600">
                                {selectedFile.predictionResult.processing_time.toFixed(2)}s
                              </span>
                            </div>
                          </div>
                          
                          <div className="flex gap-2">
                            <Button
                              onClick={() => {
                                sessionStorage.setItem('currentPrediction', JSON.stringify(selectedFile.predictionResult))
                                router.push("/results")
                              }}
                              className="flex-1 bg-blue-600 hover:bg-blue-700"
                            >
                              <FileImage className="h-4 w-4 mr-2" />
                              View Detailed Results
                            </Button>
                            <Button
                              variant="outline"
                              onClick={() => handleAnalyzeAgain(selectedFile.id)}
                              disabled={selectedFile.status === "analyzing"}
                            >
                              {selectedFile.status === "analyzing" ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                "Re-analyze"
                              )}
                            </Button>
                          </div>
                        </div>
                      ) : selectedFile?.status === "analyzing" ? (
                        <Button
                          disabled
                          className="w-full bg-purple-600"
                          size="lg"
                        >
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Analyzing Image...
                        </Button>
                      ) : selectedFile?.status === "error" ? (
                        <div className="space-y-3">
                          <div className="p-4 rounded-lg border-2 border-red-200 bg-red-50">
                            <p className="font-medium text-sm text-red-800 mb-1">Analysis Failed</p>
                            <p className="text-xs text-red-600">{selectedFile.error}</p>
                          </div>
                          <Button
                            onClick={() => handleAnalyzeAgain(selectedFile.id)}
                            className="w-full bg-blue-600 hover:bg-blue-700"
                            size="lg"
                          >
                            <FileImage className="h-4 w-4 mr-2" />
                            Try Again
                          </Button>
                        </div>
                      ) : (
                        <div className="text-center py-4">
                          <p className="text-sm text-gray-500 mb-2">
                            Image analysis will start automatically after upload completes
                          </p>
                          <div className="animate-pulse flex justify-center">
                            <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {completedFiles.length === 0 && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FileImage className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No images uploaded</h3>
                <p className="text-gray-500 text-center">Upload skin images to start the AI analysis process</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Guidelines */}
      <Card>
        <CardHeader>
          <CardTitle>Image Guidelines</CardTitle>
          <CardDescription>Follow these guidelines for best analysis results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="p-3 rounded-full bg-green-100 w-fit mx-auto mb-3">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
              </div>
              <h4 className="font-medium mb-2">Good Lighting</h4>
              <p className="text-sm text-gray-600">
                Use natural light or bright, even lighting to capture clear details
              </p>
            </div>
            <div className="text-center">
              <div className="p-3 rounded-full bg-blue-100 w-fit mx-auto mb-3">
                <FileImage className="h-6 w-6 text-blue-600" />
              </div>
              <h4 className="font-medium mb-2">High Resolution</h4>
              <p className="text-sm text-gray-600">
                Upload high-quality images (at least 1024x1024 pixels) for accurate analysis
              </p>
            </div>
            <div className="text-center">
              <div className="p-3 rounded-full bg-purple-100 w-fit mx-auto mb-3">
                <AlertCircle className="h-6 w-6 text-purple-600" />
              </div>
              <h4 className="font-medium mb-2">Close-up View</h4>
              <p className="text-sm text-gray-600">Focus on the specific area of concern with minimal background</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
