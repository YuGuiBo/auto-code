import { motion, AnimatePresence } from 'framer-motion';
import { FC, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import { bpmnApi } from '../services/api';
import { StageNavigator } from '../components/StageNavigator';
import { BpmnViewer } from '../components/BpmnViewer';
import {
  CubeIcon,
  SparklesIcon,
  ArrowDownTrayIcon,
  ArrowRightIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  CodeBracketIcon,
  Square3Stack3DIcon,
} from '@heroicons/react/24/outline';

export const BPMNPage: FC = () => {
  const navigate = useNavigate();
  const { currentProcessId, testCases } = useChatStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [bpmnXml, setBpmnXml] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [viewMode, setViewMode] = useState<'diagram' | 'xml'>('diagram');

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
              className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30"
            >
              <CubeIcon className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">BPMN流程图</h1>
              <p className="text-sm text-gray-500">基于测试案例生成标准BPMN 2.0流程定义</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            {bpmnXml ? (
              <>
                <motion.button
                  onClick={handleDownloadBPMN}
                  className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-300 flex items-center gap-2"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <ArrowDownTrayIcon className="w-4 h-4" />
                  <span>下载BPMN</span>
                </motion.button>
                <motion.button
                  onClick={handleGenerateBPMN}
                  disabled={isGenerating}
                  className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {isGenerating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>重新生成中...</span>
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="w-4 h-4" />
                      <span>重新生成</span>
                    </>
                  )}
                </motion.button>
                <motion.button
                  onClick={() => navigate('/design')}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-300 flex items-center gap-2"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>开始新流程</span>
                </motion.button>
              </>
            ) : testCases ? (
              <motion.button
                onClick={handleGenerateBPMN}
                disabled={isGenerating}
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>生成中...</span>
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-4 h-4" />
                    <span>生成BPMN流程</span>
                  </>
                )}
              </motion.button>
            ) : (
              <motion.button
                onClick={() => navigate('/cases')}
                className="px-4 py-2 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-300 flex items-center gap-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span>前往测试案例</span>
              </motion.button>
            )}
          </div>
        </div>
      </motion.header>

      {/* Stage Navigator */}
      <StageNavigator currentStage={3} />

      {/* Success Message */}
      <AnimatePresence>
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="max-w-5xl mx-auto w-full px-8 pt-6"
          >
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl flex items-start space-x-3">
              <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-700">BPMN流程生成成功！</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-8 py-8">
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
          {isGenerating ? (
            /* Loading State */
            <div className="flex flex-col items-center justify-center h-64">
              <div className="relative">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
                <SparklesIcon className="w-8 h-8 text-blue-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <p className="mt-4 text-gray-600 text-lg">AI正在生成BPMN流程图...</p>
              <p className="mt-2 text-gray-400 text-sm">这可能需要几秒钟</p>
            </div>
          ) : !bpmnXml ? (
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
                {testCases
                  ? 'AI将基于您的测试案例生成标准的BPMN 2.0流程定义，可直接导入到Flowable等流程引擎中使用。'
                  : '请先完成测试案例的生成，然后再生成BPMN流程图。'}
              </p>

              {testCases ? (
                <motion.button
                  onClick={handleGenerateBPMN}
                  disabled={isGenerating}
                  className="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <SparklesIcon className="w-5 h-5" />
                  <span>生成BPMN流程图</span>
                </motion.button>
              ) : (
                <motion.button
                  onClick={() => navigate('/cases')}
                  className="px-8 py-4 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 flex items-center space-x-2 mx-auto"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>前往测试案例</span>
                  <ArrowRightIcon className="w-5 h-5" />
                </motion.button>
              )}
            </motion.div>
          ) : (
            /* Display BPMN */
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-8"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">
                  {viewMode === 'diagram' ? 'BPMN 流程图' : 'BPMN 2.0 XML'}
                </h3>

                {/* View Mode Toggle */}
                <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
                  <motion.button
                    onClick={() => setViewMode('diagram')}
                    className={`px-4 py-2 rounded-md font-medium transition-all flex items-center gap-2 ${
                      viewMode === 'diagram'
                        ? 'bg-white text-blue-600 shadow-md'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Square3Stack3DIcon className="w-4 h-4" />
                    <span className="text-sm">流程图</span>
                  </motion.button>
                  <motion.button
                    onClick={() => setViewMode('xml')}
                    className={`px-4 py-2 rounded-md font-medium transition-all flex items-center gap-2 ${
                      viewMode === 'xml'
                        ? 'bg-white text-blue-600 shadow-md'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <CodeBracketIcon className="w-4 h-4" />
                    <span className="text-sm">XML代码</span>
                  </motion.button>
                </div>
              </div>

              {/* Content based on view mode */}
              {viewMode === 'diagram' ? (
                /* BPMN Diagram View */
                <div className="h-[900px]">
                  <BpmnViewer xml={bpmnXml} />
                </div>
              ) : (
                /* XML Code View */
                <div className="bg-gray-900 rounded-xl p-6 overflow-auto max-h-[900px]">
                  <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap break-words">
                    {bpmnXml}
                  </pre>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BPMNPage;

// Made with Bob
