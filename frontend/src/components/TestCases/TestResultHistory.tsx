import { FC, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TestHistoryItem, bpmnApi } from '../../services/api';
import { TestResultDetail } from './TestResultDetail';
import {
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChevronDownIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  CodeBracketIcon,
  ListBulletIcon,
} from '@heroicons/react/24/outline';

interface TestResultHistoryProps {
  processId: string;
  onClose: () => void;
  onBack: () => void;
}

type DetailTab = 'steps' | 'output' | 'script';

export const TestResultHistory: FC<TestResultHistoryProps> = ({ processId, onClose, onBack }) => {
  const [history, setHistory] = useState<TestHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<DetailTab>('steps');

  useEffect(() => {
    loadHistory();
  }, [processId]);

  const loadHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await bpmnApi.getTestHistory(processId);
      setHistory(response.history);
      // 默认展开第一条
      if (response.history.length > 0) {
        setExpandedId(response.history[0].id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '获取测试历史失败');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '未知时间';
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
    setActiveTab('steps');
  };

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-8 bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-8"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <ClockIcon className="w-6 h-6 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900">测试历史记录</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-sm">
            收起 ✕
          </button>
        </div>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          <span className="ml-3 text-gray-500">加载中...</span>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="mt-8 bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-8"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <ClockIcon className="w-6 h-6 text-blue-500" />
          <h3 className="text-lg font-semibold text-gray-900">测试历史记录</h3>
          <span className="text-sm text-gray-500">({history.length} 条记录)</span>
        </div>
<div className="flex items-center gap-2">
          <button
            onClick={onBack}
            className="px-3 py-1.5 text-blue-600 hover:bg-blue-50 rounded-lg text-sm"
          >
            返回自动化测试结果
          </button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={loadHistory}
            className="p-2 text-gray-400 hover:text-blue-500 transition-colors"
            title="刷新"
          >
            <ArrowPathIcon className="w-5 h-5" />
          </motion.button>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-sm">
            收起 ✕
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Empty State */}
      {!error && history.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <ClockIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-lg font-medium">暂无测试记录</p>
          <p className="text-sm mt-2">执行「自动化测试」后，测试结果将在此处展示</p>
        </div>
      )}

      {/* History List */}
      <div className="space-y-4">
        {history.map((item, index) => {
          const isExpanded = expandedId === item.id;

          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`rounded-2xl border overflow-hidden transition-all ${
                isExpanded
                  ? 'border-blue-200 shadow-md'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {/* Summary Bar */}
              <div
                className={`flex items-center justify-between px-5 py-4 cursor-pointer transition-colors ${
                  isExpanded ? 'bg-blue-50/50' : 'bg-white hover:bg-gray-50'
                }`}
                onClick={() => toggleExpand(item.id)}
              >
                <div className="flex items-center gap-4">
                  {/* 状态图标 */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      item.all_passed
                        ? 'bg-green-100'
                        : 'bg-red-100'
                    }`}
                  >
                    {item.all_passed ? (
                      <CheckCircleIcon className="w-6 h-6 text-green-600" />
                    ) : (
                      <XCircleIcon className="w-6 h-6 text-red-600" />
                    )}
                  </div>

                  {/* 信息 */}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">
                        {item.all_passed ? '全部通过' : '存在失败'}
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          item.all_passed
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {item.passed_cases}/{item.total_cases}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <ClockIcon className="w-3.5 h-3.5 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {formatDate(item.validated_at)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 右侧 */}
                <div className="flex items-center gap-4">
                  {/* 通过率进度条 */}
                  <div className="hidden sm:flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          item.success_rate === 100
                            ? 'bg-green-500'
                            : item.success_rate >= 50
                            ? 'bg-amber-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${item.success_rate}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-10">
                      {item.success_rate.toFixed(0)}%
                    </span>
                  </div>

                  <motion.div
                    animate={{ rotate: isExpanded ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronDownIcon className="w-5 h-5 text-gray-400" />
                  </motion.div>
                </div>
              </div>

              {/* Expanded Detail */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="border-t border-gray-200"
                  >
                    <div className="p-5">
                      {/* Tab Navigation */}
                      <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1 mb-4">
                        <button
                          onClick={() => setActiveTab('steps')}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                            activeTab === 'steps'
                              ? 'bg-white text-blue-600 shadow-sm'
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          <ListBulletIcon className="w-4 h-4" />
                          详细流程
                        </button>
                        <button
                          onClick={() => setActiveTab('output')}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                            activeTab === 'output'
                              ? 'bg-white text-blue-600 shadow-sm'
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          <DocumentTextIcon className="w-4 h-4" />
                          执行日志
                        </button>
                        <button
                          onClick={() => setActiveTab('script')}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                            activeTab === 'script'
                              ? 'bg-white text-blue-600 shadow-sm'
                              : 'text-gray-600 hover:text-gray-900'
                          }`}
                        >
                          <CodeBracketIcon className="w-4 h-4" />
                          测试脚本
                        </button>
                      </div>

                      {/* Tab Content */}
                      {activeTab === 'steps' && (
                        <TestResultDetail caseDetails={item.case_details} />
                      )}

                      {activeTab === 'output' && (
                        <div className="bg-gray-900 rounded-xl p-4 overflow-auto max-h-[400px]">
                          {item.execution_output ? (
                            <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap">
                              {item.execution_output}
                            </pre>
                          ) : (
                            <p className="text-gray-500 text-sm">无执行输出</p>
                          )}
                          {item.execution_errors && (
                            <div className="mt-4 pt-4 border-t border-gray-700">
                              <p className="text-red-400 text-xs font-medium mb-2">错误信息：</p>
                              <pre className="text-sm text-red-300 font-mono whitespace-pre-wrap">
                                {item.execution_errors}
                              </pre>
                            </div>
                          )}
                        </div>
                      )}

                      {activeTab === 'script' && (
                        <div className="bg-gray-900 rounded-xl p-4 overflow-auto max-h-[400px]">
                          {item.test_script ? (
                            <pre className="text-sm text-blue-300 font-mono whitespace-pre-wrap">
                              {item.test_script}
                            </pre>
                          ) : (
                            <p className="text-gray-500 text-sm">无测试脚本</p>
                          )}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default TestResultHistory;
