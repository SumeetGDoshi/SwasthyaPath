"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  IndianRupee,
  Calendar,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Clock,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn, formatCurrency, formatDate, daysAgo } from "@/lib/utils";
import { DuplicateAlert as DuplicateAlertType, DuplicateDecision } from "@/types";
import { updateDuplicateDecision } from "@/lib/api";

interface DuplicateAlertProps {
  alert: DuplicateAlertType;
  onDecision: (decision: DuplicateDecision) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function DuplicateAlert({
  alert,
  onDecision,
  isOpen,
  onClose,
}: DuplicateAlertProps) {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleDecision = async (decision: DuplicateDecision) => {
    setIsProcessing(true);
    try {
      await updateDuplicateDecision(alert.id, decision);
      onDecision(decision);
      onClose();
    } catch (error) {
      console.error("Failed to update decision:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900/30">
            <AlertTriangle className="h-8 w-8 text-amber-600 dark:text-amber-400" />
          </div>
          <DialogTitle className="text-center text-xl">
            Duplicate Test Detected!
          </DialogTitle>
          <DialogDescription className="text-center">
            You may not need to repeat this test
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Test info */}
          <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-lg font-semibold text-gray-900 dark:text-white">
                {alert.new_test_name}
              </span>
              <Badge variant="warning">Potential Duplicate</Badge>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Calendar className="h-4 w-4" />
                <span>
                  Last done: {formatDate(alert.original_test_date)}
                </span>
              </div>
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Clock className="h-4 w-4" />
                <span>{alert.days_since_original} days ago</span>
              </div>
            </div>
          </div>

          {/* Savings highlight */}
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 p-4 text-white"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Potential Savings</p>
                <p className="text-3xl font-bold">
                  {formatCurrency(alert.savings_amount)}
                </p>
              </div>
              <div className="rounded-full bg-white/20 p-3">
                <IndianRupee className="h-8 w-8" />
              </div>
            </div>
          </motion.div>

          {/* Alert message */}
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {alert.alert_message}
          </p>
        </div>

        <DialogFooter className="flex-col gap-2 sm:flex-row">
          <Button
            variant="savings"
            className="flex-1"
            onClick={() => handleDecision("skip")}
            disabled={isProcessing}
          >
            <CheckCircle2 className="mr-2 h-4 w-4" />
            Skip Test & Save {formatCurrency(alert.savings_amount)}
          </Button>
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => handleDecision("proceed")}
            disabled={isProcessing}
          >
            Proceed Anyway
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Multi-alert modal for when multiple duplicates are detected
interface MultiDuplicateAlertProps {
  alerts: DuplicateAlertType[];
  onComplete: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export function MultiDuplicateAlert({
  alerts,
  onComplete,
  isOpen,
  onClose,
}: MultiDuplicateAlertProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [decisions, setDecisions] = useState<Record<string, DuplicateDecision>>({});

  const totalSavings = alerts.reduce((sum, alert) => sum + alert.savings_amount, 0);
  const currentAlert = alerts[currentIndex];

  const handleDecision = async (decision: DuplicateDecision) => {
    setDecisions((prev) => ({ ...prev, [currentAlert.id]: decision }));

    try {
      await updateDuplicateDecision(currentAlert.id, decision);
    } catch (error) {
      console.error("Failed to update decision:", error);
    }

    if (currentIndex < alerts.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      onComplete();
      onClose();
    }
  };

  if (!currentAlert) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <div className="mb-2 flex items-center justify-between">
            <Badge variant="outline">
              {currentIndex + 1} of {alerts.length}
            </Badge>
            <Badge variant="savings">
              Total Savings: {formatCurrency(totalSavings)}
            </Badge>
          </div>
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900/30">
            <AlertTriangle className="h-8 w-8 text-amber-600 dark:text-amber-400" />
          </div>
          <DialogTitle className="text-center text-xl">
            Duplicate Tests Found!
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-lg font-semibold">
                {currentAlert.new_test_name}
              </span>
              <Badge variant="warning">Duplicate</Badge>
            </div>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span>Last done: {formatDate(currentAlert.original_test_date)}</span>
              </div>
              <div className="flex items-center gap-2">
                <IndianRupee className="h-4 w-4" />
                <span>Save: {formatCurrency(currentAlert.savings_amount)}</span>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter className="flex-col gap-2 sm:flex-row">
          <Button
            variant="savings"
            className="flex-1"
            onClick={() => handleDecision("skip")}
          >
            Skip & Save
          </Button>
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => handleDecision("proceed")}
          >
            Proceed
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}


