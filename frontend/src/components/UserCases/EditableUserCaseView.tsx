import { FC, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PlusIcon,
  TrashIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

// 匹配后端实际返回的数据结构
interface ActualUserCase {
  id: string;
  title: string;
  actor: string;
  precondition: string;
  main_flow: string[];
  alternative_flow?: string[];
  postcondition?: string;
}

interface EditableUserCaseViewProps {
  cases: ActualUserCase[];
  onChange: (cases: ActualUserCase[]) => void;
}

const EditableUserCaseView: FC<EditableUserCaseViewProps> = ({
  cases,
  onChange,
}) => {
  const [expandedCases, setExpandedCases] = useState<Set<string>>(
    new Set(cases.map((c) => c.id))
  );

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedCases);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedCases(newExpanded);
  };

  const updateCase = (index: number, field: keyof ActualUserCase, value: any) => {
    const newCases = [...cases];
    newCases[index] = { ...newCases[index], [field]: value };
    onChange(newCases);
  };

  const addMainFlowStep = (caseIndex: number) => {
    const newCases = [...cases];
    newCases[caseIndex].main_flow = [
      ...newCases[caseIndex].main_flow,
      '新步骤',
    ];
    onChange(newCases);
  };

  const updateMainFlowStep = (
    caseIndex: number,
    stepIndex: number,
    value: string
  ) => {
    const newCases = [...cases];
    newCases[caseIndex].main_flow[stepIndex] = value;
    onChange(newCases);
  };

  const removeMainFlowStep = (caseIndex: number, stepIndex: number) => {
    const newCases = [...cases];
    newCases[caseIndex].main_flow = newCases[caseIndex].main_flow.filter(
      (_, i) => i !== stepIndex
    );
    onChange(newCases);
  };

  const addAlternativeFlowStep = (caseIndex: number) => {
    const newCases = [...cases];
    if (!newCases[caseIndex].alternative_flow) {
      newCases[caseIndex].alternative_flow = [];
    }
    newCases[caseIndex].alternative_flow!.push('新替代步骤');
    onChange(newCases);
  };

  const updateAlternativeFlowStep = (
    caseIndex: number,
    stepIndex: number,
    value: string
  ) => {
    const newCases = [...cases];
    if (newCases[caseIndex].alternative_flow) {
      newCases[caseIndex].alternative_flow![stepIndex] = value;
      onChange(newCases);
    }
  };

  const removeAlternativeFlowStep = (caseIndex: number, stepIndex: number) => {
    const newCases = [...cases];
    if (newCases[caseIndex].alternative_flow) {
      newCases[caseIndex].alternative_flow = newCases[
        caseIndex
      ].alternative_flow!.filter((_, i) => i !== stepIndex);
      onChange(newCases);
    }
  };

  const addNewCase = () => {
    const newCase: ActualUserCase = {
      id: `UC-${Date.now()}`,
      title: '新用例',
      actor: '用户',
      precondition: '前置条件',
      main_flow: ['步骤1'],
      alternative_flow: [],
      postcondition: '后置条件',
    };
    onChange([...cases, newCase]);
    setExpandedCases(new Set([...expandedCases, newCase.id]));
  };

  const removeCase = (index: number) => {
    const newCases = cases.filter((_, i) => i !== index);
    onChange(newCases);
  };

  return (
    <div className="space-y-4">
      <AnimatePresence>
        {cases.map((userCase, caseIndex) => {
          const isExpanded = expandedCases.has(userCase.id);

          return (
            <motion.div
              key={userCase.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-200"
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1 flex items-center space-x-3">
                    <button
                      onClick={() => toggleExpand(userCase.id)}
                      className="p-1 hover:bg-white/50 rounded-lg transition-colors"
                    >
                      {isExpanded ? (
                        <ChevronUpIcon className="w-5 h-5 text-gray-600" />
                      ) : (
                        <ChevronDownIcon className="w-5 h-5 text-gray-600" />
                      )}
                    </button>
                    <input
                      type="text"
                      value={userCase.title}
                      onChange={(e) =>
                        updateCase(caseIndex, 'title', e.target.value)
                      }
                      className="flex-1 text-lg font-semibold bg-transparent border-b-2 border-transparent hover:border-blue-300 focus:border-blue-500 focus:outline-none px-2 py-1 transition-colors"
                    />
                  </div>
                  <button
                    onClick={() => removeCase(caseIndex)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <TrashIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="p-6 space-y-6"
                  >
                    {/* Actor */}
                    <div>
                      <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                        <span className="text-blue-500 mr-2">👤</span>
                        参与者
                      </label>
                      <input
                        type="text"
                        value={userCase.actor}
                        onChange={(e) =>
                          updateCase(caseIndex, 'actor', e.target.value)
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    {/* Precondition */}
                    <div>
                      <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                        <span className="text-green-500 mr-2">✓</span>
                        前置条件
                      </label>
                      <textarea
                        value={userCase.precondition}
                        onChange={(e) =>
                          updateCase(caseIndex, 'precondition', e.target.value)
                        }
                        rows={2}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                    </div>

                    {/* Main Flow */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="flex items-center text-sm font-medium text-gray-700">
                          <span className="text-purple-500 mr-2">📋</span>
                          主流程
                        </label>
                        <button
                          onClick={() => addMainFlowStep(caseIndex)}
                          className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        >
                          <PlusIcon className="w-4 h-4" />
                          <span>添加步骤</span>
                        </button>
                      </div>
                      <div className="space-y-2">
                        {userCase.main_flow.map((step, stepIndex) => (
                          <div
                            key={stepIndex}
                            className="flex items-center space-x-2"
                          >
                            <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 text-blue-600 rounded-full text-sm font-medium">
                              {stepIndex + 1}
                            </span>
                            <input
                              type="text"
                              value={step}
                              onChange={(e) =>
                                updateMainFlowStep(
                                  caseIndex,
                                  stepIndex,
                                  e.target.value
                                )
                              }
                              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <button
                              onClick={() =>
                                removeMainFlowStep(caseIndex, stepIndex)
                              }
                              className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            >
                              <TrashIcon className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Alternative Flow */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="flex items-center text-sm font-medium text-gray-700">
                          <span className="text-orange-500 mr-2">🔀</span>
                          替代流程
                        </label>
                        <button
                          onClick={() => addAlternativeFlowStep(caseIndex)}
                          className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        >
                          <PlusIcon className="w-4 h-4" />
                          <span>添加步骤</span>
                        </button>
                      </div>
                      {userCase.alternative_flow &&
                      userCase.alternative_flow.length > 0 ? (
                        <div className="space-y-2">
                          {userCase.alternative_flow.map((step, stepIndex) => (
                            <div
                              key={stepIndex}
                              className="flex items-center space-x-2"
                            >
                              <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-orange-100 text-orange-600 rounded-full text-sm font-medium">
                                {stepIndex + 1}
                              </span>
                              <input
                                type="text"
                                value={step}
                                onChange={(e) =>
                                  updateAlternativeFlowStep(
                                    caseIndex,
                                    stepIndex,
                                    e.target.value
                                  )
                                }
                                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              />
                              <button
                                onClick={() =>
                                  removeAlternativeFlowStep(caseIndex, stepIndex)
                                }
                                className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                              >
                                <TrashIcon className="w-4 h-4" />
                              </button>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-400 italic">
                          暂无替代流程
                        </p>
                      )}
                    </div>

                    {/* Postcondition */}
                    <div>
                      <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                        <span className="text-pink-500 mr-2">🎯</span>
                        后置条件
                      </label>
                      <textarea
                        value={userCase.postcondition || ''}
                        onChange={(e) =>
                          updateCase(caseIndex, 'postcondition', e.target.value)
                        }
                        rows={2}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Add New Case Button */}
      <motion.button
        onClick={addNewCase}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-4 border-2 border-dashed border-gray-300 rounded-2xl text-gray-500 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50 transition-all flex items-center justify-center space-x-2"
      >
        <PlusIcon className="w-5 h-5" />
        <span className="font-medium">添加新用例</span>
      </motion.button>
    </div>
  );
};

export default EditableUserCaseView;

// Made with Bob
