import React, { useState, useRef, useEffect } from 'react';
import styles from './Chatbot.module.css';

const apiUrl = import.meta.env.VITE_API_URL;

interface StatsSegmentsProps {
  user_balance: {
    cash_balance?: number;
    savings_balance?: number;
    investing_retirement?: number;
    total_balance?: number;
  };
}

const Chatbot = (props: StatsSegmentsProps) => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([{ from: 'bot', text: 'Hi! How can I help you today?' }]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, open]);

  // Utility to get cookie value
  function getCookie(name: string) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift();
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages([...messages, { from: 'user', text: input }]);
    setInput('');
    // Simulate bot response
    const csrftoken = getCookie('csrftoken');
    const response = await fetch(`${apiUrl}/openai/chatbot/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken || '',
      },
      credentials: 'include',
      body: JSON.stringify({ user_balance: props.user_balance, user_message: input }),
    });
    console.log('response: ', response);
    const data = await response.json();
    console.log('openAI Response: ', data);
    if (data == true) {
      setMessages((msgs) => [...msgs, { from: 'bot', text: 'Monetary_Balance_Query: true' }]);
    } else {
      setMessages((msgs) => [...msgs, { from: 'bot', text: data }]);
    }
  };

  return (
    <div className={styles.chatbotContainer}>
      {!open && (
        <button className={styles.fab} onClick={() => setOpen(true)} aria-label="Open chatbot">
          <img
            src="https://img.icons8.com/?size=100&id=uZrQP6cYos2I&format=png&color=000000"
            alt="Open chatbot"
            style={{ width: 40, height: 40 }}
          />
        </button>
      )}
      {open && (
        <div className={styles.chatWindow}>
          <div className={styles.header}>
            <span>Chatbot</span>
            <button className={styles.closeBtn} onClick={() => setOpen(false)} aria-label="Close chatbot">
              ×
            </button>
          </div>
          <div className={styles.messages}>
            {messages.map((msg, idx) => (
              <div key={idx} className={msg.from === 'user' ? styles.userMsg : styles.botMsg}>
                {msg.from === 'bot'
                  ? msg.text.split('\n\n').map((para, i, arr) => (
                      <div key={i} style={i === arr.length - 1 ? undefined : { marginBottom: '1em' }}>
                        {para.split('\n').map((line, j) => (
                          <div key={j}>{line}</div>
                        ))}
                      </div>
                    ))
                  : msg.text}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <form className={styles.inputArea} onSubmit={handleSend}>
            <textarea
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = e.target.scrollHeight + 'px';
              }}
              placeholder="Type your message..."
              className={styles.input}
              autoFocus
              rows={1}
              style={{ resize: 'none', overflow: 'hidden' }}
            />
            <button type="submit" className={styles.sendBtn} aria-label="Send">
              ➤
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
// Fix the issue with adding more text than the chatbot input bot can handle. currently it scrolls to the right but i want it to instead expand down.
// Fix the issue with ai response looking like it's just one long paragraph

export default Chatbot;
