"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  IndianRupee,
  FileText,
  Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ReportUploader } from "@/components/ReportUploader";
import { DuplicateAlert, MultiDuplicateAlert } from "@/components/DuplicateAlert";
import { useToast } from "@/components/ui/use-toast";
import { formatCurrency, formatDate } from "@/lib/utils";
import { UploadReportResponse, DuplicateAlert as DuplicateAlertType } from "@/types";
import { useAuth } from "@/contexts/AuthContext";

export default function UploadPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { user } = useAuth();
  const [uploadResult, setUploadResult] = useState<UploadReportResponse | null>(null);
  const [showDuplicateAlert, setShowDuplicateAlert] = useState(false);
  const [currentAlerts, setCurrentAlerts] = useState<DuplicateAlertType[]>([]);

  const handleUploadComplete = (response: UploadReportResponse) => {
    setUploadResult(response);

    if (response.duplicate_alerts && response.duplicate_alerts.length > 0) {
      setCurrentAlerts(response.duplicate_alerts);
      setShowDuplicateAlert(true);
    } else {
      // No duplicates, show success
      toast({
        title: "Report Analyzed Successfully!",
        description: `${response.extracted_data?.tests?.length || 0} tests extracted from your report.`,
        variant: "success",
      });
    }
  };

  const handleDuplicateComplete = () => {
    const skippedCount = currentAlerts.filter(a => a.decision === 'skip').length;
    const savedAmount = currentAlerts.reduce(
      (sum, alert) => sum + (alert.decision === 'skip' ? alert.savings_amount : 0),
      0
    );

    if (skippedCount > 0) {
      toast({
        title: `You saved ${formatCurrency(savedAmount)}!`,
        description: `${skippedCount} duplicate test(s) were skipped.`,
        variant: "success",
      });
    }

    setShowDuplicateAlert(false);
  };

  const handleError = (error: string) => {
    toast({
      title: "Upload Failed",
      description: error,
      variant: "destructive",
    });
  };

  return (
      <div className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          {/* Header */}
          <div className="mb-8">
            <Link href="/">
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Home
              </Button>
            </Link>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Upload Medical Report
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Take a photo or upload your medical report for instant analysis
            </p>
          </div>

          <div className="grid gap-8 lg:grid-cols-3">
            {/* Main upload area */}
            <div className="lg:col-span-2">
              {!uploadResult ? (
                <ReportUploader
                  userId={user?.id || ""}
                  onUploadComplete={handleUploadComplete}
                  onError={handleError}
                />
              ) : (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Card className="border-emerald-200 bg-emerald-50/50 dark:border-emerald-800 dark:bg-emerald-950/20">
                    <CardHeader>
                      <div className="flex items-center gap-3">
                        <div className="rounded-full bg-emerald-100 p-2 dark:bg-emerald-900">
                          <CheckCircle2 className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
                        </div>
                        <div>
                          <CardTitle>Report Analyzed!</CardTitle>
                          <p className="text-sm text-gray-500">
                            {uploadResult.message}
                          </p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Report details */}
                      {uploadResult.extracted_data && (
                        <>
                          {uploadResult.extracted_data.hospital_name && (
                            <div className="flex items-center gap-2 text-sm">
                              <FileText className="h-4 w-4 text-gray-400" />
                              <span className="text-gray-600 dark:text-gray-400">
                                {uploadResult.extracted_data.hospital_name}
                              </span>
                            </div>
                          )}
                          {uploadResult.extracted_data.report_date && (
                            <div className="flex items-center gap-2 text-sm">
                              <Clock className="h-4 w-4 text-gray-400" />
                              <span className="text-gray-600 dark:text-gray-400">
                                {formatDate(uploadResult.extracted_data.report_date)}
                              </span>
                            </div>
                          )}

                          {/* Extracted tests */}
                          <div className="mt-4">
                            <h4 className="mb-3 font-semibold">Extracted Tests</h4>
                            <div className="space-y-2">
                              {uploadResult.extracted_data.tests?.map((test, index) => (
                                <div
                                  key={index}
                                  className="flex items-center justify-between rounded-lg bg-white p-3 shadow-sm dark:bg-gray-800"
                                >
                                  <div>
                                    <span className="font-medium">{test.test_name}</span>
                                    {test.test_value && (
                                      <span className="ml-2 text-sm text-gray-500">
                                        {test.test_value} {test.test_unit}
                                      </span>
                                    )}
                                  </div>
                                  <Badge
                                    variant={
                                      test.status === "normal"
                                        ? "success"
                                        : test.status === "critical"
                                          ? "critical"
                                          : "warning"
                                    }
                                  >
                                    {test.status || "normal"}
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        </>
                      )}

                      {/* Duplicate alerts summary */}
                      {uploadResult.duplicate_alerts?.length > 0 && (
                        <div className="mt-4 rounded-lg bg-amber-50 p-4 dark:bg-amber-950/30">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5 text-amber-600" />
                            <span className="font-medium text-amber-800 dark:text-amber-200">
                              {uploadResult.duplicate_alerts.length} duplicate test(s) detected
                            </span>
                          </div>
                          <p className="mt-1 text-sm text-amber-700 dark:text-amber-300">
                            Potential savings: {formatCurrency(uploadResult.total_potential_savings)}
                          </p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex gap-3 pt-4">
                        <Link href="/timeline" className="flex-1">
                          <Button className="w-full">View Timeline</Button>
                        </Link>
                        <Button
                          variant="outline"
                          onClick={() => setUploadResult(null)}
                        >
                          Upload Another
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Tips card */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Tips for Best Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-500" />
                    <span>Ensure the report is well-lit and clearly visible</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-500" />
                    <span>Include all test values in the frame</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-500" />
                    <span>Avoid blurry or cropped images</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-500" />
                    <span>PDF reports work best if available</span>
                  </div>
                </CardContent>
              </Card>

              {/* Savings info */}
              <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/30">
                <CardContent className="p-6">
                  <div className="mb-3 flex items-center gap-2">
                    <IndianRupee className="h-5 w-5 text-emerald-600" />
                    <span className="font-semibold text-emerald-800 dark:text-emerald-200">
                      Smart Savings
                    </span>
                  </div>
                  <p className="text-sm text-emerald-700 dark:text-emerald-300">
                    Our AI checks if you've done similar tests recently and alerts
                    you about potential duplicates, saving you money.
                  </p>
                </CardContent>
              </Card>

              {/* Quick stats */}
              {uploadResult && (
                <Card>
                  <CardContent className="p-6">
                    <h3 className="mb-4 font-semibold">Analysis Summary</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Tests Found</span>
                        <span className="font-semibold">
                          {uploadResult.extracted_data?.tests?.length || 0}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Duplicates</span>
                        <span className="font-semibold">
                          {uploadResult.duplicate_alerts?.length || 0}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Potential Savings</span>
                        <span className="font-semibold text-emerald-600">
                          {formatCurrency(uploadResult.total_potential_savings)}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>

        {/* Duplicate Alert Modal */}
        {currentAlerts.length === 1 && (
          <DuplicateAlert
            alert={currentAlerts[0]}
            onDecision={() => handleDuplicateComplete()}
            isOpen={showDuplicateAlert}
            onClose={() => setShowDuplicateAlert(false)}
          />
        )}

        {currentAlerts.length > 1 && (
          <MultiDuplicateAlert
            alerts={currentAlerts}
            onComplete={handleDuplicateComplete}
            isOpen={showDuplicateAlert}
            onClose={() => setShowDuplicateAlert(false)}
          />
        )}
      </div>
  );
}


