import React from 'react';
import { motion } from 'framer-motion';
import {
  DocumentTextIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  CubeIcon,
  TableCellsIcon,
} from '@heroicons/react/24/outline';
import {
  StructuredRequirements,
  FunctionalRequirement,
  NonFunctionalRequirement,
  BusinessRule,
  DataRequirement,
} from '../../services/api';

interface StructuredRequirementsViewProps {
  requirements: StructuredRequirements | null;
  isLoading?: boolean;
}

const StructuredRequirementsView: React.FC<StructuredRequirementsViewProps> = ({
  requirements,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!requirements) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12"
      >
        <DocumentTextIcon className="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <p className="text-gray-500 text-lg">暂无需求文档</p>
        <p className="text-gray-400 text-sm mt-2">请先完成分析矩阵，然后生成需求文档</p>
      </motion.div>
    );
  }

  const priorityColors = {
    high: 'bg-red-100 text-red-700 border-red-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-green-100 text-green-700 border-green-200',
  };

  const priorityLabels = {
    high: '高',
    medium: '中',
    low: '低',
  };

  return (
    <div className="space-y-6">
      {/* 标题和概述 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
      >
        <h2 className="text-2xl font-bold text-gray-900 mb-4">{requirements.title}</h2>
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-600 leading-relaxed">{requirements.overview}</p>
        </div>
      </motion.div>

      {/* 功能需求 */}
      {requirements.functional_requirements && requirements.functional_requirements.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <CheckCircleIcon className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">功能需求</h3>
          </div>
          <div className="space-y-4">
            {requirements.functional_requirements.map((req: FunctionalRequirement, index: number) => (
              <motion.div
                key={req.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.05 }}
                className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono text-blue-600 bg-white px-2 py-1 rounded">
                      {req.id}
                    </span>
                    <h4 className="font-semibold text-gray-900">{req.title}</h4>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full border ${
                      priorityColors[req.priority]
                    }`}
                  >
                    {priorityLabels[req.priority]}
                  </span>
                </div>
                <p className="text-gray-700 text-sm mb-3">{req.description}</p>
                {req.actors && Array.isArray(req.actors) && req.actors.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {req.actors.map((actor: string, i: number) => (
                      <span
                        key={i}
                        className="text-xs bg-white text-blue-700 px-2 py-1 rounded-full border border-blue-200"
                      >
                        {actor}
                      </span>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* 非功能需求 */}
      {requirements.non_functional_requirements &&
        requirements.non_functional_requirements.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-purple-100 rounded-lg">
                <ShieldCheckIcon className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">非功能需求</h3>
            </div>
            <div className="space-y-4">
              {requirements.non_functional_requirements.map(
                (req: NonFunctionalRequirement, index: number) => (
                  <motion.div
                    key={req.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-mono text-purple-600 bg-white px-2 py-1 rounded">
                        {req.id}
                      </span>
                      <span className="text-xs bg-white text-purple-700 px-2 py-1 rounded-full border border-purple-200">
                        {req.category}
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm mb-2">{req.description}</p>
                    <div className="bg-white/50 rounded-lg p-2 border border-purple-100">
                      <p className="text-xs text-gray-600">
                        <span className="font-semibold">验收标准：</span>
                        {req.criteria}
                      </p>
                    </div>
                  </motion.div>
                )
              )}
            </div>
          </motion.div>
        )}

      {/* 业务规则 */}
      {requirements.business_rules && requirements.business_rules.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-orange-100 rounded-lg">
              <CubeIcon className="w-6 h-6 text-orange-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">业务规则</h3>
          </div>
          <div className="space-y-4">
            {requirements.business_rules.map((rule: BusinessRule, index: number) => (
              <motion.div
                key={rule.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.05 }}
                className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl p-4 border border-orange-100"
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-sm font-mono text-orange-600 bg-white px-2 py-1 rounded">
                    {rule.id}
                  </span>
                  <p className="text-gray-900 font-medium">{rule.description}</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-white/50 rounded-lg p-3 border border-orange-100">
                    <p className="text-xs font-semibold text-gray-600 mb-1">触发条件</p>
                    <p className="text-sm text-gray-700">{rule.condition}</p>
                  </div>
                  <div className="bg-white/50 rounded-lg p-3 border border-orange-100">
                    <p className="text-xs font-semibold text-gray-600 mb-1">执行动作</p>
                    <p className="text-sm text-gray-700">{rule.action}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* 数据需求 */}
      {requirements.data_requirements && requirements.data_requirements.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <TableCellsIcon className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">数据需求</h3>
          </div>
          <div className="space-y-4">
            {requirements.data_requirements.map((data: DataRequirement, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.05 }}
                className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-100"
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{data.entity}</h4>
                  <span className="text-xs bg-white text-green-700 px-2 py-1 rounded-full border border-green-200">
                    {data.source}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {data.attributes && Array.isArray(data.attributes) && data.attributes.map((attr: string, i: number) => (
                    <span
                      key={i}
                      className="text-xs bg-white text-gray-700 px-3 py-1 rounded-full border border-green-200"
                    >
                      {attr}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default StructuredRequirementsView;

// Made with Bob
