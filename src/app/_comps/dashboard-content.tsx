"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Search,
  FileImage,
  FileText,
  Video,
  Headphones,
  Plus,
  FolderOpen,
  Share2,
  MoreHorizontal,
  TrendingUp,
  Users,
  Activity,
} from "lucide-react"
import Link from "next/link"

const categories = [
  { name: "Skin Images", count: "480 files", icon: FileImage, color: "bg-purple-500", href: "/upload" },
  { name: "Reports", count: "156 files", icon: FileText, color: "bg-teal-500", href: "/results" },
  { name: "Analysis", count: "30 files", icon: Video, color: "bg-pink-500", href: "/history" },
  { name: "Audio Notes", count: "80 files", icon: Headphones, color: "bg-blue-500", href: "/upload" },
]

const folders = [
  { name: "Recent Scans", count: "230 files", icon: FolderOpen },
  { name: "High Risk Cases", count: "15 files", icon: FolderOpen },
  { name: "Follow-ups", count: "65 files", icon: FolderOpen },
  { name: "Archive", count: "21 files", icon: FolderOpen },
]

const recentFiles = [
  { name: "IMG_000000", type: "PNG file", size: "5 MB", time: "2 hours ago", status: "analyzed" },
  { name: "Patient_scan_001", type: "AVI file", size: "105 MB", time: "5 hours ago", status: "pending" },
  { name: "Melanoma_case", type: "MP3 file", size: "21 MB", time: "1 day ago", status: "analyzed" },
  { name: "Skin_analysis_report", type: "DOCX file", size: "500 kb", time: "2 days ago", status: "completed" },
]

const stats = [
  { title: "Total Scans", value: "1,234", change: "+12%", icon: Activity },
  { title: "High Risk Cases", value: "23", change: "+5%", icon: TrendingUp },
  { title: "Patients Helped", value: "456", change: "+18%", icon: Users },
]

export function DashboardContent() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your skin analysis overview.</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input placeholder="Search files..." className="pl-10 w-80" />
          </div>
          <Link href="/upload">
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="h-4 w-4 mr-2" />
              New Scan
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-green-600 mt-1">{stat.change} from last month</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Categories */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Categories</CardTitle>
              <CardDescription>Quick access to your medical files</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {categories.map((category) => (
                  <Link key={category.name} href={category.href}>
                    <div className="flex flex-col items-center p-4 rounded-lg border hover:bg-gray-50 transition-colors cursor-pointer">
                      <div className={`p-3 rounded-lg ${category.color} text-white mb-2`}>
                        <category.icon className="h-6 w-6" />
                      </div>
                      <h3 className="font-medium text-sm text-center">{category.name}</h3>
                      <p className="text-xs text-gray-500 text-center">{category.count}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Files */}
          <Card>
            <CardHeader>
              <CardTitle>Files</CardTitle>
              <CardDescription>Organize your medical data</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {folders.map((folder) => (
                  <div
                    key={folder.name}
                    className="flex flex-col items-center p-4 rounded-lg border hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    <folder.icon className="h-8 w-8 text-blue-600 mb-2" />
                    <h3 className="font-medium text-sm text-center">{folder.name}</h3>
                    <p className="text-xs text-gray-500 text-center">{folder.count}</p>
                  </div>
                ))}
                <div className="flex flex-col items-center p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-blue-400 transition-colors cursor-pointer">
                  <Plus className="h-8 w-8 text-gray-400 mb-2" />
                  <span className="text-sm text-gray-500">Add folder</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Files */}
          <Card>
            <CardHeader>
              <CardTitle>Recent files</CardTitle>
              <CardDescription>Your latest medical scans and reports</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentFiles.map((file) => (
                  <div key={file.name} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded bg-blue-100">
                        <FileImage className="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{file.name}</p>
                        <p className="text-xs text-gray-500">
                          {file.type} • {file.size}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-500">{file.time}</span>
                      <div
                        className={`px-2 py-1 rounded-full text-xs ${
                          file.status === "analyzed"
                            ? "bg-green-100 text-green-700"
                            : file.status === "pending"
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {file.status}
                      </div>
                      <Button variant="ghost" size="sm">
                        <Share2 className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Storage Usage</span>
                <span className="text-sm font-normal text-blue-600">25% left</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">75 GB of 100 GB are used</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: "75%" }}></div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Shared Analysis</CardTitle>
              <CardDescription>Collaborative cases</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50">
                <div className="p-2 rounded bg-blue-100">
                  <FileImage className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">Melanoma Study</p>
                  <div className="flex -space-x-2 mt-1">
                    <div className="w-6 h-6 rounded-full bg-gray-300 border-2 border-white"></div>
                    <div className="w-6 h-6 rounded-full bg-gray-400 border-2 border-white"></div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 rounded-lg bg-purple-50">
                <div className="p-2 rounded bg-purple-100">
                  <FileText className="h-4 w-4 text-purple-600" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">Research Data</p>
                  <div className="flex -space-x-2 mt-1">
                    <div className="w-6 h-6 rounded-full bg-gray-300 border-2 border-white"></div>
                    <div className="w-6 h-6 rounded-full bg-gray-400 border-2 border-white"></div>
                    <div className="w-6 h-6 rounded-full bg-gray-500 border-2 border-white"></div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 rounded-lg bg-pink-50">
                <div className="p-2 rounded bg-pink-100">
                  <Video className="h-4 w-4 text-pink-600" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">Case Review</p>
                  <div className="flex -space-x-2 mt-1">
                    <div className="w-6 h-6 rounded-full bg-gray-300 border-2 border-white"></div>
                  </div>
                </div>
              </div>

              <Button
                variant="outline"
                className="w-full text-blue-600 border-blue-200 hover:bg-blue-50 bg-transparent"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add more
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
