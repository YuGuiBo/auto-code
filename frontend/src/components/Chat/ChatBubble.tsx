import { motion } from 'framer-motion';
import { FC } from 'react';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatBubbleProps {
  message: Message;
  index: number;
}

export const ChatBubble: FC<ChatBubbleProps> = ({ message, index }) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.3,
        delay: index * 0.05,
        ease: [0.25, 0.1, 0.25, 1],
      }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex items-end gap-2 max-w-[70%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: index * 0.05 + 0.1 }}
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            isUser
              ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
              : 'bg-gradient-to-br from-purple-500 to-pink-500 text-white'
          }`}
        >
          {isUser ? '我' : 'AI'}
        </motion.div>

        {/* Message Bubble */}
        <div className="flex flex-col gap-1">
          <motion.div
            whileHover={{ scale: 1.02 }}
            className={`relative px-4 py-3 rounded-2xl ${
              isUser
                ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-md'
                : 'bg-white/80 backdrop-blur-xl text-gray-800 rounded-bl-md shadow-lg shadow-gray-200/50'
            }`}
            style={{
              boxShadow: isUser
                ? '0 4px 12px rgba(59, 130, 246, 0.3)'
                : '0 4px 12px rgba(0, 0, 0, 0.08)',
            }}
          >
            {/* Message Content */}
            <p className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">
              {message.content}
            </p>

            {/* Tail */}
            <div
              className={`absolute bottom-0 ${
                isUser ? '-right-1' : '-left-1'
              } w-3 h-3 ${
                isUser
                  ? 'bg-gradient-to-br from-blue-500 to-blue-600'
                  : 'bg-white/80 backdrop-blur-xl'
              }`}
              style={{
                clipPath: isUser
                  ? 'polygon(0 0, 100% 0, 100% 100%)'
                  : 'polygon(0 0, 0 100%, 100% 100%)',
              }}
            />
          </motion.div>

          {/* Timestamp */}
          <span
            className={`text-xs text-gray-400 px-2 ${
              isUser ? 'text-right' : 'text-left'
            }`}
          >
            {message.timestamp.toLocaleTimeString('zh-CN', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

// Made with Bob
