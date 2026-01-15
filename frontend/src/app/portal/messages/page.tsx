"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface MessageAttachment {
  file_name: string;
  file_type: string;
  file_size: number;
  file_url: string;
}

interface MessageDetail {
  id: number;
  sender_type: "patient" | "provider";
  sender_name: string;
  content: string;
  attachments: MessageAttachment[];
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

interface MessageThread {
  id: number;
  subject: string;
  category: string;
  recipient_name: string;
  recipient_role: string;
  status: string;
  is_starred: boolean;
  is_archived: boolean;
  created_at: string;
  messages: MessageDetail[];
}

interface MessageThreadSummary {
  id: number;
  subject: string;
  category: string;
  recipient_name: string;
  last_message_preview: string;
  last_message_at: string | null;
  last_message_sender_type: string | null;
  status: string;
  is_starred: boolean;
  is_archived: boolean;
  unread_count: number;
  created_at: string;
}

interface SendMessageRequest {
  thread_id?: number;
  subject?: string;
  category: string;
  recipient_id?: number;
  recipient_name?: string;
  recipient_role?: string;
  content: string;
  attachments?: MessageAttachment[];
}

export default function MessagingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Thread list state
  const [threads, setThreads] = useState<MessageThreadSummary[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [selectedThread, setSelectedThread] = useState<MessageThread | null>(null);
  const [showArchived, setShowArchived] = useState(false);

  // Compose message state
  const [showCompose, setShowCompose] = useState(false);
  const [composeForm, setComposeForm] = useState<SendMessageRequest>({
    category: "other",
    content: "",
  });
  const [composeErrors, setComposeErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    checkAuth();
    fetchThreads();
    fetchUnreadCount();
  }, [showArchived]);

  const checkAuth = () => {
    const token = localStorage.getItem("portal_access_token");
    if (!token) {
      router.push("/portal/login");
    }
  };

  const getToken = () => {
    return localStorage.getItem("portal_access_token");
  };

  const fetchThreads = async () => {
    const token = getToken();
    if (!token) return;

    try {
      const response = await fetch(
        `/api/v1/portal/messages/threads?is_archived=${showArchived}&limit=50`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.status === 401) {
        router.push("/portal/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch message threads");
      }

      const data = await response.json();
      setThreads(data.threads || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load messages");
    } finally {
      setLoading(false);
    }
  };

  const fetchUnreadCount = async () => {
    const token = getToken();
    if (!token) return;

    try {
      const response = await fetch("/api/v1/portal/messages/unread-count", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.total_unread || 0);
      }
    } catch (err) {
      console.error("Failed to fetch unread count:", err);
    }
  };

  const fetchThreadDetail = async (threadId: number) => {
    const token = getToken();
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/messages/threads/${threadId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch thread details");
      }

      const data = await response.json();
      setSelectedThread(data);
      setShowCompose(false);

      // Refresh thread list to update unread counts
      fetchThreads();
      fetchUnreadCount();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load thread");
    }
  };

  const handleStarThread = async (threadId: number, isStarred: boolean) => {
    const token = getToken();
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/messages/threads/${threadId}/star`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ is_starred: !isStarred }),
      });

      if (!response.ok) {
        throw new Error("Failed to update thread");
      }

      fetchThreads();
      if (selectedThread?.id === threadId) {
        setSelectedThread({ ...selectedThread, is_starred: !isStarred });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to star thread");
    }
  };

  const handleArchiveThread = async (threadId: number, isArchived: boolean) => {
    const token = getToken();
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/portal/messages/threads/${threadId}/archive`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ is_archived: !isArchived }),
      });

      if (!response.ok) {
        throw new Error("Failed to archive thread");
      }

      fetchThreads();
      if (selectedThread?.id === threadId) {
        setSelectedThread(null);
      }
      setSuccessMessage(!isArchived ? "Thread archived" : "Thread unarchived");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to archive thread");
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage(null);

    // Validate form
    const errors: Record<string, string> = {};

    if (!composeForm.thread_id && !composeForm.subject) {
      errors.subject = "Subject is required for new messages";
    }

    if (!composeForm.content?.trim()) {
      errors.content = "Message content is required";
    }

    if (Object.keys(errors).length > 0) {
      setComposeErrors(errors);
      return;
    }

    setSending(true);
    setError(null);

    try {
      const token = getToken();
      const response = await fetch("/api/v1/portal/messages/send", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(composeForm),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to send message" }));
        throw new Error(errorData.detail || "Failed to send message");
      }

      const data = await response.json();

      // Clear form
      setComposeForm({ category: "other", content: "" });
      setComposeErrors({});

      setSuccessMessage("Message sent successfully!");
      setTimeout(() => setSuccessMessage(null), 3000);

      // If replying to existing thread, refresh it
      if (composeForm.thread_id && selectedThread) {
        fetchThreadDetail(selectedThread.id);
      } else {
        // New thread, go to it
        fetchThreadDetail(data.thread_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setSending(false);
    }
  };

  const handleReply = () => {
    if (!selectedThread) return;
    setShowCompose(true);
    setComposeForm({
      thread_id: selectedThread.id,
      category: selectedThread.category,
      content: "",
    });
  };

  const handleNewMessage = () => {
    setSelectedThread(null);
    setShowCompose(true);
    setComposeForm({
      category: "other",
      content: "",
    });
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "medical_question": return "bg-blue-100 text-blue-700";
      case "appointment_question": return "bg-green-100 text-green-700";
      case "billing_question": return "bg-yellow-100 text-yellow-700";
      case "prescription_question": return "bg-purple-100 text-purple-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case "medical_question": return "Medical";
      case "appointment_question": return "Appointment";
      case "billing_question": return "Billing";
      case "prescription_question": return "Prescription";
      default: return "Other";
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat("id-ID", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const formatShortDate = (dateStr: string | null) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return new Intl.DateTimeFormat("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
    } else if (diffDays === 1) {
      return "Yesterday";
    } else if (diffDays < 7) {
      return new Intl.DateTimeFormat("id-ID", { weekday: "short" }).format(date);
    } else {
      return new Intl.DateTimeFormat("id-ID", {
        day: "2-digit",
        month: "short",
      }).format(date);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading messages...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
              {unreadCount > 0 && (
                <p className="text-sm text-gray-600 mt-1">
                  {unreadCount} unread message{unreadCount > 1 ? "s" : ""}
                </p>
              )}
            </div>
            <button
              onClick={handleNewMessage}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
            >
              + New Message
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">{successMessage}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Thread List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">Inbox</h2>
                  <button
                    onClick={() => setShowArchived(!showArchived)}
                    className="text-sm text-indigo-600 hover:underline"
                  >
                    {showArchived ? "Show Active" : "Show Archived"}
                  </button>
                </div>
              </div>
              <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
                {threads.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    <p className="mt-2">No messages yet</p>
                    <button
                      onClick={handleNewMessage}
                      className="mt-4 text-indigo-600 hover:underline text-sm"
                    >
                      Send your first message
                    </button>
                  </div>
                ) : (
                  threads.map((thread) => (
                    <div
                      key={thread.id}
                      onClick={() => fetchThreadDetail(thread.id)}
                      className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                        selectedThread?.id === thread.id ? "bg-indigo-50 border-l-4 border-indigo-600" : ""
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            {thread.unread_count > 0 && (
                              <span className="flex-shrink-0 w-2 h-2 bg-indigo-600 rounded-full"></span>
                            )}
                            <h3 className={`text-sm font-medium truncate ${
                              thread.unread_count > 0 ? "text-gray-900" : "text-gray-600"
                            }`}>
                              {thread.subject}
                            </h3>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {thread.recipient_name}
                          </p>
                          <p className="text-xs text-gray-400 mt-1 truncate">
                            {thread.last_message_preview}
                          </p>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <span className="text-xs text-gray-400">
                            {formatShortDate(thread.last_message_at)}
                          </span>
                          <span className={`px-2 py-0.5 text-xs rounded-full ${getCategoryColor(thread.category)}`}>
                            {getCategoryLabel(thread.category)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Thread Detail / Compose */}
          <div className="lg:col-span-2">
            {!selectedThread && !showCompose && (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <h2 className="mt-4 text-lg font-medium text-gray-900">Select a conversation</h2>
                <p className="mt-2 text-sm text-gray-500">
                  Choose a thread from the left or start a new conversation
                </p>
                <button
                  onClick={handleNewMessage}
                  className="mt-6 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  + New Message
                </button>
              </div>
            )}

            {showCompose && (
              <div className="bg-white rounded-lg shadow-md">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">
                    {composeForm.thread_id ? "Reply to Thread" : "New Message"}
                  </h2>
                </div>
                <form onSubmit={handleSendMessage} className="p-6 space-y-4">
                  {!composeForm.thread_id && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Subject <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={composeForm.subject || ""}
                          onChange={(e) => {
                            setComposeForm({ ...composeForm, subject: e.target.value });
                            if (composeErrors.subject) {
                              setComposeErrors({ ...composeErrors, subject: "" });
                            }
                          }}
                          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                            composeErrors.subject ? "border-red-300" : "border-gray-300"
                          }`}
                          placeholder="Message subject"
                        />
                        {composeErrors.subject && (
                          <p className="mt-1 text-sm text-red-600">{composeErrors.subject}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Category
                        </label>
                        <select
                          value={composeForm.category}
                          onChange={(e) => setComposeForm({ ...composeForm, category: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        >
                          <option value="medical_question">Medical Question</option>
                          <option value="appointment_question">Appointment Question</option>
                          <option value="billing_question">Billing Question</option>
                          <option value="prescription_question">Prescription Question</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                    </>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Message <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={composeForm.content}
                      onChange={(e) => {
                        setComposeForm({ ...composeForm, content: e.target.value });
                        if (composeErrors.content) {
                          setComposeErrors({ ...composeErrors, content: "" });
                        }
                      }}
                      rows={6}
                      className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                        composeErrors.content ? "border-red-300" : "border-gray-300"
                      }`}
                      placeholder="Type your message..."
                    />
                    {composeErrors.content && (
                      <p className="mt-1 text-sm text-red-600">{composeErrors.content}</p>
                    )}
                  </div>

                  <div className="flex gap-3">
                    <button
                      type="submit"
                      disabled={sending || !composeForm.content.trim()}
                      className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
                    >
                      {sending ? "Sending..." : "Send Message"}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowCompose(false);
                        setComposeForm({ category: "other", content: "" });
                        setComposeErrors({});
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {selectedThread && !showCompose && (
              <div className="bg-white rounded-lg shadow-md">
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h2 className="text-lg font-semibold text-gray-900">{selectedThread.subject}</h2>
                      <div className="flex items-center gap-2 mt-2">
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getCategoryColor(selectedThread.category)}`}>
                          {getCategoryLabel(selectedThread.category)}
                        </span>
                        <span className="text-sm text-gray-500">
                          with {selectedThread.recipient_name}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleStarThread(selectedThread.id, selectedThread.is_starred)}
                        className={`p-2 rounded-lg hover:bg-gray-100 ${
                          selectedThread.is_starred ? "text-yellow-500" : "text-gray-400"
                        }`}
                      >
                        <svg className="w-5 h-5" fill={selectedThread.is_starred ? "currentColor" : "none"} viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleArchiveThread(selectedThread.id, selectedThread.is_archived)}
                        className="p-2 rounded-lg hover:bg-gray-100 text-gray-400"
                      >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                <div className="p-6 space-y-4 max-h-[500px] overflow-y-auto">
                  {selectedThread.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender_type === "patient" ? "justify-end" : "justify-start"}`}
                    >
                      <div className={`max-w-[70%] rounded-lg p-4 ${
                        message.sender_type === "patient"
                          ? "bg-indigo-600 text-white"
                          : "bg-gray-100 text-gray-900"
                      }`}>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm font-medium">{message.sender_name}</span>
                          <span className={`text-xs ${
                            message.sender_type === "patient" ? "text-indigo-200" : "text-gray-500"
                          }`}>
                            {formatDate(message.created_at)}
                          </span>
                        </div>
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        {message.attachments && message.attachments.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {message.attachments.map((attachment, idx) => (
                              <a
                                key={idx}
                                href={attachment.file_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`flex items-center gap-2 text-sm ${
                                  message.sender_type === "patient"
                                    ? "text-indigo-200 hover:text-white"
                                    : "text-indigo-600 hover:text-indigo-700"
                                }`}
                              >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                                </svg>
                                {attachment.file_name}
                              </a>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="p-6 border-t border-gray-200">
                  <button
                    onClick={handleReply}
                    className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
                  >
                    Reply
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
