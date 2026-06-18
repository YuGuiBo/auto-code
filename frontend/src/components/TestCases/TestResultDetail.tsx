import { FC, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TestCaseDetail, TestCaseDetailStep } from '../../services/api';
import {
  CheckCircleIcon,
  XCircleIcon,
  ChevronDownIcon,
  DocumentTextIcon,
  UserIcon,
  FlagIcon,
} from '@heroicons/react/24/outline';

interface TestResultDetailProps {
  caseDetails: TestCaseDetail[];
}

const StepIcon: FC<{ status: TestCaseDetailStep['status'] }> = ({ status }) => {
  switch (status) {
    case 'passed':
      return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
    case 'failed':
      return <XCircleIcon className="w-5 h-5 text-red-500" />;
    case 'completed':
      return <FlagIcon className="w-5 h-5 text-blue-500" />;
    default:
      return <DocumentTextIcon className="w-5 h-5 text-gray-400" />;
  }
};

const getStepLabel = (step: string): { icon: string; label: string; role: string } => {
  // 解析步骤描述，识别角色和动作
  const submitKeywords = ['提交', '申请', '发起'];
  const completeKeywords = ['流程完成', '流程终止', '流程结束'];

  if (completeKeywords.some(kw => step.includes(kw))) {
    return { icon: '🏁', label: step, role: '系统' };
  }
  if (submitKeywords.some(kw => step.includes(kw))) {
    return { icon: '📋', label: step, role: '申请人' };
  }

  // 审批步骤识别
  const roleMapping: Record<string, string> = {
    supervisor: '直接主管',
    pm: '项目经理',
    director: '部门经理',
    manager: '经理',
    hr: 'HR',
    finance: '财务',
    ceo: '总经理',
  };

  for (const [key, roleName] of Object.entries(roleMapping)) {
    if (step.toLowerCase().includes(key)) {
      return { icon: '👤', label: step, role: roleName };
    }
  }

  // 默认
  return { icon: '📌', label: step, role: '' };
};

export const TestResultDetail: FC<TestResultDetailProps> = ({ caseDetails }) => {
  const [expandedCases, setExpandedCases] = useState<Set<number>>(
    new Set(caseDetails.length <= 3 ? caseDetails.map((_, i) => i) : [0])
  );

  const toggleCase = (index: number) => {
    const newExpanded = new Set(expandedCases);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedCases(newExpanded);
  };

  if (!caseDetails || caseDetails.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <DocumentTextIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p className="text-sm">暂无详细的测试步骤数据</p>
        <p className="text-xs text-gray-400 mt-1">执行测试后将在此展示每个用例的详细流程</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {caseDetails.map((caseItem, index) => {
        const isExpanded = expandedCases.has(index);
        const isPassed = caseItem.status === 'passed';

        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`rounded-xl border overflow-hidden ${
              isPassed
                ? 'border-green-200 bg-green-50/50'
                : 'border-red-200 bg-red-50/50'
            }`}
          >
            {/* 用例标题 */}
            <div
              className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-white/50 transition-colors"
              onClick={() => toggleCase(index)}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center ${
                    isPassed ? 'bg-green-100' : 'bg-red-100'
                  }`}
                >
                  {isPassed ? (
                    <CheckCircleIcon className="w-4 h-4 text-green-600" />
                  ) : (
                    <XCircleIcon className="w-4 h-4 text-red-600" />
                  )}
                </div>
                <span className="font-medium text-sm text-gray-800">
                  {caseItem.case_name}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    isPassed
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {isPassed ? '通过' : '失败'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">
                  {caseItem.steps?.length || 0} 步骤
                </span>
                <motion.div
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDownIcon className="w-4 h-4 text-gray-400" />
                </motion.div>
              </div>
            </div>

            {/* 展开的步骤详情 */}
            <AnimatePresence>
              {isExpanded && caseItem.steps && caseItem.steps.length > 0 && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="border-t border-gray-200/50"
                >
                  <div className="px-4 py-3">
                    <div className="relative pl-6">
                      {/* 连接线 */}
                      <div className="absolute left-[11px] top-3 bottom-3 w-0.5 bg-gray-200" />

                      {caseItem.steps.map((step, stepIdx) => {
                        const stepInfo = getStepLabel(step.step);
                        return (
                          <div
                            key={stepIdx}
                            className="relative flex items-start gap-3 pb-4 last:pb-0"
                          >
                            {/* 步骤图标 */}
                            <div className="absolute -left-6 mt-0.5 z-10 bg-white rounded-full p-0.5">
                              <StepIcon status={step.status} />
                            </div>

                            {/* 步骤内容 */}
                            <div className="flex-1 ml-2">
                              <div className="flex items-center gap-2">
                                <span className="text-sm">{stepInfo.icon}</span>
                                <span className="text-sm font-medium text-gray-800">
                                  {step.step}
                                </span>
                              </div>
                              {stepInfo.role && (
                                <div className="flex items-center gap-1 mt-0.5">
                                  <UserIcon className="w-3 h-3 text-gray-400" />
                                  <span className="text-xs text-gray-500">
                                    {stepInfo.role}
                                  </span>
                                </div>
                              )}
                              {step.detail && (
                                <p className="text-xs text-gray-500 mt-1 bg-white/80 rounded px-2 py-1">
                                  💬 {step.detail}
                                </p>
                              )}
                            </div>

                            {/* 状态标签 */}
                            <div className="flex-shrink-0">
                              {step.status === 'passed' && (
                                <span className="text-xs text-green-600 font-medium">
                                  ✓ 通过
                                </span>
                              )}
                              {step.status === 'failed' && (
                                <span className="text-xs text-red-600 font-medium">
                                  ✗ 失败
                                </span>
                              )}
                              {step.status === 'completed' && (
                                <span className="text-xs text-blue-600 font-medium">
                                  ✓ 完成
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })}
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

export default TestResultDetail;
