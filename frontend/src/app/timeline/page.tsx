"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Plus,
  RefreshCw,
  Download,
  Calendar,
  User,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TimelineView } from "@/components/TimelineView";
import { SavingsCounter } from "@/components/SavingsCounter";
import { useToast } from "@/components/ui/use-toast";
import { formatCurrency } from "@/lib/utils";
import { getTimeline, getSavings, setupDemo } from "@/lib/api";
import { TimelineEntry, SavingsResponse } from "@/types";
import { useAuth } from "@/contexts/AuthContext";

export default function TimelinePage() {
  const { toast } = useToast();
  const { user } = useAuth();
  const [entries, setEntries] = useState<TimelineEntry[]>([]);
  const [savings, setSavings] = useState<SavingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (user?.id) {
      loadData(user.id);
    }
  }, [user?.id]);

  const loadData = async (uid: string) => {
    try {
      setIsLoading(true);
      const [timelineData, savingsData] = await Promise.all([
        getTimeline(uid),
        getSavings(uid),
      ]);
      setEntries(timelineData.entries);
      setSavings(savingsData);
    } catch (error) {
      console.error("Failed to load data:", error);
      toast({
        title: "Failed to load data",
        description: "Please check your connection and try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!user?.id) return;
    setIsRefreshing(true);
    await loadData(user.id);
    setIsRefreshing(false);
    toast({
      title: "Refreshed!",
      description: "Your timeline is up to date.",
    });
  };

  return (
      <div className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl">
          {/* Header */}
          <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <Link href="/">
                <Button variant="ghost" className="mb-2">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Home
                </Button>
              </Link>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Health Timeline
              </h1>
              <p className="mt-1 text-gray-600 dark:text-gray-400">
                Track all your medical tests in one place
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={handleRefresh}
                disabled={isRefreshing}
              >
                <RefreshCw
                  className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`}
                />
                Refresh
              </Button>
              <Link href="/upload">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Report
                </Button>
              </Link>
            </div>
          </div>

          {/* User info card */}
          <Card className="mb-8">
            <CardContent className="flex flex-col items-center justify-between gap-4 p-6 sm:flex-row">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <User className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="font-semibold text-gray-900 dark:text-white">
                    {user?.name || "User"}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {user?.email} {user?.phone && `• ${user.phone}`}
                  </p>
                </div>
              </div>
              <Badge variant="outline" className="text-sm">
                <Calendar className="mr-1 h-3 w-3" />
                {entries.length} tests recorded
              </Badge>
            </CardContent>
          </Card>

          <div className="grid gap-8 lg:grid-cols-3">
            {/* Main timeline */}
            <div className="lg:col-span-2">
              <TimelineView entries={entries} isLoading={isLoading} />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Savings counter */}
              <SavingsCounter
                totalSavings={savings?.total_savings || 0}
                testsSkipped={savings?.tests_skipped || 0}
                breakdown={savings?.breakdown}
                animated={!isLoading}
              />

              {/* Quick stats */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Total Tests</span>
                    <span className="font-semibold">{entries.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Normal Results</span>
                    <span className="font-semibold text-green-600">
                      {entries.filter((e) => e.status === "normal").length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Abnormal Results</span>
                    <span className="font-semibold text-yellow-600">
                      {entries.filter((e) => e.status === "abnormal").length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Critical Results</span>
                    <span className="font-semibold text-red-600">
                      {entries.filter((e) => e.status === "critical").length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Duplicates Detected</span>
                    <span className="font-semibold text-amber-600">
                      {entries.filter((e) => e.is_duplicate).length}
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Categories breakdown */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">By Category</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { name: "Blood Tests", category: "blood", color: "bg-red-500" },
                    { name: "Imaging", category: "imaging", color: "bg-blue-500" },
                    { name: "Vitals", category: "vitals", color: "bg-pink-500" },
                    { name: "Urine Tests", category: "urine", color: "bg-amber-500" },
                    { name: "Other", category: "other", color: "bg-gray-500" },
                  ].map((cat) => {
                    const count = entries.filter(
                      (e) => e.category === cat.category
                    ).length;
                    const percentage = entries.length
                      ? Math.round((count / entries.length) * 100)
                      : 0;

                    return (
                      <div key={cat.category}>
                        <div className="mb-1 flex justify-between text-sm">
                          <span className="text-gray-600 dark:text-gray-400">
                            {cat.name}
                          </span>
                          <span className="font-medium">{count}</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                            className={`h-full ${cat.color}`}
                          />
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>

              {/* Quick actions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Link href="/upload" className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <Plus className="mr-2 h-4 w-4" />
                      Upload New Report
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    disabled
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Export Timeline (Coming Soon)
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
  );
}


