import { motion, AnimatePresence } from 'framer-motion';
import { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatContainer } from '../components/Chat';
import { EditableMatrixCard } from '../components/Matrix';
import { StageNavigator } from '../components/StageNavigator';
import { useChatStore } from '../stores/chatStore';
import { PencilIcon, CheckIcon, XMarkIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

export const ProcessDesignPage: FC = () => {
  const navigate = useNavigate();
  const {
    messages,
    isLoading,
    isSaving,
    saveSuccess,
    sendMessage,
    analysisMatrix,
    updateAnalysisMatrix
  } = useChatStore();
  
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedMatrix, setEditedMatrix] = useState(analysisMatrix);

  const handleEnterEditMode = () => {
    setEditedMatrix(analysisMatrix);
    setIsEditMode(true);
  };

  const handleSave = async () => {
    if (editedMatrix) {
      await updateAnalysisMatrix(editedMatrix);
      setIsEditMode(false);
    }
  };

  const handleCancel = () => {
    setEditedMatrix(analysisMatrix);
    setIsEditMode(false);
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white/80 backdrop-blur-xl border-b border-gray-200 px-6 py-4 shadow-sm"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <motion.div
              whileHover={{ scale: 1.05, rotate: 5 }}
              className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30"
            >
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </motion.div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">BPM-Nova</h1>
              <p className="text-sm text-gray-500">AI驱动的流程设计工具</p>
            </div>
          </div>

          {/* Progress Indicator and Next Step Button */}
          {analysisMatrix && (
            <div className="flex items-center gap-3">
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-full"
              >
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-blue-700">
                  需求分析完成
                </span>
              </motion.div>
              
              <motion.button
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/requirements')}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-purple-500/30"
              >
                生成需求文档
                <ArrowRightIcon className="w-4 h-4" />
              </motion.button>
            </div>
          )}
        </div>
      </motion.header>

      {/* Stage Navigator */}
      <StageNavigator currentStage={analysisMatrix ? 1 : 0} />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex-1 flex flex-col"
        >
          <ChatContainer
            messages={messages}
            onSendMessage={sendMessage}
            isLoading={isLoading}
          />
        </motion.div>

        {/* Analysis Matrix Panel (will be shown when available) */}
        {analysisMatrix && (
          <motion.aside
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="w-96 bg-white/80 backdrop-blur-xl border-l border-gray-200 p-6 overflow-y-auto"
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: '#cbd5e1 transparent',
            }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-800">
                需求分析矩阵
              </h2>
              
              {!isEditMode ? (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleEnterEditMode}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors shadow-md"
                >
                  <PencilIcon className="w-4 h-4" />
                  编辑矩阵
                </motion.button>
              ) : (
                <div className="flex items-center gap-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSave}
                    disabled={isSaving}
                    className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white rounded-lg text-sm font-medium transition-colors shadow-md"
                  >
                    <CheckIcon className="w-4 h-4" />
                    {isSaving ? '保存中...' : '保存'}
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleCancel}
                    disabled={isSaving}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-400 hover:bg-gray-500 disabled:bg-gray-300 text-white rounded-lg text-sm font-medium transition-colors shadow-md"
                  >
                    <XMarkIcon className="w-4 h-4" />
                    取消
                  </motion.button>
                </div>
              )}
            </div>

            {/* Save Success Message */}
            <AnimatePresence>
              {saveSuccess && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700"
                >
                  ✓ 保存成功！
                </motion.div>
              )}
            </AnimatePresence>

            {/* Matrix Content */}
            <div className="space-y-4">
              {isEditMode && editedMatrix ? (
                <>
                  <EditableMatrixCard
                    title="参与者"
                    items={editedMatrix.actors || []}
                    color="blue"
                    onUpdate={(items) => setEditedMatrix({ ...editedMatrix, actors: items })}
                  />
                  <EditableMatrixCard
                    title="场景"
                    items={editedMatrix.scenarios || []}
                    color="purple"
                    onUpdate={(items) => setEditedMatrix({ ...editedMatrix, scenarios: items })}
                  />
                  <EditableMatrixCard
                    title="数据"
                    items={editedMatrix.data || []}
                    color="green"
                    onUpdate={(items) => setEditedMatrix({ ...editedMatrix, data: items })}
                  />
                  <EditableMatrixCard
                    title="规则"
                    items={editedMatrix.rules || []}
                    color="orange"
                    onUpdate={(items) => setEditedMatrix({ ...editedMatrix, rules: items })}
                  />
                  <EditableMatrixCard
                    title="异常"
                    items={editedMatrix.exceptions || []}
                    color="red"
                    onUpdate={(items) => setEditedMatrix({ ...editedMatrix, exceptions: items })}
                  />
                </>
              ) : (
                <>
              {/* Actors */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-blue-900 mb-2">
                  参与者 ({analysisMatrix.actors?.length || 0})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysisMatrix.actors?.map((actor, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-white/80 rounded-full text-xs text-blue-700 font-medium"
                    >
                      {actor}
                    </span>
                  ))}
                </div>
              </div>

              {/* Scenarios */}
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-purple-900 mb-2">
                  场景 ({analysisMatrix.scenarios?.length || 0})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysisMatrix.scenarios?.map((scenario, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-white/80 rounded-full text-xs text-purple-700 font-medium"
                    >
                      {scenario}
                    </span>
                  ))}
                </div>
              </div>

              {/* Data */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-green-900 mb-2">
                  数据 ({analysisMatrix.data?.length || 0})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysisMatrix.data?.map((item, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-white/80 rounded-full text-xs text-green-700 font-medium"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              {/* Rules */}
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-orange-900 mb-2">
                  规则 ({analysisMatrix.rules?.length || 0})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysisMatrix.rules?.map((rule, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-white/80 rounded-full text-xs text-orange-700 font-medium"
                    >
                      {rule}
                    </span>
                  ))}
                </div>
              </div>

              {/* Exceptions */}
              <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-red-900 mb-2">
                  异常 ({analysisMatrix.exceptions?.length || 0})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysisMatrix.exceptions?.map((exception, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-white/80 rounded-full text-xs text-red-700 font-medium"
                    >
                      {exception}
                    </span>
                  ))}
                </div>
              </div>
                </>
              )}
            </div>
          </motion.aside>
        )}
      </div>
    </div>
  );
};

// Made with Bob
