'use client';

import { useCallback, useEffect, useState } from 'react';

import ChatArea from '@/components/ChatArea';
import ChatInput from '@/components/ChatInput';
import FileUpload from '@/components/FileUpload';
import Sidebar from '@/components/Sidebar';
import {
  clearAuthToken,
  getCurrentUser,
  getThreadHistory,
  hasAuthToken,
  login,
  sendMessage,
} from '@/lib/api';
import { createId } from '@/lib/id';
import type { AuthUser, Message } from '@/lib/types';

export default function Dashboard() {
  const [currentThreadId, setCurrentThreadId] = useState<string>('main');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputVal, setInputVal] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const loadThread = useCallback(async (threadId: string) => {
    if (!user) {
      setMessages([]);
      return;
    }

    try {
      const history = await getThreadHistory(threadId);
      const mappedMessages: Message[] = history.messages.map((message, index) => ({
        id: `${threadId}-${index}-${createId()}`,
        role: message.role === 'human' ? 'user' : 'assistant',
        content: message.content,
        timestamp: new Date(),
      }));
      setMessages(mappedMessages);
    } catch (error) {
      console.error(`Failed to load history for thread ${threadId}`, error);
      setMessages([
        {
          id: createId(),
          role: 'assistant',
          content:
            error instanceof Error
              ? `Error loading thread history: ${error.message}`
              : 'Error loading thread history.',
          timestamp: new Date(),
        },
      ]);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      void loadThread(currentThreadId);
    }
  }, [currentThreadId, loadThread, user]);

  useEffect(() => {
    async function bootstrapAuth() {
      if (!hasAuthToken()) {
        setAuthLoading(false);
        return;
      }

      try {
        const me = await getCurrentUser();
        setUser(me);
      } catch (error) {
        console.error('Failed to restore auth session', error);
        clearAuthToken();
      } finally {
        setAuthLoading(false);
      }
    }

    void bootstrapAuth();
  }, []);

  const handleLogin = useCallback(async () => {
    if (!username.trim() || !password.trim()) {
      setAuthError('Enter both username and password.');
      return;
    }

    setIsLoggingIn(true);
    setAuthError(null);

    try {
      await login(username.trim(), password);
      const me = await getCurrentUser();
      setUser(me);
      setPassword('');
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Login failed');
    } finally {
      setIsLoggingIn(false);
      setAuthLoading(false);
    }
  }, [password, username]);

  const handleLogout = useCallback(() => {
    clearAuthToken();
    setUser(null);
    setMessages([]);
    setCurrentThreadId('main');
    setAuthError(null);
  }, []);

  const handleSend = useCallback(async () => {
    if (!inputVal.trim()) return;

    const userText = inputVal.trim();
    setInputVal('');

    const userMsg: Message = {
      id: createId(),
      role: 'user',
      content: userText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const res = await sendMessage(userText, currentThreadId);

      const aiMsg: Message = {
        id: createId(),
        role: 'assistant',
        content: res.response,
        chart: res.chart,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMsg]);
      setCurrentThreadId(res.thread_id);
    } catch (error) {
      const errMsg: Message = {
        id: createId(),
        role: 'assistant',
        content: `Error: ${
          error instanceof Error ? error.message : 'Failed to connect to AI'
        }`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [currentThreadId, inputVal]);

  if (authLoading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
          background: 'var(--surface)',
          color: 'var(--on-surface)',
        }}
      >
        Restoring your session...
      </div>
    );
  }

  if (!user) {
    return (
      <main
        style={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
          padding: '2rem',
          background:
            'radial-gradient(circle at top, rgba(39, 174, 96, 0.14), transparent 38%), var(--surface)',
        }}
      >
        <section
          className="card-high"
          style={{
            width: 'min(420px, 100%)',
            padding: '2rem',
            borderRadius: '1.5rem',
            display: 'grid',
            gap: '1rem',
          }}
        >
          <div>
            <p className="label-upper" style={{ marginBottom: '0.75rem' }}>
              Secure Login
            </p>
            <h1 style={{ margin: 0, fontSize: '2rem' }}>Sign in to CFOBuddy</h1>
            <p style={{ color: 'var(--on-surface-variant)', marginTop: '0.75rem' }}>
              JWT auth is now enabled. Use the backend credentials configured in your
              environment.
            </p>
          </div>

          <label style={{ display: 'grid', gap: '0.4rem' }}>
            <span className="label-upper">Username</span>
            <input
              className="input-field"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
            />
          </label>

          <label style={{ display: 'grid', gap: '0.4rem' }}>
            <span className="label-upper">Password</span>
            <input
              className="input-field"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !isLoggingIn) {
                  void handleLogin();
                }
              }}
              autoComplete="current-password"
            />
          </label>

          {authError ? (
            <p style={{ color: '#d64545', margin: 0 }}>{authError}</p>
          ) : null}

          <button
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
            onClick={() => void handleLogin()}
            disabled={isLoggingIn}
          >
            {isLoggingIn ? 'Signing in...' : 'Sign In'}
          </button>
        </section>
      </main>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar
        currentThreadId={currentThreadId}
        onSelectThread={(id) => setCurrentThreadId(id)}
        userName={user.username}
        userRole={user.auth_type === 'jwt' ? 'JWT Session' : 'Legacy API Key'}
      />

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
        <header
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 1.5rem',
            borderBottom: '1px solid rgba(68, 71, 77, 0.15)',
            background: 'var(--surface-container-low)',
          }}
        >
          <h1 className="label-upper" style={{ margin: 0 }}>
            {currentThreadId === 'main' ? 'Overview' : `Thread: ${currentThreadId.slice(0, 8)}`}
          </h1>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--outline)' }}>
              Signed in as {user.username}
            </span>
            <button className="btn btn-ghost btn-sm" onClick={handleLogout}>
              Sign Out
            </button>
          </div>
        </header>

        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <ChatArea messages={messages} isTyping={isTyping} />
            </div>

            <div
              style={{
                padding: '1.5rem',
                background: 'var(--surface-container-low)',
                borderTop: '1px solid rgba(68, 71, 77, 0.15)',
              }}
            >
              <ChatInput
                value={inputVal}
                onChange={setInputVal}
                onSend={handleSend}
                loading={isTyping}
              />
            </div>
          </div>

          <aside
            style={{
              width: 320,
              borderLeft: '1px solid rgba(68, 71, 77, 0.15)',
              background: 'var(--surface-container)',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div style={{ padding: '1.5rem', borderBottom: '1px solid rgba(68, 71, 77, 0.15)' }}>
              <h2 className="label-upper" style={{ marginBottom: '1rem' }}>
                Knowledge Base
              </h2>
              <FileUpload />
            </div>

            <div style={{ padding: '1.5rem', flex: 1, overflowY: 'auto' }}>
              <h2 className="label-upper" style={{ marginBottom: '1rem' }}>
                Context Engine
              </h2>
              <div
                className="card-high"
                style={{ padding: '1rem', fontSize: '0.8125rem', color: 'var(--on-surface-variant)' }}
              >
                <div
                  style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}
                >
                  <span>Vector Search</span>
                  <span style={{ color: 'var(--secondary)' }}>Active</span>
                </div>
                <div
                  style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}
                >
                  <span>Live Market Data</span>
                  <span style={{ color: 'var(--secondary)' }}>Active</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Reranker</span>
                  <span style={{ color: 'var(--secondary)' }}>Ready</span>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
