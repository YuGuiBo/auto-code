import { motion, AnimatePresence } from 'framer-motion';
import { FC, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import {
  DocumentTextIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  SparklesIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import StructuredRequirementsView from '../components/Requirements/StructuredRequirementsView';
import EditableRequirementsView from '../components/Requirements/EditableRequirementsView';
import { StageNavigator } from '../components/StageNavigator';
import { StructuredRequirements } from '../services/api';

export const RequirementsPage: FC = () => {
  const navigate = useNavigate();
  const {
    structuredRequirements,
    isGenerating,
    isSaving,
    saveSuccess,
    generateRequirements,
    updateRequirements,
    analysisMatrix,
  } = useChatStore();

  const [isEditMode, setIsEditMode] = useState(false);
  const [editedRequirements, setEditedRequirements] = useState<StructuredRequirements | null>(
    null
  );

  useEffect(() => {
    if (structuredRequirements) {
      setEditedRequirements(structuredRequirements);
    }
  }, [structuredRequirements]);

  const handleGenerate = async () => {
    await generateRequirements();
  };

  const handleEnterEditMode = () => {
    setEditedRequirements(structuredRequirements);
    setIsEditMode(true);
  };

  const handleSave = async () => {
    if (editedRequirements) {
      await updateRequirements(editedRequirements);
      setIsEditMode(false);
    }
  };

  const handleCancel = () => {
    setEditedRequirements(structuredRequirements);
    setIsEditMode(false);
  };

  const handleChange = (requirements: StructuredRequirements) => {
    setEditedRequirements(requirements);
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
              <DocumentTextIcon className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">结构化需求文档</h1>
              <p className="text-sm text-gray-500">基于分析矩阵生成的详细需求</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            {!structuredRequirements && analysisMatrix && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleGenerate}
                disabled={isGenerating}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-blue-500/30"
              >
                <SparklesIcon className="w-5 h-5" />
                {isGenerating ? '生成中...' : '生成需求文档'}
              </motion.button>
            )}

            {structuredRequirements && !isEditMode && (
              <>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleEnterEditMode}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors shadow-md"
                >
                  <PencilIcon className="w-4 h-4" />
                  编辑文档
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/cases')}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-purple-500/30"
                >
                  <span>前往测试案例</span>
                  <ArrowRightIcon className="w-4 h-4" />
                </motion.button>
              </>
            )}

            {isEditMode && (
              <>
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
              </>
            )}
          </div>
        </div>
      </motion.header>

      {/* Stage Navigator */}
      <StageNavigator currentStage={1} />

      {/* Save Success Message */}
      <AnimatePresence>
        {saveSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mx-6 mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700 shadow-sm"
          >
            ✓ 保存成功！
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex-1 overflow-y-auto p-6"
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: '#cbd5e1 transparent',
        }}
      >
        <div className="max-w-5xl mx-auto">
          {isGenerating ? (
            /* Loading State */
            <div className="flex flex-col items-center justify-center h-64">
              <div className="relative">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
                <SparklesIcon className="w-8 h-8 text-blue-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <p className="mt-4 text-gray-600 text-lg">AI正在生成需求文档...</p>
              <p className="mt-2 text-gray-400 text-sm">这可能需要几秒钟</p>
            </div>
          ) : !structuredRequirements ? (
            /* Empty State */
            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-12 text-center">
              <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                <DocumentTextIcon className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                生成需求文档
              </h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                {analysisMatrix
                  ? '基于您的分析矩阵，AI将为您生成详细的结构化需求文档，包括操作步骤、前置条件和后置条件。'
                  : '请先完成分析矩阵的生成，然后再生成需求文档。'}
              </p>

              {analysisMatrix ? (
                <motion.button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <SparklesIcon className="w-5 h-5" />
                  <span>生成需求文档</span>
                </motion.button>
              ) : (
                <motion.button
                  onClick={() => navigate('/design')}
                  className="px-8 py-4 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center space-x-2 mx-auto"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>前往分析矩阵</span>
                  <ArrowRightIcon className="w-5 h-5" />
                </motion.button>
              )}
            </div>
          ) : isEditMode && editedRequirements ? (
            <EditableRequirementsView
              requirements={editedRequirements}
              onChange={handleChange}
            />
          ) : (
            <StructuredRequirementsView
              requirements={structuredRequirements}
              isLoading={isGenerating}
            />
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default RequirementsPage;

// Made with Bob
