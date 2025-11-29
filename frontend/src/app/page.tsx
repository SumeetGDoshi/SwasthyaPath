"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  FileText,
  AlertTriangle,
  IndianRupee,
  Clock,
  ArrowRight,
  Sparkles,
  Shield,
  Zap,
  CheckCircle2,
  LayoutDashboard,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";

export default function HomePage() {
  const { user } = useAuth();

  const features = [
    {
      icon: <FileText className="h-6 w-6" />,
      title: "AI Report Analysis",
      description:
        "Upload any medical report and our AI extracts all test results instantly",
      color: "text-blue-500",
      bg: "bg-blue-50 dark:bg-blue-950",
    },
    {
      icon: <AlertTriangle className="h-6 w-6" />,
      title: "Duplicate Detection",
      description:
        "Automatically detects if you're repeating tests unnecessarily",
      color: "text-amber-500",
      bg: "bg-amber-50 dark:bg-amber-950",
    },
    {
      icon: <IndianRupee className="h-6 w-6" />,
      title: "Cost Savings",
      description:
        "See exactly how much money you save by avoiding duplicate tests",
      color: "text-emerald-500",
      bg: "bg-emerald-50 dark:bg-emerald-950",
    },
    {
      icon: <Clock className="h-6 w-6" />,
      title: "Health Timeline",
      description:
        "Track all your medical tests in a beautiful chronological view",
      color: "text-purple-500",
      bg: "bg-purple-50 dark:bg-purple-950",
    },
  ];

  const stats = [
    { value: "₹2,100+", label: "Average Savings" },
    { value: "95%", label: "Accuracy" },
    { value: "<5s", label: "Analysis Time" },
    { value: "100+", label: "Tests Supported" },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 py-20 sm:px-6 lg:px-8">
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-emerald-200/40 to-cyan-200/40 blur-3xl" />
          <div className="absolute right-0 bottom-0 h-[400px] w-[400px] rounded-full bg-gradient-to-br from-emerald-200/30 to-teal-200/30 blur-3xl" />
        </div>

        <div className="mx-auto max-w-6xl">
          {/* Top Navigation */}
          <div className="absolute top-4 right-4 sm:top-8 sm:right-8 flex gap-2">
            <span className="py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">
              Hi, {user?.name}
            </span>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            {/* Badge */}
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-4 py-2 text-sm font-medium text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
              <Sparkles className="h-4 w-4" />
              <span>AI-Powered Healthcare Intelligence</span>
            </div>

            {/* Main heading */}
            <h1 className="mb-6 text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl md:text-6xl">
              Stop Repeating{" "}
              <span className="bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
                Unnecessary Tests
              </span>
            </h1>

            <p className="mx-auto mb-8 max-w-2xl text-lg text-gray-600 dark:text-gray-300 sm:text-xl">
              Upload your medical reports and let AI detect duplicate tests,
              saving you money and time. Built for Indian healthcare.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link href="/upload">
                <Button size="xl" className="group">
                  Upload Report
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <Link href="/timeline">
                <Button variant="outline" size="xl">
                  <LayoutDashboard className="mr-2 h-5 w-5" />
                  View Dashboard
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-16 grid grid-cols-2 gap-4 sm:grid-cols-4"
          >
            {stats.map((stat, index) => (
              <div
                key={stat.label}
                className="rounded-xl bg-white/60 p-4 text-center shadow-sm backdrop-blur-sm dark:bg-gray-800/60"
              >
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 sm:text-3xl">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold text-gray-900 dark:text-white">
              How It Works
            </h2>
            <p className="mx-auto max-w-2xl text-gray-600 dark:text-gray-400">
              Three simple steps to smarter healthcare management
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="h-full card-hover border-0 shadow-md">
                  <CardContent className="p-6">
                    <div
                      className={`mb-4 inline-flex rounded-xl p-3 ${feature.bg}`}
                    >
                      <div className={feature.color}>{feature.icon}</div>
                    </div>
                    <h3 className="mb-2 font-semibold text-gray-900 dark:text-white">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-emerald-50/50 px-4 py-20 dark:bg-emerald-950/20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div>
              <h2 className="mb-6 text-3xl font-bold text-gray-900 dark:text-white">
                Save Money on Healthcare
              </h2>
              <p className="mb-8 text-gray-600 dark:text-gray-400">
                Indians spend thousands of rupees every year on unnecessary
                repeat tests. Our AI helps you identify when a previous test
                result is still valid.
              </p>

              <div className="space-y-4">
                {[
                  "Automatic validity period checking",
                  "Real-time cost savings calculation",
                  "Support for 100+ medical tests",
                  "Works with all major Indian labs",
                ].map((benefit) => (
                  <div key={benefit} className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                    <span className="text-gray-700 dark:text-gray-300">
                      {benefit}
                    </span>
                  </div>
                ))}
              </div>

              <Link href="/upload" className="mt-8 inline-block">
                <Button variant="savings" size="lg">
                  Start Saving Now
                  <IndianRupee className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>

            <div className="relative">
              <div className="rounded-2xl bg-white p-8 shadow-xl dark:bg-gray-800">
                <div className="mb-4 flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-500">
                    Your Savings
                  </span>
                  <Shield className="h-5 w-5 text-emerald-500" />
                </div>
                <div className="mb-6 text-4xl font-bold text-emerald-600">
                  ₹2,100
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">HbA1c (skipped)</span>
                    <span className="font-medium text-emerald-600">₹700</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Lipid Profile (skipped)</span>
                    <span className="font-medium text-emerald-600">₹1,000</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Thyroid Panel (skipped)</span>
                    <span className="font-medium text-emerald-600">₹400</span>
                  </div>
                </div>
              </div>
              <div className="absolute -right-4 -top-4 rounded-full bg-emerald-500 px-4 py-2 text-sm font-bold text-white shadow-lg">
                3 tests skipped!
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <Card className="overflow-hidden border-0 bg-gradient-to-r from-emerald-500 to-teal-500 shadow-2xl">
            <CardContent className="p-8 text-center sm:p-12">
              <Zap className="mx-auto mb-4 h-12 w-12 text-white" />
              <h2 className="mb-4 text-2xl font-bold text-white sm:text-3xl">
                Ready to Start Saving?
              </h2>
              <p className="mx-auto mb-8 max-w-lg text-emerald-100">
                Upload your first medical report and see the magic happen.
                It takes less than 5 seconds.
              </p>
              <Link href="/upload">
                <Button
                  size="xl"
                  variant="secondary"
                  className="bg-white text-emerald-600 hover:bg-gray-100"
                >
                  Upload Your Report
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl text-center text-sm text-gray-500">
          <p>
            Built for the Indian Healthcare Hackathon 2024 •{" "}
            <span className="font-medium text-emerald-600">Swasthya Path</span>
          </p>
        </div>
      </footer>
    </div>
  );
}


