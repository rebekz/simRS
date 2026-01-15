"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Camera, X, RotateCw, Check } from "lucide-react";

/**
 * WEB-S-3.7: Camera Capture Component
 *
 * Key Features:
 * - Camera access for photo capture
 * - Mobile-friendly UI (375px breakpoint)
 * - Touch-friendly buttons (44x44px minimum)
 * - Camera switch (front/back)
 * - Photo preview and retake
 * - Base64 output for storage
 */

// ============================================================================
// TYPES
// ============================================================================

export interface CapturedPhoto {
  dataUrl: string;
  timestamp: Date;
}

interface CameraCaptureProps {
  onCapture: (photo: CapturedPhoto) => void;
  onCancel?: () => void;
  className?: string;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function CameraCapture({ onCapture, onCancel, className = "" }: CameraCaptureProps) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [facingMode, setFacingMode] = useState<"user" | "environment">("environment");
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  /**
   * Initialize camera
   */
  const startCamera = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Stop existing stream
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }

      // Request camera access
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      setStream(mediaStream);

      // Attach to video element
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }
    } catch (err) {
      console.error("Camera access error:", err);
      setError(
        "Tidak dapat mengakses kamera. Pastikan izin kamera diberikan."
      );
    } finally {
      setIsLoading(false);
    }
  }, [facingMode, stream]);

  /**
   * Stop camera
   */
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  }, [stream]);

  /**
   * Switch camera (front/back)
   */
  const switchCamera = useCallback(() => {
    setFacingMode((prev) => (prev === "user" ? "environment" : "user"));
  }, []);

  /**
   * Capture photo from video stream
   */
  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Mirror if using front camera
    if (facingMode === "user") {
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to data URL
    const dataUrl = canvas.toDataURL("image/jpeg", 0.85);

    setCapturedImage(dataUrl);
    stopCamera();
  }, [facingMode, stopCamera]);

  /**
   * Retake photo
   */
  const retakePhoto = useCallback(() => {
    setCapturedImage(null);
    startCamera();
  }, [startCamera]);

  /**
   * Confirm and send captured photo
   */
  const confirmPhoto = useCallback(() => {
    if (!capturedImage) return;

    onCapture({
      dataUrl: capturedImage,
      timestamp: new Date(),
    });
  }, [capturedImage, onCapture]);

  /**
   * Handle cancel
   */
  const handleCancel = useCallback(() => {
    stopCamera();
    onCancel?.();
  }, [stopCamera, onCancel]);

  // Start camera on mount
  useEffect(() => {
    startCamera();

    return () => {
      stopCamera();
    };
  }, [facingMode]); // Only restart on facing mode change

  // Restart camera when facing mode changes
  useEffect(() => {
    if (facingMode && !capturedImage) {
      startCamera();
    }
  }, [facingMode, capturedImage, startCamera]);

  return (
    <div className={`relative ${className}`}>
      {/* Camera Viewfinder */}
      <div className="relative bg-black rounded-xl overflow-hidden">
        {capturedImage ? (
          // Captured Image Preview
          <div className="relative">
            <img
              src={capturedImage}
              alt="Captured photo"
              className="w-full h-auto"
            />
          </div>
        ) : (
          // Live Camera Feed
          <div className="relative aspect-[4/3] md:aspect-[16/9]">
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                <div className="text-white text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-2"></div>
                  <p className="text-sm">Memuat kamera...</p>
                </div>
              </div>
            )}

            {error && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-900 p-4">
                <div className="text-center text-white">
                  <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            )}

            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover ${isLoading || error ? "hidden" : ""}`}
            />

            {/* Camera facing mode indicator */}
            {stream && !isLoading && !error && (
              <div className="absolute top-3 left-3">
                <span className="px-3 py-1 bg-black bg-opacity-50 text-white text-xs rounded-full">
                  {facingMode === "user" ? "Depan" : "Belakang"}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Hidden canvas for capture */}
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      {/* Controls - Mobile-optimized (min 44x44px) */}
      <div className="mt-4 flex items-center justify-center gap-3 md:gap-4">
        {!capturedImage ? (
          // Capture controls
          <>
            {/* Cancel button */}
            <button
              type="button"
              onClick={handleCancel}
              className="flex-shrink-0 w-12 h-12 md:w-14 md:h-14 min-w-[44px] min-h-[44px] flex items-center justify-center rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
              aria-label="Batal"
            >
              <X className="w-6 h-6 text-gray-700" />
            </button>

            {/* Capture button */}
            <button
              type="button"
              onClick={capturePhoto}
              disabled={!stream || isLoading}
              className="flex-shrink-0 w-16 h-16 md:w-20 md:h-20 min-w-[64px] min-h-[64px] flex items-center justify-center rounded-full bg-white hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed border-4 border-gray-300"
              aria-label="Ambil foto"
            >
              <Camera className="w-8 h-8 md:w-10 md:h-10 text-blue-600" />
            </button>

            {/* Switch camera button */}
            <button
              type="button"
              onClick={switchCamera}
              disabled={!stream || isLoading}
              className="flex-shrink-0 w-12 h-12 md:w-14 md:h-14 min-w-[44px] min-h-[44px] flex items-center justify-center rounded-full bg-gray-200 hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Ganti kamera"
            >
              <RotateCw className="w-6 h-6 text-gray-700" />
            </button>
          </>
        ) : (
          // Preview controls
          <>
            {/* Retake button */}
            <button
              type="button"
              onClick={retakePhoto}
              className="flex items-center gap-2 px-6 py-3 min-h-[44px] bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors font-medium"
            >
              <RotateCw className="w-5 h-5" />
              <span>Ulang</span>
            </button>

            {/* Confirm button */}
            <button
              type="button"
              onClick={confirmPhoto}
              className="flex items-center gap-2 px-6 py-3 min-h-[44px] bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
            >
              <Check className="w-5 h-5" />
              <span>Gunakan</span>
            </button>
          </>
        )}
      </div>

      {/* Instructions */}
      {!capturedImage && !error && (
        <p className="mt-3 text-center text-sm text-gray-600">
          Posisikan wajah pasien dalam frame
        </p>
      )}
    </div>
  );
}

/**
 * Photo thumbnail component for display in forms
 */
export interface PhotoThumbnailProps {
  photo: CapturedPhoto | string | null;
  onRemove?: () => void;
  onRetake?: () => void;
  className?: string;
}

export function PhotoThumbnail({
  photo,
  onRemove,
  onRetake,
  className = "",
}: PhotoThumbnailProps) {
  const dataUrl = typeof photo === "string" ? photo : photo?.dataUrl;

  if (!dataUrl) {
    return (
      <div
        className={`flex flex-col items-center justify-center bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 ${className}`}
      >
        <Camera className="w-8 h-8 text-gray-400 mb-2" />
        <p className="text-sm text-gray-500">Foto belum diambil</p>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <img
        src={dataUrl}
        alt="Patient photo"
        className="w-full h-auto rounded-lg border-2 border-gray-200"
      />

      {/* Actions overlay */}
      <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-30 transition-all rounded-lg flex items-center justify-center opacity-0 hover:opacity-100">
        <div className="flex gap-2">
          {onRetake && (
            <button
              type="button"
              onClick={onRetake}
              className="w-10 h-10 min-w-[40px] min-h-[40px] flex items-center justify-center rounded-full bg-white hover:bg-gray-100 transition-colors"
              aria-label="Foto ulang"
            >
              <RotateCw className="w-5 h-5 text-gray-700" />
            </button>
          )}
          {onRemove && (
            <button
              type="button"
              onClick={onRemove}
              className="w-10 h-10 min-w-[40px] min-h-[40px] flex items-center justify-center rounded-full bg-white hover:bg-gray-100 transition-colors"
              aria-label="Hapus foto"
            >
              <X className="w-5 h-5 text-gray-700" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
