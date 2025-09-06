import React, { useState, useRef, useEffect } from 'react';
import styles from './Chatbot.module.css';

const Chatbot: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([{ from: 'bot', text: 'Hi! How can I help you today?' }]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, open]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages([...messages, { from: 'user', text: input }]);
    setInput('');
    // Simulate bot response
    setTimeout(() => {
      setMessages((msgs) => [...msgs, { from: 'bot', text: "I'm just a demo chatbot!" }]);
    }, 600);
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
                {msg.text}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <form className={styles.inputArea} onSubmit={handleSend}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className={styles.input}
              autoFocus
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

export default Chatbot;
