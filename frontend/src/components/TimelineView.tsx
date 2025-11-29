"use client";

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  Droplet,
  Scan,
  Heart,
  FlaskConical,
  FileText,
  Calendar,
  Building2,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus,
  Filter,
  Clock,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  cn,
  formatDate,
  getRelativeTime,
  getStatusColor,
} from "@/lib/utils";
import { TimelineEntry, TestCategory, TestStatus } from "@/types";

// Category icons mapping
const categoryIcons: Record<TestCategory, React.ReactNode> = {
  blood: <Droplet className="h-4 w-4" />,
  imaging: <Scan className="h-4 w-4" />,
  vitals: <Heart className="h-4 w-4" />,
  urine: <FlaskConical className="h-4 w-4" />,
  other: <FileText className="h-4 w-4" />,
};

// Status colors
const statusColors: Record<TestStatus, string> = {
  normal: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  abnormal: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  critical: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
};

// Check if test result is still valid
function isTestValid(validUntil?: string): boolean {
  if (!validUntil) return false;
  const today = new Date();
  const validDate = new Date(validUntil);
  return validDate >= today;
}

// Get days remaining until expiry
function getDaysRemaining(validUntil?: string): number | null {
  if (!validUntil) return null;
  const today = new Date();
  const validDate = new Date(validUntil);
  const diffTime = validDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

interface TimelineViewProps {
  entries: TimelineEntry[];
  isLoading?: boolean;
}

export function TimelineView({ entries, isLoading = false }: TimelineViewProps) {
  const [filter, setFilter] = useState<TestCategory | "all">("all");
  const [statusFilter, setStatusFilter] = useState<TestStatus | "all">("all");

  // Filter entries
  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      if (filter !== "all" && entry.category !== filter) return false;
      if (statusFilter !== "all" && entry.status !== statusFilter) return false;
      return true;
    });
  }, [entries, filter, statusFilter]);

  // Group entries by month
  const groupedEntries = useMemo(() => {
    const groups: Record<string, TimelineEntry[]> = {};
    
    filteredEntries.forEach((entry) => {
      const date = new Date(entry.test_date);
      const monthYear = date.toLocaleDateString("en-IN", {
        month: "long",
        year: "numeric",
      });
      
      if (!groups[monthYear]) {
        groups[monthYear] = [];
      }
      groups[monthYear].push(entry);
    });
    
    return groups;
  }, [filteredEntries]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="flex gap-4">
                <div className="h-12 w-12 rounded-full bg-gray-200 dark:bg-gray-700" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-1/3 rounded bg-gray-200 dark:bg-gray-700" />
                  <div className="h-3 w-1/2 rounded bg-gray-200 dark:bg-gray-700" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <Card className="border-dashed">
        <CardContent className="p-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
            <FileText className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            No Tests Found
          </h3>
          <p className="mt-2 text-gray-500 dark:text-gray-400">
            Upload your first medical report to start tracking your health timeline.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-500">Filter:</span>
        </div>
        
        {/* Category filters */}
        <Button
          variant={filter === "all" ? "default" : "outline"}
          size="sm"
          onClick={() => setFilter("all")}
        >
          All
        </Button>
        {(["blood", "imaging", "vitals", "urine"] as TestCategory[]).map((cat) => (
          <Button
            key={cat}
            variant={filter === cat ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter(cat)}
          >
            {categoryIcons[cat]}
            <span className="ml-1 capitalize">{cat}</span>
          </Button>
        ))}

        {/* Status filters */}
        <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />
        {(["normal", "abnormal", "critical"] as TestStatus[]).map((status) => (
          <Button
            key={status}
            variant={statusFilter === status ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter(statusFilter === status ? "all" : status)}
            className={cn(
              statusFilter === status && status === "normal" && "bg-green-600 hover:bg-green-700",
              statusFilter === status && status === "abnormal" && "bg-yellow-600 hover:bg-yellow-700",
              statusFilter === status && status === "critical" && "bg-red-600 hover:bg-red-700"
            )}
          >
            <span className="capitalize">{status}</span>
          </Button>
        ))}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {entries.length}
            </div>
            <div className="text-sm text-gray-500">Total Tests</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {entries.filter((e) => e.status === "normal").length}
            </div>
            <div className="text-sm text-gray-500">Normal</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {entries.filter((e) => e.status !== "normal").length}
            </div>
            <div className="text-sm text-gray-500">Need Attention</div>
          </CardContent>
        </Card>
      </div>

      {/* Timeline */}
      {Object.entries(groupedEntries).map(([monthYear, monthEntries]) => (
        <div key={monthYear}>
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-500">
            {monthYear}
          </h3>
          
          <div className="relative space-y-4">
            {/* Timeline line */}
            <div className="timeline-connector" />
            
            {monthEntries.map((entry, index) => (
              <TestCard key={entry.id} entry={entry} index={index} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// Individual test card component
function TestCard({ entry, index }: { entry: TimelineEntry; index: number }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="relative pl-12"
    >
      {/* Timeline dot */}
      <div
        className={cn(
          "absolute left-4 top-4 h-4 w-4 rounded-full border-2 border-white shadow",
          entry.status === "normal" && "bg-green-500",
          entry.status === "abnormal" && "bg-yellow-500",
          entry.status === "critical" && "bg-red-500"
        )}
      />

      <Card
        className={cn(
          "cursor-pointer transition-all hover:shadow-md",
          entry.is_duplicate && "border-amber-200 bg-amber-50/50 dark:border-amber-800 dark:bg-amber-950/20"
        )}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              {/* Category icon */}
              <div
                className={cn(
                  "rounded-lg p-2",
                  entry.category === "blood" && "bg-red-100 text-red-600 dark:bg-red-900/30",
                  entry.category === "imaging" && "bg-blue-100 text-blue-600 dark:bg-blue-900/30",
                  entry.category === "vitals" && "bg-pink-100 text-pink-600 dark:bg-pink-900/30",
                  entry.category === "urine" && "bg-amber-100 text-amber-600 dark:bg-amber-900/30",
                  entry.category === "other" && "bg-gray-100 text-gray-600 dark:bg-gray-800"
                )}
              >
                {categoryIcons[entry.category]}
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-gray-900 dark:text-white">
                    {entry.test_name}
                  </h4>
                  {entry.is_duplicate && (
                    <Badge variant="warning" className="gap-1">
                      <AlertTriangle className="h-3 w-3" />
                      Duplicate
                    </Badge>
                  )}
                </div>
                
                {entry.test_value && (
                  <p className="mt-1 text-lg font-medium">
                    {entry.test_value}
                    {entry.test_unit && (
                      <span className="ml-1 text-sm text-gray-500">
                        {entry.test_unit}
                      </span>
                    )}
                  </p>
                )}

                <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(entry.test_date)}
                  </div>
                  {entry.hospital_name && (
                    <div className="flex items-center gap-1">
                      <Building2 className="h-3 w-3" />
                      {entry.hospital_name}
                    </div>
                  )}
                </div>
                
                {/* Validity Status */}
                {entry.valid_until && (
                  <div className="mt-2">
                    {isTestValid(entry.valid_until) ? (
                      <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                        <CheckCircle2 className="h-3 w-3" />
                        Valid until {formatDate(entry.valid_until)}
                        {getDaysRemaining(entry.valid_until) !== null && getDaysRemaining(entry.valid_until)! <= 30 && (
                          <span className="text-amber-600 dark:text-amber-400">
                            ({getDaysRemaining(entry.valid_until)} days left)
                          </span>
                        )}
                      </div>
                    ) : (
                      <div className="inline-flex items-center gap-1.5 rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                        <XCircle className="h-3 w-3" />
                        Expired on {formatDate(entry.valid_until)}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Status badge */}
            <Badge className={statusColors[entry.status]}>
              {entry.status}
            </Badge>
          </div>

          {/* Expanded content */}
          {isExpanded && entry.reference_range && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mt-4 border-t pt-4"
            >
              <div className="text-sm">
                <span className="text-gray-500">Reference Range: </span>
                <span className="font-medium">{entry.reference_range}</span>
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

// Trend indicator component
function TrendIndicator({ trend }: { trend: "up" | "down" | "stable" }) {
  if (trend === "up") {
    return <TrendingUp className="h-4 w-4 text-red-500" />;
  }
  if (trend === "down") {
    return <TrendingDown className="h-4 w-4 text-green-500" />;
  }
  return <Minus className="h-4 w-4 text-gray-400" />;
}


