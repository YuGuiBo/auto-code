import { motion, AnimatePresence } from 'framer-motion';
import { FC, useState } from 'react';
import {
  ChevronDownIcon,
  ChevronUpIcon,
  UserIcon,
  CheckCircleIcon,
  ClipboardDocumentListIcon,
} from '@heroicons/react/24/outline';

// 实际的用例数据结构（来自后端）
interface ActualUserCase {
  id: string;
  title: string;
  actor: string;
  precondition: string;
  main_flow: string[];
  alternative_flow?: string[];
  postcondition?: string;
  priority?: string;
}

interface TimelineUserCaseViewProps {
  cases: ActualUserCase[];
  onEdit?: () => void;
}

const TimelineUserCaseView: FC<TimelineUserCaseViewProps> = ({ cases, onEdit }) => {
  const [expandedCaseId, setExpandedCaseId] = useState<string | null>(null);

  const toggleCase = (caseId: string) => {
    setExpandedCaseId(expandedCaseId === caseId ? null : caseId);
  };

  return (
    <div className="space-y-6">
      {/* Timeline Container */}
      <div className="relative">
        {/* Vertical Timeline Line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-200 via-purple-200 to-pink-200" />

        {/* Cases */}
        <div className="space-y-8">
          {cases.map((userCase, index) => (
            <motion.div
              key={userCase.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative pl-16"
            >
              {/* Timeline Node */}
              <div className="absolute left-3 top-3 w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-white" />
              </div>

              {/* Case Card */}
              <motion.div
                className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100"
                whileHover={{ scale: 1.01 }}
              >
                {/* Card Header */}
                <button
                  onClick={() => toggleCase(userCase.id)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50/50 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-md">
                      <UserIcon className="w-5 h-5 text-white" />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {userCase.title}
                      </h3>
                      <p className="text-sm text-gray-500 line-clamp-1">
                        {userCase.actor && `参与者：${userCase.actor}`}
                      </p>
                    </div>
                  </div>
                  <motion.div
                    animate={{ rotate: expandedCaseId === userCase.id ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {expandedCaseId === userCase.id ? (
                      <ChevronUpIcon className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDownIcon className="w-5 h-5 text-gray-400" />
                    )}
                  </motion.div>
                </button>

                {/* Expandable Content */}
                <AnimatePresence>
                  {expandedCaseId === userCase.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6 space-y-4 border-t border-gray-100">
                        {/* Actor */}
                        {userCase.actor && (
                          <div className="pt-4">
                            <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                              <UserIcon className="w-4 h-4 mr-2 text-blue-500" />
                              参与者
                            </h4>
                            <p className="text-sm text-gray-600 pl-6">
                              {userCase.actor}
                            </p>
                          </div>
                        )}

                        {/* Precondition */}
                        {userCase.precondition && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                              <CheckCircleIcon className="w-4 h-4 mr-2 text-green-500" />
                              前置条件
                            </h4>
                            <p className="text-sm text-gray-600 pl-6">
                              {userCase.precondition}
                            </p>
                          </div>
                        )}

                        {/* Main Flow */}
                        {userCase.main_flow && userCase.main_flow.length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                              <ClipboardDocumentListIcon className="w-4 h-4 mr-2 text-blue-500" />
                              主流程
                            </h4>
                            <ol className="space-y-2">
                              {userCase.main_flow.map((step, idx) => (
                                <li
                                  key={idx}
                                  className="text-sm text-gray-600 pl-6 relative"
                                >
                                  <span className="absolute left-0 w-5 h-5 rounded-full bg-blue-100 text-blue-600 text-xs flex items-center justify-center font-medium">
                                    {idx + 1}
                                  </span>
                                  {step}
                                </li>
                              ))}
                            </ol>
                          </div>
                        )}

                        {/* Alternative Flow */}
                        {userCase.alternative_flow && userCase.alternative_flow.length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                              <ClipboardDocumentListIcon className="w-4 h-4 mr-2 text-orange-500" />
                              备选流程
                            </h4>
                            <ol className="space-y-2">
                              {userCase.alternative_flow.map((step, idx) => (
                                <li
                                  key={idx}
                                  className="text-sm text-gray-600 pl-6 relative"
                                >
                                  <span className="absolute left-0 w-5 h-5 rounded-full bg-orange-100 text-orange-600 text-xs flex items-center justify-center font-medium">
                                    {idx + 1}
                                  </span>
                                  {step}
                                </li>
                              ))}
                            </ol>
                          </div>
                        )}

                        {/* Postcondition */}
                        {userCase.postcondition && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                              <CheckCircleIcon className="w-4 h-4 mr-2 text-purple-500" />
                              后置条件
                            </h4>
                            <p className="text-sm text-gray-600 pl-6">
                              {userCase.postcondition}
                            </p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Edit Button */}
      {onEdit && (
        <motion.button
          onClick={onEdit}
          className="w-full py-3 px-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          编辑用例
        </motion.button>
      )}
    </div>
  );
};

export default TimelineUserCaseView;

// Made with Bob
