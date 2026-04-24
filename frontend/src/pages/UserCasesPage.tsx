import { motion, AnimatePresence } from 'framer-motion';
import { FC, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import TimelineUserCaseView from '../components/UserCases/TimelineUserCaseView';
import EditableUserCaseView from '../components/UserCases/EditableUserCaseView';
import { StageNavigator } from '../components/StageNavigator';
import {
  UserGroupIcon,
  SparklesIcon,
  ExclamationCircleIcon,
  ArrowRightIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

export const UserCasesPage: FC = () => {
  const navigate = useNavigate();
  const {
    currentProcessId,
    userCases,
    structuredRequirements,
    isGenerating,
    isSaving,
    saveSuccess,
    error,
    generateUserCases,
    updateUserCases,
  } = useChatStore();

  const [isEditMode, setIsEditMode] = useState(false);
  const [editedCases, setEditedCases] = useState<any[]>([]);

  // Check if we have requirements to generate cases from
  useEffect(() => {
    if (!currentProcessId) {
      navigate('/design');
    }
  }, [currentProcessId, navigate]);

  useEffect(() => {
    if (userCases) {
      setEditedCases(userCases);
    }
  }, [userCases]);

  const handleGenerateCases = async () => {
    await generateUserCases();
  };

  const handleProceedToBPMN = () => {
    navigate('/bpmn');
  };

  const handleEnterEditMode = () => {
    setEditedCases(userCases || []);
    setIsEditMode(true);
  };

  const handleSave = async () => {
    await updateUserCases(editedCases);
    setIsEditMode(false);
  };

  const handleCancel = () => {
    setEditedCases(userCases || []);
    setIsEditMode(false);
  };

  const handleCasesChange = (cases: any[]) => {
    setEditedCases(cases);
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
              <UserGroupIcon className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">用户用例</h1>
              <p className="text-sm text-gray-500">基于需求文档生成详细的用户用例</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            {!userCases && structuredRequirements && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleGenerateCases}
                disabled={isGenerating}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-blue-500/30"
              >
                <SparklesIcon className="w-5 h-5" />
                {isGenerating ? '生成中...' : '生成用户用例'}
              </motion.button>
            )}

            {userCases && !isEditMode && (
              <>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleEnterEditMode}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors shadow-md"
                >
                  <PencilIcon className="w-4 h-4" />
                  编辑用例
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
      <StageNavigator currentStage={3} />

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
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
                <SparklesIcon className="w-8 h-8 text-blue-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <p className="mt-4 text-gray-600 text-lg">AI正在生成用户用例...</p>
              <p className="mt-2 text-gray-400 text-sm">这可能需要几秒钟</p>
            </div>
          ) : !userCases ? (
            /* Empty State */
            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-12 text-center">
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
                  <SparklesIcon className="w-5 h-5" />
                  <span>生成用户用例</span>
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
            /* Display Cases */
            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-8">
              {isEditMode ? (
                <EditableUserCaseView
                  cases={editedCases}
                  onChange={handleCasesChange}
                />
              ) : (
                <TimelineUserCaseView cases={userCases as any} />
              )}
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default UserCasesPage;

// Made with Bob
