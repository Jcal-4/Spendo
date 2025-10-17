import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useState } from 'react';
import styles from './Chatbot.module.css';

const apiUrl = import.meta.env.VITE_API_URL;

export function MyChat() {
  const [open, setOpen] = useState(false);

  // Utility to get cookie value
  function getCookie(name: string) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift();
  }

  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        const csrftoken = getCookie('csrftoken');
        if (existing) {
          // implement session refresh
        }

        const res = await fetch(`${apiUrl}/chatkit/session/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken || '',
          },
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
    },
    theme: {
      colorScheme: 'dark',
      radius: 'round',
      density: 'compact',
      typography: {
        baseSize: 16,
        fontFamily:
          '"OpenAI Sans", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif',
        fontFamilyMono:
          'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace',
        fontSources: [
          {
            family: 'OpenAI Sans',
            src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Regular.woff2',
            weight: 400,
            style: 'normal',
            display: 'swap',
          },
          // ...and 7 more font sources
        ],
      },
    },
    header: {
      rightAction: {
        icon: 'close',
        onClick: () => setOpen(false),
      },
    },
  });

  return (
    <div className={styles.openAIchatbotContainer}>
      {!open && (
        <button className={styles.fab} onClick={() => setOpen(true)} aria-label="Open chatbot">
          <img
            src="https://img.icons8.com/?size=100&id=kTuxVYRKeKEY&format=png&color=000000"
            alt="chatgpt"
            style={{ width: 40, height: 40 }}
          />
        </button>
      )}
      {open && (
        <div>
          <ChatKit control={control} className="min-h-[700px] w-[450px] " />
        </div>
      )}
    </div>
  );
}
export default MyChat;
