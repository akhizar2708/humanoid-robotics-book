import React, { useState, useEffect } from 'react';
import styles from './ChatbotWidget.module.css';

interface Citation {
  module: string;
  chapter: string;
  page_url: string;
}

interface QueryResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
  session_id: string;
}

interface ChatMessage {
  message: string;
  sender: 'user' | 'bot';
  citations?: Citation[];
}

// Use globalThis to safely access environment variables in Docusaurus
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    // @ts-ignore - Docusaurus injects this at build time
    return window.REACT_APP_API_URL || 'http://localhost:8000';
  }
  return 'http://localhost:8000';
};

export const ChatbotWidget: React.FC = () => {
  const API_URL = getApiUrl();
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      message: "Hello! I'm your AI assistant for the Humanoid Robotics book. Ask me anything!",
      sender: 'bot',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [selectedText, setSelectedText] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  // Only run on client side
  useEffect(() => {
    setIsMounted(true);
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  // Handle text selection - only on client
  useEffect(() => {
    if (!isMounted) return;

    const handleSelection = () => {
      try {
        const selection = window.getSelection();
        const text = selection?.toString().trim();
        if (text && text.length > 0) {
          setSelectedText(text);
        }
      } catch (err) {
        console.error('Selection error:', err);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('touchend', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('touchend', handleSelection);
    };
  }, [isMounted]);

  const sendQuery = async (query: string, queryScope: 'global' | 'selected' = 'global') => {
    if (!sessionId) {
      setError('Session not initialized. Please refresh the page.');
      return;
    }

    setIsTyping(true);
    setError(null);

    // Add user message
    setMessages((prev) => [...prev, { message: query, sender: 'user' }]);
    setInputValue('');

    try {
      const requestBody = {
        query,
        session_id: sessionId,
        query_scope: queryScope,
        ...(queryScope === 'selected' && selectedText ? { selected_text: selectedText } : {}),
      };

      const response = await fetch(`${API_URL}/api/v1/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: QueryResponse = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          message: data.answer,
          sender: 'bot',
          citations: data.citations,
        },
      ]);

      if (queryScope === 'selected') {
        setSelectedText('');
      }
    } catch (err) {
      console.error('Error sending query:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);
      setMessages((prev) => [
        ...prev,
        {
          message: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
          sender: 'bot',
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = () => {
    const query = inputValue.trim();
    if (!query) return;

    if (selectedText) {
      sendQuery(query, 'selected');
    } else {
      sendQuery(query, 'global');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isMounted) {
    return null;
  }

  return (
    <div className={styles.chatbotContainer}>
      {isExpanded ? (
        <div className={styles.chatbotExpanded}>
          <div className={styles.chatHeader}>
            <h3>AI Book Assistant</h3>
            <button
              className={styles.minimizeButton}
              onClick={() => setIsExpanded(false)}
              aria-label="Minimize chat"
            >
              &#8722;
            </button>
          </div>

          <div className={styles.messagesContainer}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`${styles.message} ${
                  msg.sender === 'user' ? styles.userMessage : styles.botMessage
                }`}
              >
                <div className={styles.messageContent}>{msg.message}</div>
                {msg.citations && msg.citations.length > 0 && (
                  <div className={styles.citations}>
                    <strong>Sources:</strong>
                    {msg.citations.map((citation, citIdx) => (
                      <a
                        key={citIdx}
                        href={citation.page_url}
                        className={styles.citationLink}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {citation.module} - {citation.chapter}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {isTyping && (
              <div className={`${styles.message} ${styles.botMessage}`}>
                <div className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>

          {selectedText && (
            <div className={styles.selectedTextBanner}>
              Selected text: "{selectedText.substring(0, 50)}..."
            </div>
          )}

          {error && <div className={styles.errorBanner}>{error}</div>}

          <div className={styles.inputContainer}>
            <textarea
              className={styles.input}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              rows={2}
            />
            <button
              className={styles.sendButton}
              onClick={handleSend}
              disabled={!inputValue.trim() || isTyping}
            >
              Send
            </button>
          </div>
        </div>
      ) : (
        <button
          className={styles.chatbotButton}
          onClick={() => setIsExpanded(true)}
          aria-label="Open chat"
        >
          💬
        </button>
      )}
    </div>
  );
};
