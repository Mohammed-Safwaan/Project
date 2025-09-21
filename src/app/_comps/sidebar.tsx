"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Home, Upload, FileText, History, Settings, LogOut, User } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Upload", href: "/upload", icon: Upload },
  { name: "Results", href: "/results", icon: FileText },
  { name: "History", href: "/history", icon: History },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-screen w-64 flex-col bg-blue-900 text-white">
      {/* User Profile Section */}
      <div className="flex items-center gap-3 p-6 border-b border-blue-800">
        <Avatar className="h-10 w-10">
          <AvatarImage src="/medical-professional.png" alt="User" />
          <AvatarFallback className="bg-blue-700 text-white">
            <User className="h-5 w-5" />
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
          <span className="text-sm font-medium">Dr. Smith</span>
          <span className="text-xs text-blue-200">Medical Professional</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive ? "bg-blue-800 text-white" : "text-blue-100 hover:bg-blue-800 hover:text-white",
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="border-t border-blue-800 p-4 space-y-1">
        <button className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-blue-100 hover:bg-blue-800 hover:text-white transition-colors w-full">
          <Settings className="h-5 w-5" />
          Settings
        </button>
        <button className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-blue-100 hover:bg-blue-800 hover:text-white transition-colors w-full">
          <LogOut className="h-5 w-5" />
          Log out
        </button>
      </div>
    </div>
  )
}
