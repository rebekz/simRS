"use client";

/**
 * Training Viewer Component for STORY-038
 *
 * Provides content viewer with:
 * - Video player/embed
 * - Document viewer (PDF)
 * - Interactive tutorial steps
 * - Progress tracking
 * - Next/Previous navigation
 * - Mark complete button
 */

import { useState, useEffect, useRef } from "react";
import {
  Play,
  Pause,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  Clock,
  BookOpen,
  FileText,
  Video,
  Monitor,
  Award,
  Maximize,
  Volume2,
  VolumeX,
  RotateCw,
  Download,
} from "lucide-react";

// Types
interface Lesson {
  id: number;
  module_id: number;
  title: string;
  description?: string;
  lesson_order: number;
  content_type: "video" | "document" | "interactive" | "quiz";
  content_url?: string;
  duration_minutes?: number;
  is_mandatory: boolean;
}

interface LessonProgress {
  lesson_id: number;
  status: "not_started" | "in_progress" | "completed";
  progress_percentage: number;
  time_spent_seconds: number;
  completed_at?: string;
  last_position?: number; // For videos, last position in seconds
}

interface QuizQuestion {
  id: number;
  question_text: string;
  question_type: "multiple_choice" | "true_false" | "short_answer";
  options?: string[];
  correct_answer?: string;
  explanation?: string;
}

interface TrainingViewerProps {
  moduleId: number;
  moduleTitle: string;
  onComplete?: () => void;
}

export function TrainingViewer({ moduleId, moduleTitle, onComplete }: TrainingViewerProps) {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(0);
  const [progress, setProgress] = useState<Record<number, LessonProgress>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, string>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadLessons();
  }, [moduleId]);

  const loadLessons = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");

      const response = await fetch(`/api/v1/training/modules/${moduleId}/lessons`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setLessons(data.lessons || []);

        // Load progress for each lesson
        const progressResponse = await fetch(
          `/api/v1/training/modules/${moduleId}/progress`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (progressResponse.ok) {
          const progressData = await progressResponse.json();
          const progressMap: Record<number, LessonProgress> = {};
          progressData.lessons_progress?.forEach((p: LessonProgress) => {
            progressMap[p.lesson_id] = p;
          });
          setProgress(progressMap);

          // Find first incomplete lesson
          const firstIncompleteIndex = data.lessons?.findIndex(
            (lesson: Lesson) =>
              !progressMap[lesson.id] || progressMap[lesson.id].status !== "completed"
          );
          if (firstIncompleteIndex >= 0) {
            setCurrentLessonIndex(firstIncompleteIndex);
          }
        }
      }
    } catch (error) {
      console.error("Failed to load lessons:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const currentLesson = lessons[currentLessonIndex];
  const currentProgress = currentLesson ? progress[currentLesson.id] : null;

  const updateProgress = async (lessonId: number, updates: Partial<LessonProgress>) => {
    try {
      const token = localStorage.getItem("token");

      await fetch(`/api/v1/training/lessons/${lessonId}/progress`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...updates,
          time_spent_seconds: (currentProgress?.time_spent_seconds || 0) + 1,
        }),
      });

      setProgress((prev) => ({
        ...prev,
        [lessonId]: {
          ...prev[lessonId],
          ...updates,
        },
      }));
    } catch (error) {
      console.error("Failed to update progress:", error);
    }
  };

  const markLessonComplete = async (lessonId: number) => {
    await updateProgress(lessonId, {
      status: "completed",
      progress_percentage: 100,
    });

    // Check if all lessons are completed
    const allCompleted = lessons.every(
      (lesson) => progress[lesson.id]?.status === "completed" || lesson.id === lessonId
    );

    if (allCompleted) {
      onComplete?.();
    }
  };

  const handlePrevious = () => {
    if (currentLessonIndex > 0) {
      setCurrentLessonIndex(currentLessonIndex - 1);
    }
  };

  const handleNext = async () => {
    if (currentLesson && currentProgress?.status === "completed") {
      if (currentLessonIndex < lessons.length - 1) {
        setCurrentLessonIndex(currentLessonIndex + 1);
      }
    } else if (currentLesson) {
      // Auto-mark as complete before moving to next
      await markLessonComplete(currentLesson.id);
      if (currentLessonIndex < lessons.length - 1) {
        setCurrentLessonIndex(currentLessonIndex + 1);
      }
    }
  };

  const handleVideoTimeUpdate = () => {
    if (videoRef.current && currentLesson) {
      const currentTime = videoRef.current.currentTime;
      const duration = videoRef.current.duration;

      if (duration > 0) {
        const progressPercent = (currentTime / duration) * 100;

        // Update progress every 5 seconds
        if (Math.floor(currentTime) % 5 === 0) {
          updateProgress(currentLesson.id, {
            progress_percentage: Math.round(progressPercent),
            last_position: Math.round(currentTime),
          });
        }

        // Auto-complete when 90% watched
        if (progressPercent >= 90 && currentProgress?.status !== "completed") {
          markLessonComplete(currentLesson.id);
        }
      }
    }
  };

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const toggleFullscreen = () => {
    if (containerRef.current) {
      if (!isFullscreen) {
        containerRef.current.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
      setIsFullscreen(!isFullscreen);
    }
  };

  const handleQuizAnswer = (questionId: number, answer: string) => {
    setQuizAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const submitQuiz = async () => {
    // Calculate score
    let correct = 0;
    const total = Object.keys(quizAnswers).length;
    correct = Object.values(quizAnswers).filter((answer) => answer === "correct").length;
    const score = total > 0 ? Math.round((correct / total) * 100) : 0;

    setQuizScore(score);
    setQuizSubmitted(true);

    // Mark lesson as complete if score >= 70%
    if (score >= 70 && currentLesson) {
      await markLessonComplete(currentLesson.id);
    }
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case "video":
        return <Video className="h-5 w-5" />;
      case "document":
        return <FileText className="h-5 w-5" />;
      case "interactive":
        return <Monitor className="h-5 w-5" />;
      case "quiz":
        return <BookOpen className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!currentLesson) {
    return (
      <div className="text-center py-12 text-gray-500">
        <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p>Tidak ada pelajaran dalam modul ini</p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-200px)]">
      {/* Sidebar - Lesson List */}
      {showSidebar && (
        <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-medium text-gray-900">Daftar Pelajaran</h3>
            <p className="text-sm text-gray-500 mt-1">{moduleTitle}</p>
          </div>
          <div className="divide-y divide-gray-200">
            {lessons.map((lesson, index) => {
              const lessonProgress = progress[lesson.id];
              const isActive = index === currentLessonIndex;

              return (
                <button
                  key={lesson.id}
                  onClick={() => setCurrentLessonIndex(index)}
                  className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                    isActive ? "bg-blue-50 border-l-4 border-blue-600" : ""
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {lessonProgress?.status === "completed" ? (
                        <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        </div>
                      ) : (
                        <div
                          className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-medium ${
                            isActive ? "border-blue-600 text-blue-600" : "border-gray-300 text-gray-500"
                          }`}
                        >
                          {index + 1}
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        {getContentTypeIcon(lesson.content_type)}
                        <p
                          className={`text-sm font-medium truncate ${
                            isActive ? "text-blue-600" : "text-gray-900"
                          }`}
                        >
                          {lesson.title}
                        </p>
                      </div>
                      {lesson.is_mandatory && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 mt-1">
                          Wajib
                        </span>
                      )}
                      {lessonProgress && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>{lessonProgress.progress_percentage}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className={`h-1.5 rounded-full ${
                                lessonProgress.status === "completed"
                                  ? "bg-green-600"
                                  : "bg-blue-600"
                              }`}
                              style={{ width: `${lessonProgress.progress_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6" ref={containerRef}>
          <div className="max-w-4xl mx-auto">
            {/* Lesson Header */}
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <span>Pelajaran {currentLessonIndex + 1} dari {lessons.length}</span>
                    {currentLesson.is_mandatory && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                        Wajib
                      </span>
                    )}
                  </div>
                  <h1 className="text-2xl font-bold text-gray-900 mt-2">
                    {currentLesson.title}
                  </h1>
                  {currentLesson.description && (
                    <p className="text-gray-600 mt-2">{currentLesson.description}</p>
                  )}
                </div>
                <button
                  onClick={() => setShowSidebar(!showSidebar)}
                  className="p-2 hover:bg-gray-200 rounded-lg"
                  title="Toggle Sidebar"
                >
                  <BookOpen className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Video Content */}
            {currentLesson.content_type === "video" && currentLesson.content_url && (
              <div className="bg-black rounded-lg overflow-hidden shadow-lg">
                <video
                  ref={videoRef}
                  className="w-full"
                  src={currentLesson.content_url}
                  onTimeUpdate={handleVideoTimeUpdate}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                />
                {/* Custom Controls */}
                <div className="bg-gray-900 p-4">
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={handlePlayPause}
                      className="text-white hover:text-gray-300"
                    >
                      {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
                    </button>
                    <button onClick={toggleMute} className="text-white hover:text-gray-300">
                      {isMuted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
                    </button>
                    <button
                      onClick={toggleFullscreen}
                      className="text-white hover:text-gray-300"
                    >
                      <Maximize className="h-5 w-5" />
                    </button>
                    <div className="flex-1">
                      <div className="w-full bg-gray-700 rounded-full h-1">
                        <div
                          className="bg-blue-600 h-1 rounded-full"
                          style={{
                            width: `${
                              videoRef.current
                                ? (videoRef.current.currentTime / videoRef.current.duration) * 100
                                : 0
                            }%`,
                          }}
                        ></div>
                      </div>
                    </div>
                    <span className="text-white text-sm">
                      {videoRef.current ? formatTime(videoRef.current.currentTime) : "0:00"} /{" "}
                      {videoRef.current ? formatTime(videoRef.current.duration) : "0:00"}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Document Content */}
            {currentLesson.content_type === "document" && currentLesson.content_url && (
              <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-gray-600" />
                    <span className="font-medium text-gray-900">Document Viewer</span>
                  </div>
                  <button
                    onClick={() => window.open(currentLesson.content_url, "_blank")}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </button>
                </div>
                <div className="p-4">
                  <iframe
                    src={currentLesson.content_url}
                    className="w-full h-[600px] border-0"
                    title={currentLesson.title}
                  />
                </div>
              </div>
            )}

            {/* Interactive Content */}
            {currentLesson.content_type === "interactive" && currentLesson.content_url && (
              <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center space-x-2">
                    <Monitor className="h-5 w-5 text-gray-600" />
                    <span className="font-medium text-gray-900">Interactive Content</span>
                  </div>
                </div>
                <div className="p-4">
                  <iframe
                    src={currentLesson.content_url}
                    className="w-full h-[600px] border-0"
                    title={currentLesson.title}
                  />
                </div>
              </div>
            )}

            {/* Quiz Content */}
            {currentLesson.content_type === "quiz" && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center space-x-2 mb-6">
                  <BookOpen className="h-6 w-6 text-blue-600" />
                  <h2 className="text-xl font-bold text-gray-900">Kuis</h2>
                </div>

                <div className="space-y-6">
                  {/* Sample quiz questions */}
                  {[
                    {
                      id: 1,
                      question: "Apa tujuan utama dari pelatihan ini?",
                      type: "multiple_choice" as const,
                      options: [
                        "Meningkatkan pemahaman",
                        "Memenuhi persyaratan",
                        "Mengembangkan keterampilan",
                        "Semua jawaban benar",
                      ],
                      correct: 3,
                    },
                    {
                      id: 2,
                      question: "Pelatihan ini wajib diikuti.",
                      type: "true_false" as const,
                      options: ["Benar", "Salah"],
                      correct: 0,
                    },
                  ].map((q) => (
                    <div key={q.id} className="border rounded-lg p-4">
                      <p className="font-medium text-gray-900 mb-3">
                        {q.id}. {q.question}
                      </p>
                      <div className="space-y-2">
                        {q.options.map((option, index) => (
                          <label
                            key={index}
                            className={`flex items-center p-3 border rounded-md cursor-pointer transition-colors ${
                              quizAnswers[q.id] === String(index)
                                ? "bg-blue-50 border-blue-600"
                                : "hover:bg-gray-50"
                            } ${
                              quizSubmitted && index === q.correct
                                ? "bg-green-50 border-green-600"
                                : ""
                            } ${
                              quizSubmitted &&
                              quizAnswers[q.id] === String(index) &&
                              index !== q.correct
                                ? "bg-red-50 border-red-600"
                                : ""
                            }`}
                          >
                            <input
                              type="radio"
                              name={`question-${q.id}`}
                              value={index}
                              checked={quizAnswers[q.id] === String(index)}
                              onChange={(e) => handleQuizAnswer(q.id, e.target.value)}
                              disabled={quizSubmitted}
                              className="mr-3"
                            />
                            <span>{option}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}

                  {quizSubmitted && (
                    <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded-md">
                      <div className="flex items-center space-x-2">
                        <Award className="h-5 w-5 text-blue-600" />
                        <p className="font-medium text-blue-900">
                          Skor Anda: {quizScore}%
                        </p>
                      </div>
                      <p className="text-sm text-blue-700 mt-1">
                        {quizScore >= 70
                          ? "Selamat! Anda lulus kuis ini."
                          : "Anda perlu mencoba lagi untuk lulus."}
                      </p>
                    </div>
                  )}

                  {!quizSubmitted ? (
                    <button
                      onClick={submitQuiz}
                      disabled={Object.keys(quizAnswers).length === 0}
                      className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Submit Kuis
                    </button>
                  ) : (
                    quizScore < 70 && (
                      <button
                        onClick={() => {
                          setQuizAnswers({});
                          setQuizSubmitted(false);
                          setQuizScore(0);
                        }}
                        className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-orange-600 hover:bg-orange-700"
                      >
                        <RotateCw className="h-4 w-4 mr-2" />
                        Coba Lagi
                      </button>
                    )
                  )}
                </div>
              </div>
            )}

            {/* Progress indicator */}
            {currentProgress && currentProgress.status !== "completed" && (
              <div className="mt-6 bg-white rounded-lg shadow p-4">
                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span>Progres Pelajaran Ini</span>
                  <span>{currentProgress.progress_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${currentProgress.progress_percentage}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Footer */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentLessonIndex === 0}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </button>

            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                Waktu terpakai:{" "}
                {currentProgress ? formatTime(currentProgress.time_spent_seconds) : "0:00"}
              </span>
            </div>

            <button
              onClick={handleNext}
              disabled={currentLessonIndex === lessons.length - 1}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {currentProgress?.status === "completed" ? "Next" : "Mark Complete & Next"}
              <ChevronRight className="h-4 w-4 ml-2" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
