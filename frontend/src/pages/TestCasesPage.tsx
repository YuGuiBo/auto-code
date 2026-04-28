import { motion, AnimatePresence } from 'framer-motion';
import { FC, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import { StageNavigator } from '../components/StageNavigator';
import { TestCaseView } from '../components/TestCases/TestCaseView';
import {
  BeakerIcon,
  SparklesIcon,
  ExclamationCircleIcon,
  ArrowRightIcon,
  XMarkIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

export const TestCasesPage: FC = () => {
  const navigate = useNavigate();
  const {
    currentProcessId,
    testCases,
    structuredRequirements,
    bpmnXml,
    bpmnNeedsRegeneration,
    isGenerating,
    error,
    saveSuccess,
    generateTestCases,
    submitTestCaseFeedback,
    setBpmnNeedsRegeneration,
  } = useChatStore();

  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);

  // Check if we have requirements to generate test cases from
  useEffect(() => {
    if (!currentProcessId) {
      navigate('/design');
    }
  }, [currentProcessId, navigate]);

  const handleGenerateTestCases = async () => {
    await generateTestCases();
  };

  const handleSubmitFeedback = async () => {
    if (!feedbackText.trim()) return;
    
    setIsSubmittingFeedback(true);
    try {
      await submitTestCaseFeedback(feedbackText);
      setFeedbackText('');
      setShowFeedbackDialog(false);
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const handleProceedToBPMN = () => {
    navigate('/bpmn');
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
              className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/30"
            >
              <BeakerIcon className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">测试案例</h1>
              <p className="text-sm text-gray-500">基于需求文档生成的详细测试案例</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            {!testCases && structuredRequirements && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleGenerateTestCases}
                disabled={isGenerating}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-green-500/30"
              >
                <SparklesIcon className="w-5 h-5" />
                {isGenerating ? '生成中...' : '生成测试案例'}
              </motion.button>
            )}

            {testCases && (
              <>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowFeedbackDialog(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg text-sm font-medium transition-colors shadow-md"
                >
                  <ExclamationCircleIcon className="w-4 h-4" />
                  发现问题
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleProceedToBPMN}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-purple-500/30"
                >
                  <span>前往BPMN流程</span>
                  <ArrowRightIcon className="w-4 h-4" />
                </motion.button>
              </>
            )}
          </div>
        </div>
      </motion.header>

      {/* Stage Navigator */}
      <StageNavigator currentStage={2} />

      {/* BPMN重新生成警告 */}
      <AnimatePresence>
        {bpmnNeedsRegeneration && bpmnXml && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mx-6 mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-3"
          >
            <ExclamationCircleIcon className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-amber-800 font-medium">测试案例已更新</p>
              <p className="text-sm text-amber-700 mt-1">
                由于测试案例发生了变化，建议您重新生成BPMN流程图以确保一致性。
              </p>
            </div>
            <button
              onClick={() => setBpmnNeedsRegeneration(false)}
              className="text-amber-600 hover:text-amber-800"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success Message */}
      <AnimatePresence>
        {saveSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mx-6 mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700 shadow-sm flex items-center gap-2"
          >
            <CheckCircleIcon className="w-5 h-5" />
            ✓ 测试案例已更新成功！
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
          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3"
            >
              <ExclamationCircleIcon className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </motion.div>
          )}

          {isGenerating ? (
            /* Loading State */
            <div className="flex flex-col items-center justify-center h-64">
              <div className="relative">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-500"></div>
                <BeakerIcon className="w-8 h-8 text-green-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <p className="mt-4 text-gray-600 text-lg">AI正在生成测试案例...</p>
              <p className="mt-2 text-gray-400 text-sm">这可能需要几秒钟</p>
            </div>
          ) : !testCases ? (
            /* Empty State */
            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-12 text-center">
              <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg">
                <BeakerIcon className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                生成测试案例
              </h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                {structuredRequirements
                  ? '基于您的需求文档，AI将为您生成详细的测试案例，包括正常流程、条件分支和异常场景。'
                  : '请先完成需求文档的生成，然后再生成测试案例。'}
              </p>

              {structuredRequirements ? (
                <motion.button
                  onClick={handleGenerateTestCases}
                  disabled={isGenerating}
                  className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <SparklesIcon className="w-5 h-5" />
                  <span>生成测试案例</span>
                </motion.button>
              ) : (
                <motion.button
                  onClick={() => navigate('/requirements')}
                  className="px-8 py-4 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center space-x-2 mx-auto"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>前往需求文档</span>
                  <ArrowRightIcon className="w-5 h-5" />
                </motion.button>
              )}
            </div>
          ) : (
            /* Display Test Cases */
            <TestCaseView testCasesData={testCases} />
          )}
        </div>
      </motion.div>

      {/* Feedback Dialog */}
      <AnimatePresence>
        {showFeedbackDialog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowFeedbackDialog(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">发现问题？</h3>
                <button
                  onClick={() => setShowFeedbackDialog(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>

              <p className="text-sm text-gray-600 mb-4">
                请描述您发现的问题或缺失的场景，AI将分析并更新测试案例。
              </p>

              <textarea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder="例如：缺少员工撤回申请的场景..."
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none text-sm"
                disabled={isSubmittingFeedback}
              />

              <div className="flex justify-end gap-3 mt-4">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowFeedbackDialog(false)}
                  disabled={isSubmittingFeedback}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
                >
                  取消
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSubmitFeedback}
                  disabled={isSubmittingFeedback || !feedbackText.trim()}
                  className="px-6 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isSubmittingFeedback ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>提交中...</span>
                    </>
                  ) : (
                    <span>提交反馈</span>
                  )}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TestCasesPage;

// Made with Bob
