'use client';

import { useState, useCallback } from 'react';
import Sidebar from '@/components/Sidebar';
import ChatArea from '@/components/ChatArea';
import ChatInput from '@/components/ChatInput';
import FileUpload from '@/components/FileUpload';
import { sendMessage } from '@/lib/api';
import type { Message } from '@/lib/types';

export default function Dashboard() {
  const [currentThreadId, setCurrentThreadId] = useState<string>('main');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputVal, setInputVal] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = useCallback(async () => {
    if (!inputVal.trim()) return;

    const userText = inputVal.trim();
    setInputVal('');

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: userText,
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      // In a real implementation we'd use sendMessageStream here.
      // Currently using the non-streaming sync fetch since backend lacks /chat/stream SSE.
      const res = await sendMessage(userText, currentThreadId);
      
      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: res.response,
        chart: res.chart,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, aiMsg]);
      setCurrentThreadId(res.thread_id);
    } catch (err: any) {
      const errMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `**Error:** ${err.message || 'Failed to connect to AI'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [inputVal, currentThreadId]);

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar 
        currentThreadId={currentThreadId} 
        onSelectThread={(id) => {
          setCurrentThreadId(id);
          // In real app, we'd fetch thread history here.
          // For now, we just clear current chat view to simulate a new thread.
          setMessages([]); 
        }} 
      />
      
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
        {/* Header */}
        <header style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          padding: '0 1.5rem',
          borderBottom: '1px solid rgba(68, 71, 77, 0.15)',
          background: 'var(--surface-container-low)'
        }}>
          <h1 className="label-upper" style={{ margin: 0 }}>
            {currentThreadId === 'main' ? 'Overview' : `Thread: ${currentThreadId.slice(0,8)}`}
          </h1>
          
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--outline)' }}>
              Model: Groq Llama 3
            </span>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--secondary)', boxShadow: '0 0 8px var(--secondary)' }} />
          </div>
        </header>

        {/* Dynamic content area */}
        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
          
          {/* Main Chat Area */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <ChatArea messages={messages} isTyping={isTyping} />
            </div>
            
            <div style={{ padding: '1.5rem', background: 'var(--surface-container-low)', borderTop: '1px solid rgba(68, 71, 77, 0.15)' }}>
              <ChatInput 
                value={inputVal}
                onChange={setInputVal}
                onSend={handleSend}
                loading={isTyping}
              />
            </div>
          </div>

          {/* Right Panel (File Upload & Context) */}
          <aside style={{ 
            width: 320, 
            borderLeft: '1px solid rgba(68, 71, 77, 0.15)',
            background: 'var(--surface-container)',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid rgba(68, 71, 77, 0.15)' }}>
              <h2 className="label-upper" style={{ marginBottom: '1rem' }}>Knowledge Base</h2>
              <FileUpload />
            </div>
            
            <div style={{ padding: '1.5rem', flex: 1, overflowY: 'auto' }}>
              <h2 className="label-upper" style={{ marginBottom: '1rem' }}>Context Engine</h2>
              <div className="card-high" style={{ padding: '1rem', fontSize: '0.8125rem', color: 'var(--on-surface-variant)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>Vector Search</span>
                  <span style={{ color: 'var(--secondary)' }}>Active</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>Live Market Data</span>
                  <span style={{ color: 'var(--secondary)' }}>Active</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Web Search</span>
                  <span style={{ color: 'var(--secondary)' }}>Active</span>
                </div>
              </div>
            </div>
          </aside>

        </div>
      </main>
    </div>
  );
}
