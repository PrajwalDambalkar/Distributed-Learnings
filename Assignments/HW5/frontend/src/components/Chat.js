import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendMessage, fetchMessages, clearMessages } from '../store/chatSlice';
import '../styles.css';

function Chat() {
  const dispatch = useDispatch();
  const { messages, currentConversationId, loading, error } = useSelector((state) => state.chat);
  
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (currentConversationId) {
      dispatch(fetchMessages(currentConversationId));
    }
  }, [currentConversationId, dispatch]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const messageText = input;
    setInput('');

    await dispatch(sendMessage({
      message: messageText,
      conversationId: currentConversationId,
      title: currentConversationId ? null : `Chat: ${messageText.slice(0, 30)}...`
    }));

    // Fetch updated messages
    if (currentConversationId) {
      dispatch(fetchMessages(currentConversationId));
    }
  };

  const handleNewChat = () => {
    dispatch(clearMessages());
  };

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>AI Chat</h1>
        <button onClick={handleNewChat} style={{ padding: '10px 20px', background: '#6366f1', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          New Chat
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div style={{ 
        border: '2px solid #e2e8f0', 
        borderRadius: '12px', 
        height: '500px', 
        display: 'flex', 
        flexDirection: 'column',
        background: 'white'
      }}>
        {/* Messages Area */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '15px'
        }}>
          {messages.length === 0 && !loading && (
            <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: '50px' }}>
              <p>Start a conversation with the AI</p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: '12px',
                background: msg.role === 'user' ? '#667eea' : '#f1f5f9',
                color: msg.role === 'user' ? 'white' : '#1e293b',
                wordWrap: 'break-word'
              }}
            >
              <div style={{ fontWeight: '600', fontSize: '12px', marginBottom: '4px', opacity: 0.8 }}>
                {msg.role === 'user' ? 'You' : 'AI'}
              </div>
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
            </div>
          ))}

          {loading && (
            <div style={{ textAlign: 'center', color: '#667eea' }}>
              <p>AI is thinking...</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form onSubmit={handleSubmit} style={{ 
          borderTop: '2px solid #e2e8f0', 
          padding: '20px',
          display: 'flex',
          gap: '10px'
        }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
            style={{ 
              flex: 1,
              padding: '12px',
              border: '2px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '14px'
            }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            style={{
              padding: '12px 24px',
              background: loading ? '#cbd5e1' : '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: '600'
            }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat;