import { motion } from 'framer-motion';
import { FC, useState, KeyboardEvent, useRef, useEffect } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  placeholder = '描述你想要创建的流程...',
}) => {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="relative"
    >
      {/* Input Container */}
      <motion.div
        animate={{
          boxShadow: isFocused
            ? '0 8px 32px rgba(59, 130, 246, 0.15)'
            : '0 4px 16px rgba(0, 0, 0, 0.08)',
        }}
        className={`relative bg-white/80 backdrop-blur-xl rounded-2xl border-2 transition-colors duration-200 ${
          isFocused ? 'border-blue-400' : 'border-gray-200'
        }`}
      >
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          placeholder={placeholder}
          rows={1}
          className="w-full px-5 py-4 pr-14 bg-transparent resize-none outline-none text-gray-800 placeholder-gray-400 text-[15px] leading-relaxed max-h-32 overflow-y-auto"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: '#cbd5e1 transparent',
          }}
        />

        {/* Send Button */}
        <motion.button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          whileHover={{ scale: message.trim() && !disabled ? 1.05 : 1 }}
          whileTap={{ scale: message.trim() && !disabled ? 0.95 : 1 }}
          className={`absolute right-3 bottom-3 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 ${
            message.trim() && !disabled
              ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30 cursor-pointer'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          }`}
        >
          <motion.div
            animate={{
              rotate: message.trim() && !disabled ? [0, -10, 0] : 0,
            }}
            transition={{
              duration: 0.5,
              repeat: message.trim() && !disabled ? Infinity : 0,
              repeatDelay: 2,
            }}
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </motion.div>
        </motion.button>
      </motion.div>

      {/* Hint Text */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: isFocused ? 1 : 0 }}
        className="absolute -bottom-6 left-0 text-xs text-gray-400"
      >
        按 Enter 发送，Shift + Enter 换行
      </motion.p>
    </motion.div>
  );
};

// Made with Bob
