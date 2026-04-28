import { FC, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TestCasesData } from '../../services/api';
import {
  ChevronDownIcon,
  CheckCircleIcon,
  BeakerIcon,
} from '@heroicons/react/24/outline';

interface TestCaseViewProps {
  testCasesData: TestCasesData;
}

export const TestCaseView: FC<TestCaseViewProps> = ({ testCasesData }) => {
  const test_cases = testCasesData.test_cases || [];
  const metadata = testCasesData.metadata;
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set([test_cases[0]?.id]));

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  };

  const categoryColors = {
    normal: { bg: 'bg-green-100', text: 'text-green-800', label: '正常流程' },
    branch: { bg: 'bg-purple-100', text: 'text-purple-800', label: '条件分支' },
    exception: { bg: 'bg-orange-100', text: 'text-orange-800', label: '异常场景' },
  };

  return (
    <div className="space-y-6">
      {/* 概览卡片 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <BeakerIcon className="w-6 h-6 text-green-600" />
          <h2 className="text-lg font-semibold text-gray-900">测试案例概览</h2>
        </div>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-xl p-4">
            <p className="text-sm text-blue-600 mb-1">总计</p>
            <p className="text-2xl font-bold text-blue-900">{metadata.total_cases || 0}</p>
          </div>
          <div className="bg-green-50 rounded-xl p-4">
            <p className="text-sm text-green-600 mb-1">正常流程</p>
            <p className="text-2xl font-bold text-green-900">{metadata.normal_cases || 0}</p>
          </div>
          <div className="bg-purple-50 rounded-xl p-4">
            <p className="text-sm text-purple-600 mb-1">条件分支</p>
            <p className="text-2xl font-bold text-purple-900">{metadata.branch_cases || 0}</p>
          </div>
          <div className="bg-orange-50 rounded-xl p-4">
            <p className="text-sm text-orange-600 mb-1">异常场景</p>
            <p className="text-2xl font-bold text-orange-900">{metadata.exception_cases || 0}</p>
          </div>
        </div>
      </motion.div>

      {/* 测试案例列表 */}
      {test_cases.map((testCase, index) => {
        const isExpanded = expandedIds.has(testCase.id);
        const colors = categoryColors[testCase.category as keyof typeof categoryColors] || categoryColors.normal;

        return (
          <motion.div
            key={testCase.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg overflow-hidden"
          >
            {/* 头部 */}
            <div
              className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleExpand(testCase.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
                      {colors.label}
                    </span>
                    <span className="text-sm text-gray-500">{testCase.id}</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{testCase.name}</h3>
                  <p className="text-sm text-gray-600">{testCase.description}</p>
                </div>
                <motion.div
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ChevronDownIcon className="w-6 h-6 text-gray-400" />
                </motion.div>
              </div>
            </div>

            {/* 展开内容 */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="border-t border-gray-200"
                >
                  <div className="p-6 space-y-6">
                    {/* 前置条件 */}
                    {Array.isArray(testCase.preconditions) && testCase.preconditions.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">前置条件</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {testCase.preconditions.map((condition, i) => (
                            <li key={i} className="text-sm text-gray-600">{condition}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* 测试步骤 */}
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-3">测试步骤</h4>
                      <div className="space-y-4">
                        {Array.isArray(testCase.steps) && testCase.steps.map((step, i) => (
                          <div key={i} className="flex gap-4">
                            <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                              {step.step_no}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-sm font-medium text-gray-900">{step.actor}</span>
                                <span className="text-sm text-gray-500">-</span>
                                <span className="text-sm text-gray-700">{step.action}</span>
                              </div>
                              {step.fields && Object.keys(step.fields).length > 0 && (
                                <div className="bg-gray-50 rounded-lg p-3 mb-2">
                                  <p className="text-xs text-gray-500 mb-2">输入数据：</p>
                                  <div className="grid grid-cols-2 gap-2">
                                    {Object.entries(step.fields).map(([key, value]) => (
                                      <div key={key} className="text-xs">
                                        <span className="text-gray-500">{key}:</span>
                                        <span className="text-gray-900 ml-1">{String(value)}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                              <div className="flex items-start gap-2">
                                <CheckCircleIcon className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                                <p className="text-sm text-gray-600">{step.expected_result}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* 后置条件 */}
                    {Array.isArray(testCase.postconditions) && testCase.postconditions.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">后置条件</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {testCase.postconditions.map((condition, i) => (
                            <li key={i} className="text-sm text-gray-600">{condition}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* 预期最终结果 */}
                    <div className="bg-green-50 rounded-xl p-4">
                      <h4 className="text-sm font-semibold text-green-900 mb-2">预期最终结果</h4>
                      <p className="text-sm text-green-700">{testCase.expected_final_result}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </div>
  );
};

export default TestCaseView;

// Made with Bob