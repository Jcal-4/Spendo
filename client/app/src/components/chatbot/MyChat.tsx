import { ChatKit, useChatKit } from '@openai/chatkit-react';

const apiUrl = import.meta.env.VITE_API_URL;

export function MyChat() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        if (existing) {
          // implement session refresh
        }

        const res = await fetch(`${apiUrl}/api/chatkit/session/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
    },
  });

  return <ChatKit control={control} className="min-h-[500px] w-[400px]" />;
}
export default MyChat;
