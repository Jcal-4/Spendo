import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useState } from 'react';
import styles from './Chatbot.module.css';

const apiUrl = import.meta.env.VITE_API_URL;

interface MyChatProps {
  user_balance: {
    cash_balance: number;
    savings_balance: number;
    investing_retirement: number;
    total_balance: number;
  };
}

export function MyChat({ user_balance }: MyChatProps) {
  const [open, setOpen] = useState(false);

  // user_balance is available for future use (e.g., passing to backend context)
  // Currently unused but kept for potential backend integration
  void user_balance; // Acknowledge parameter to prevent unused variable warning

  const { control } = useChatKit({
    api: {
      url: `${apiUrl}/chatkit/`,
      domainKey: 'domain_pk_68f1603233888190b4b67253144535800b4aeac929b652bc',
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
