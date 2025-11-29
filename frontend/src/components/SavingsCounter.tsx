"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { IndianRupee, TrendingUp, Award, ChevronDown } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn, formatCurrency } from "@/lib/utils";
import { SavingsBreakdown } from "@/types";

interface SavingsCounterProps {
  totalSavings: number;
  testsSkipped: number;
  breakdown?: SavingsBreakdown[];
  animated?: boolean;
}

export function SavingsCounter({
  totalSavings,
  testsSkipped,
  breakdown = [],
  animated = true,
}: SavingsCounterProps) {
  const [displayValue, setDisplayValue] = useState(animated ? 0 : totalSavings);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    if (!animated) {
      setDisplayValue(totalSavings);
      return;
    }

    const duration = 1500; // ms
    const startTime = performance.now();
    const startValue = displayValue;
    const endValue = totalSavings;

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease-out-expo)
      const easeOutExpo = 1 - Math.pow(2, -10 * progress);
      
      const currentValue = Math.round(
        startValue + (endValue - startValue) * easeOutExpo
      );
      
      setDisplayValue(currentValue);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [totalSavings, animated]);

  if (totalSavings === 0) {
    return (
      <Card className="border-dashed">
        <CardContent className="p-6 text-center">
          <div className="mb-3 inline-flex rounded-full bg-gray-100 p-3 dark:bg-gray-800">
            <IndianRupee className="h-6 w-6 text-gray-400" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white">
            No Savings Yet
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Upload reports to detect duplicates and save money!
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="mb-1 flex items-center gap-2">
              <span className="text-sm font-medium text-emerald-100">
                Total Savings
              </span>
              {testsSkipped > 0 && (
                <Badge className="bg-white/20 text-white hover:bg-white/30">
                  {testsSkipped} tests skipped
                </Badge>
              )}
            </div>
            
            <motion.div
              key={displayValue}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-baseline gap-1"
            >
              <span className="text-4xl font-bold sm:text-5xl">
                ₹{displayValue.toLocaleString("en-IN")}
              </span>
            </motion.div>
          </div>

          <div className="rounded-full bg-white/20 p-4">
            <TrendingUp className="h-8 w-8" />
          </div>
        </div>

        {/* Breakdown */}
        {breakdown.length > 0 && (
          <div className="mt-4">
            <button
              onClick={() => setShowBreakdown(!showBreakdown)}
              className="flex w-full items-center justify-between rounded-lg bg-white/10 px-3 py-2 text-sm hover:bg-white/20"
            >
              <span>View breakdown</span>
              <ChevronDown
                className={cn(
                  "h-4 w-4 transition-transform",
                  showBreakdown && "rotate-180"
                )}
              />
            </button>

            {showBreakdown && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="mt-2 space-y-2"
              >
                {breakdown.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between rounded-lg bg-white/10 px-3 py-2 text-sm"
                  >
                    <span>{item.test_name}</span>
                    <span className="font-semibold">
                      {formatCurrency(item.amount_saved)}
                    </span>
                  </div>
                ))}
              </motion.div>
            )}
          </div>
        )}

        {/* Achievement badge */}
        {testsSkipped >= 3 && (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2">
            <Award className="h-5 w-5 text-yellow-300" />
            <span className="text-sm">Smart Saver! You're making great choices.</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Compact version for headers/sticky elements
export function SavingsCounterCompact({
  totalSavings,
  testsSkipped,
}: {
  totalSavings: number;
  testsSkipped: number;
}) {
  if (totalSavings === 0) return null;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="savings-badge cursor-help">
            <IndianRupee className="h-4 w-4" />
            <span>{formatCurrency(totalSavings)} saved</span>
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>
            {testsSkipped} duplicate test(s) skipped, saving you money!
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}


