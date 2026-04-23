import { motion, AnimatePresence } from 'framer-motion';
import { FC, useRef, useEffect, useState } from 'react';
import { ChatBubble, Message } from './ChatBubble';
import { ChatInput } from './ChatInput';

interface ChatContainerProps {
  messages: Message[];
  onSendMessage: (content: string) => void;
  isLoading?: boolean;
}

export const ChatContainer: FC<ChatContainerProps> = ({
  messages,
  onSendMessage,
  isLoading = false,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Check if user has scrolled up
  const handleScroll = () => {
    if (containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-6 py-6 space-y-4"
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: '#cbd5e1 transparent',
        }}
      >
        {/* Empty State */}
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center justify-center h-full text-center"
          >
            <motion.div
              animate={{
                scale: [1, 1.05, 1],
                rotate: [0, 5, -5, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
              className="w-24 h-24 mb-6 bg-gradient-to-br from-blue-400 to-purple-500 rounded-3xl flex items-center justify-center shadow-2xl shadow-blue-500/30"
            >
              <svg
                className="w-12 h-12 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </motion.div>
            <h3 className="text-2xl font-semibold text-gray-800 mb-2">
              开始你的流程设计之旅
            </h3>
            <p className="text-gray-500 max-w-md">
              告诉我你想要创建什么样的流程，我会帮你分析需求并生成完整的BPMN流程图
            </p>
          </motion.div>
        )}

        {/* Messages */}
        <AnimatePresence mode="popLayout">
          {messages.map((message, index) => (
            <ChatBubble key={message.id} message={message} index={index} />
          ))}
        </AnimatePresence>

        {/* Loading Indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-2 mb-4"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-sm font-medium">
              AI
            </div>
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl rounded-bl-md px-4 py-3 shadow-lg">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.5, 1, 0.5],
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      delay: i * 0.2,
                    }}
                    className="w-2 h-2 bg-gray-400 rounded-full"
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Scroll to Bottom Button */}
      <AnimatePresence>
        {showScrollButton && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={scrollToBottom}
            className="absolute bottom-24 right-8 w-10 h-10 bg-white/90 backdrop-blur-xl rounded-full shadow-lg flex items-center justify-center text-gray-600 hover:bg-white transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 14l-7 7m0 0l-7-7m7 7V3"
              />
            </svg>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Input Area */}
      <div className="px-6 pb-6 pt-2">
        <ChatInput onSend={onSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
};

// Made with Bob
