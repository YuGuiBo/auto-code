import { motion } from 'framer-motion';
import { FC, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import { bpmnApi } from '../services/api';
import {
  CubeIcon,
  SparklesIcon,
  ArrowDownTrayIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

export const BPMNPage: FC = () => {
  const navigate = useNavigate();
  const { currentProcessId, userCases } = useChatStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [bpmnXml, setBpmnXml] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!currentProcessId) {
      navigate('/design');
    }
  }, [currentProcessId, navigate]);

  const handleGenerateBPMN = async () => {
    if (!currentProcessId) return;

    setIsGenerating(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await bpmnApi.generateBPMN(currentProcessId);
      setBpmnXml(response.bpmn_xml);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      console.error('Failed to generate BPMN:', err);
      setError(err.response?.data?.detail || '生成BPMN失败，请稍后重试。');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadBPMN = () => {
    if (!bpmnXml) return;

    const blob = new Blob([bpmnXml], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `process-${currentProcessId}.bpmn`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
              <CubeIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                BPMN流程图
              </h1>
              <p className="text-gray-500 text-sm">
                基于用户用例生成标准BPMN 2.0流程定义
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

        {/* Success Message */}
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-start space-x-3"
          >
            <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-green-700">BPMN流程生成成功！</p>
          </motion.div>
        )}

        {/* Content */}
        {!bpmnXml ? (
          /* Empty State - Generate BPMN */
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-12 text-center"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
              <CubeIcon className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              生成BPMN流程图
            </h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              {userCases
                ? 'AI将基于您的用户用例生成标准的BPMN 2.0流程定义，可直接导入到Flowable等流程引擎中使用。'
                : '请先完成用户用例的生成，然后再生成BPMN流程图。'}
            </p>

            {userCases ? (
              <motion.button
                onClick={handleGenerateBPMN}
                disabled={isGenerating}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
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
                    <span>生成BPMN流程</span>
                  </>
                )}
              </motion.button>
            ) : (
              <motion.button
                onClick={() => navigate('/cases')}
                className="px-8 py-4 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center space-x-2 mx-auto"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span>前往用户用例</span>
              </motion.button>
            )}
          </motion.div>
        ) : (
          /* Display BPMN */
          <div className="space-y-6">
            {/* BPMN XML Display */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-8"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  BPMN 2.0 XML
                </h3>
                <motion.button
                  onClick={handleDownloadBPMN}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                  <span>下载BPMN</span>
                </motion.button>
              </div>

              <div className="bg-gray-900 rounded-xl p-6 overflow-auto max-h-96">
                <pre className="text-sm text-green-400 font-mono">
                  {bpmnXml}
                </pre>
              </div>
            </motion.div>

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="flex space-x-4"
            >
              <motion.button
                onClick={handleGenerateBPMN}
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
                onClick={() => navigate('/design')}
                className="flex-1 py-4 px-6 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span>开始新流程</span>
              </motion.button>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BPMNPage;

// Made with Bob
