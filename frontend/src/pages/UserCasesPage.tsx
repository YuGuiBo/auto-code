import { motion } from 'framer-motion';
import { FC, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import TimelineUserCaseView from '../components/UserCases/TimelineUserCaseView';
import {
  UserGroupIcon,
  SparklesIcon,
  ExclamationCircleIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';

export const UserCasesPage: FC = () => {
  const navigate = useNavigate();
  const {
    currentProcessId,
    userCases,
    structuredRequirements,
    isGenerating,
    error,
    generateUserCases,
  } = useChatStore();

  // Check if we have requirements to generate cases from
  useEffect(() => {
    if (!currentProcessId) {
      navigate('/design');
    }
  }, [currentProcessId, navigate]);

  const handleGenerateCases = async () => {
    await generateUserCases();
  };

  const handleProceedToBPMN = () => {
    navigate('/bpmn');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
              <UserGroupIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                用户用例
              </h1>
              <p className="text-gray-500 text-sm">
                基于需求文档生成详细的用户用例
              </p>
            </div>
          </div>
        </motion.div>

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

        {/* Content */}
        {!userCases ? (
          /* Empty State - Generate Cases */
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-12 text-center"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
              <UserGroupIcon className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              生成用户用例
            </h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              {structuredRequirements
                ? '基于您的需求文档，AI将为您生成详细的用户用例，包括操作步骤、前置条件和后置条件。'
                : '请先完成需求文档的生成，然后再生成用户用例。'}
            </p>

            {structuredRequirements ? (
              <motion.button
                onClick={handleGenerateCases}
                disabled={isGenerating}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isGenerating ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>生成中...</span>
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-5 h-5" />
                    <span>生成用户用例</span>
                  </>
                )}
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
          </motion.div>
        ) : (
          /* Display Cases */
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-8"
            >
              <TimelineUserCaseView cases={userCases} />
            </motion.div>

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="flex space-x-4"
            >
              <motion.button
                onClick={handleGenerateCases}
                disabled={isGenerating}
                className="flex-1 py-4 px-6 bg-white/80 backdrop-blur-xl text-gray-700 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isGenerating ? (
                  <>
                    <div className="w-5 h-5 border-2 border-gray-700 border-t-transparent rounded-full animate-spin" />
                    <span>重新生成中...</span>
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-5 h-5" />
                    <span>重新生成</span>
                  </>
                )}
              </motion.button>

              <motion.button
                onClick={handleProceedToBPMN}
                className="flex-1 py-4 px-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span>生成BPMN流程</span>
                <ArrowRightIcon className="w-5 h-5" />
              </motion.button>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserCasesPage;

// Made with Bob
