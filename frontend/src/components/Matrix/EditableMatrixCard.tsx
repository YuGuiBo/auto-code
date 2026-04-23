import { FC, useState, KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PlusIcon, XMarkIcon, PencilIcon, CheckIcon } from '@heroicons/react/24/outline';

interface EditableMatrixCardProps {
  title: string;
  items: string[];
  color: 'blue' | 'purple' | 'green' | 'orange' | 'red';
  onUpdate: (items: string[]) => void;
}

const colorConfig = {
  blue: {
    bg: 'from-blue-50 to-blue-100',
    text: 'text-blue-900',
    badge: 'bg-white/80 text-blue-700',
    button: 'bg-blue-500 hover:bg-blue-600',
    input: 'border-blue-300 focus:border-blue-500 focus:ring-blue-500',
  },
  purple: {
    bg: 'from-purple-50 to-purple-100',
    text: 'text-purple-900',
    badge: 'bg-white/80 text-purple-700',
    button: 'bg-purple-500 hover:bg-purple-600',
    input: 'border-purple-300 focus:border-purple-500 focus:ring-purple-500',
  },
  green: {
    bg: 'from-green-50 to-green-100',
    text: 'text-green-900',
    badge: 'bg-white/80 text-green-700',
    button: 'bg-green-500 hover:bg-green-600',
    input: 'border-green-300 focus:border-green-500 focus:ring-green-500',
  },
  orange: {
    bg: 'from-orange-50 to-orange-100',
    text: 'text-orange-900',
    badge: 'bg-white/80 text-orange-700',
    button: 'bg-orange-500 hover:bg-orange-600',
    input: 'border-orange-300 focus:border-orange-500 focus:ring-orange-500',
  },
  red: {
    bg: 'from-red-50 to-red-100',
    text: 'text-red-900',
    badge: 'bg-white/80 text-red-700',
    button: 'bg-red-500 hover:bg-red-600',
    input: 'border-red-300 focus:border-red-500 focus:ring-red-500',
  },
};

export const EditableMatrixCard: FC<EditableMatrixCardProps> = ({
  title,
  items,
  color,
  onUpdate,
}) => {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [newValue, setNewValue] = useState('');

  const colors = colorConfig[color];

  const handleStartEdit = (index: number) => {
    setEditingIndex(index);
    setEditValue(items[index]);
  };

  const handleSaveEdit = () => {
    if (editingIndex !== null && editValue.trim()) {
      const newItems = [...items];
      newItems[editingIndex] = editValue.trim();
      onUpdate(newItems);
      setEditingIndex(null);
      setEditValue('');
    }
  };

  const handleCancelEdit = () => {
    setEditingIndex(null);
    setEditValue('');
  };

  const handleDelete = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    onUpdate(newItems);
  };

  const handleAdd = () => {
    if (newValue.trim()) {
      onUpdate([...items, newValue.trim()]);
      setNewValue('');
      setIsAdding(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>, action: 'edit' | 'add') => {
    if (e.key === 'Enter') {
      e.preventDefault();
      action === 'edit' ? handleSaveEdit() : handleAdd();
    } else if (e.key === 'Escape') {
      action === 'edit' ? handleCancelEdit() : setIsAdding(false);
    }
  };

  return (
    <motion.div
      layout
      className={`bg-gradient-to-br ${colors.bg} rounded-xl p-4`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className={`text-sm font-semibold ${colors.text}`}>
          {title} ({items.length})
        </h3>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsAdding(true)}
          className={`p-1 rounded-lg ${colors.button} text-white transition-colors`}
          title="添加项目"
        >
          <PlusIcon className="w-4 h-4" />
        </motion.button>
      </div>

      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {items.map((item, index) => (
            <motion.div
              key={`${item}-${index}`}
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex items-center gap-2"
            >
              {editingIndex === index ? (
                <>
                  <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, 'edit')}
                    className={`flex-1 px-3 py-1.5 text-xs rounded-lg border-2 ${colors.input} focus:outline-none focus:ring-2`}
                    autoFocus
                  />
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={handleSaveEdit}
                    className="p-1 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
                  >
                    <CheckIcon className="w-4 h-4" />
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={handleCancelEdit}
                    className="p-1 bg-gray-400 hover:bg-gray-500 text-white rounded-lg transition-colors"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </motion.button>
                </>
              ) : (
                <>
                  <span className={`flex-1 px-3 py-1.5 ${colors.badge} rounded-lg text-xs font-medium`}>
                    {item}
                  </span>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleStartEdit(index)}
                    className="p-1 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleDelete(index)}
                    className="p-1 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </motion.button>
                </>
              )}
            </motion.div>
          ))}

          {isAdding && (
            <motion.div
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, 'add')}
                placeholder="输入新项目..."
                className={`flex-1 px-3 py-1.5 text-xs rounded-lg border-2 ${colors.input} focus:outline-none focus:ring-2`}
                autoFocus
              />
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleAdd}
                className="p-1 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
              >
                <CheckIcon className="w-4 h-4" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => {
                  setIsAdding(false);
                  setNewValue('');
                }}
                className="p-1 bg-gray-400 hover:bg-gray-500 text-white rounded-lg transition-colors"
              >
                <XMarkIcon className="w-4 h-4" />
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>

        {items.length === 0 && !isAdding && (
          <p className="text-xs text-gray-500 italic text-center py-2">
            暂无项目，点击 + 添加
          </p>
        )}
      </div>
    </motion.div>
  );
};

// Made with Bob