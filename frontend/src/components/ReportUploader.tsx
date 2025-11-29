"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Camera,
  FileImage,
  Loader2,
  CheckCircle2,
  X,
  FileText,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn, isValidFileType, isValidFileSize, formatCurrency } from "@/lib/utils";
import { uploadReport } from "@/lib/api";
import { UploadReportResponse } from "@/types";

interface ReportUploaderProps {
  userId: string;
  onUploadComplete?: (response: UploadReportResponse) => void;
  onError?: (error: string) => void;
}

export function ReportUploader({
  userId,
  onUploadComplete,
  onError,
}: ReportUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file
    if (!isValidFileType(file)) {
      setError("Please upload a JPEG, PNG, or PDF file");
      return;
    }

    if (!isValidFileSize(file)) {
      setError("File size must be less than 10MB");
      return;
    }

    setError(null);
    setSelectedFile(file);

    // Create preview for images
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "application/pdf": [".pdf"],
    },
    maxFiles: 1,
    noClick: true,  // Prevent double dialog - only use the Browse Files button
    noKeyboard: false,
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const response = await uploadReport(selectedFile, userId);
      clearInterval(progressInterval);
      setUploadProgress(100);

      // Short delay to show 100% progress
      setTimeout(() => {
        onUploadComplete?.(response);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to upload report";
      setError(errorMessage);
      onError?.(errorMessage);
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreview(null);
    setError(null);
    setUploadProgress(0);
  };

  return (
    <Card className="overflow-hidden border-2 border-dashed border-transparent">
      <CardContent className="p-0">
        <AnimatePresence mode="wait">
          {!selectedFile ? (
            // Drop zone
            <motion.div
              key="dropzone"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              {...getRootProps()}
              className={cn(
                "upload-zone flex flex-col items-center justify-center p-8 text-center",
                isDragActive && "upload-zone-active"
              )}
            >
              <input {...getInputProps()} />

              <div className="mb-4 rounded-full bg-primary/10 p-4">
                <Upload className="h-8 w-8 text-primary" />
              </div>

              <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                {isDragActive ? "Drop your report here" : "Upload Medical Report"}
              </h3>

              <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
                Drag and drop your report, or click the button below
              </p>

              <div className="flex flex-col gap-2 sm:flex-row">
                <Button type="button" onClick={open}>
                  <FileImage className="mr-2 h-4 w-4" />
                  Browse Files
                </Button>

                {/* Mobile camera capture */}
                <div className="sm:hidden">
                  <label htmlFor="camera-input">
                    <Button type="button" variant="outline" asChild>
                      <span>
                        <Camera className="mr-2 h-4 w-4" />
                        Take Photo
                      </span>
                    </Button>
                  </label>
                  <input
                    id="camera-input"
                    type="file"
                    accept="image/*"
                    capture="environment"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) onDrop([file]);
                    }}
                  />
                </div>
              </div>

              <p className="mt-4 text-xs text-gray-400">
                Supports JPEG, PNG, and PDF (max 10MB)
              </p>
            </motion.div>
          ) : (
            // File preview
            <motion.div
              key="preview"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="p-6"
            >
              <div className="mb-6 flex items-start justify-between">
                <div className="flex items-center gap-4">
                  {preview ? (
                    <div className="relative h-20 w-20 overflow-hidden rounded-lg border">
                      <img
                        src={preview}
                        alt="Preview"
                        className="h-full w-full object-cover"
                      />
                    </div>
                  ) : (
                    <div className="flex h-20 w-20 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-800">
                      <FileText className="h-8 w-8 text-gray-400" />
                    </div>
                  )}

                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                {!isUploading && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleRemoveFile}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>

              {/* Error message */}
              {error && (
                <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
                  <AlertCircle className="h-4 w-4" />
                  {error}
                </div>
              )}

              {/* Upload progress */}
              {isUploading && (
                <div className="mb-6">
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className="text-gray-500">
                      {uploadProgress < 100
                        ? "Analyzing report..."
                        : "Analysis complete!"}
                    </span>
                    <span className="font-medium">{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} className="h-2" />
                </div>
              )}

              {/* Actions */}
              {!isUploading ? (
                <div className="flex gap-3">
                  <Button onClick={handleUpload} className="flex-1">
                    <Upload className="mr-2 h-4 w-4" />
                    Analyze Report
                  </Button>
                  <Button variant="outline" onClick={handleRemoveFile}>
                    Cancel
                  </Button>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2 text-primary">
                  {uploadProgress < 100 ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>AI is reading your report...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="h-5 w-5" />
                      <span>Processing complete!</span>
                    </>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}


