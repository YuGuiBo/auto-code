import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PencilIcon,
  PlusIcon,
  TrashIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import {
  StructuredRequirements,
  FunctionalRequirement,
  NonFunctionalRequirement,
  BusinessRule,
  DataRequirement,
} from '../../services/api';

interface EditableRequirementsViewProps {
  requirements: StructuredRequirements;
  onChange: (requirements: StructuredRequirements) => void;
}

const EditableRequirementsView: React.FC<EditableRequirementsViewProps> = ({
  requirements,
  onChange,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingSection, setEditingSection] = useState<string | null>(null);

  // 确保所有字段都有默认值，并且都是数组类型
  const safeRequirements: StructuredRequirements = {
    title: requirements?.title || '',
    overview: requirements?.overview || '',
    functional_requirements: Array.isArray(requirements?.functional_requirements)
      ? requirements.functional_requirements
      : [],
    non_functional_requirements: Array.isArray(requirements?.non_functional_requirements)
      ? requirements.non_functional_requirements
      : [],
    business_rules: Array.isArray(requirements?.business_rules)
      ? requirements.business_rules
      : [],
    data_requirements: Array.isArray(requirements?.data_requirements)
      ? requirements.data_requirements.map(dr => ({
          ...dr,
          attributes: Array.isArray(dr.attributes) ? dr.attributes : []
        }))
      : [],
  };

  // 功能需求编辑
  const handleEditFR = (id: string, field: keyof FunctionalRequirement, value: any) => {
    const updated = safeRequirements.functional_requirements.map((req) =>
      req.id === id ? { ...req, [field]: value } : req
    );
    onChange({ ...safeRequirements, functional_requirements: updated });
  };

  const handleAddFR = () => {
    const currentReqs = safeRequirements.functional_requirements;
    const newId = `FR-${String(currentReqs.length + 1).padStart(3, '0')}`;
    const newReq: FunctionalRequirement = {
      id: newId,
      title: '新功能需求',
      description: '请输入描述',
      priority: 'medium',
      actors: [],
    };
    onChange({
      ...safeRequirements,
      functional_requirements: [...currentReqs, newReq],
    });
    setEditingId(newId);
    setEditingSection('fr');
  };

  const handleDeleteFR = (id: string) => {
    const updated = safeRequirements.functional_requirements.filter((req) => req.id !== id);
    onChange({ ...safeRequirements, functional_requirements: updated });
  };

  // 非功能需求编辑
  const handleEditNFR = (id: string, field: keyof NonFunctionalRequirement, value: any) => {
    const updated = safeRequirements.non_functional_requirements.map((req) =>
      req.id === id ? { ...req, [field]: value } : req
    );
    onChange({ ...safeRequirements, non_functional_requirements: updated });
  };

  const handleAddNFR = () => {
    const currentReqs = safeRequirements.non_functional_requirements;
    const newId = `NFR-${String(currentReqs.length + 1).padStart(3, '0')}`;
    const newReq: NonFunctionalRequirement = {
      id: newId,
      category: '性能',
      description: '请输入描述',
      criteria: '请输入验收标准',
    };
    onChange({
      ...safeRequirements,
      non_functional_requirements: [...currentReqs, newReq],
    });
    setEditingId(newId);
    setEditingSection('nfr');
  };

  const handleDeleteNFR = (id: string) => {
    const updated = safeRequirements.non_functional_requirements.filter((req) => req.id !== id);
    onChange({ ...safeRequirements, non_functional_requirements: updated });
  };

  // 业务规则编辑
  const handleEditBR = (id: string, field: keyof BusinessRule, value: any) => {
    const updated = safeRequirements.business_rules.map((rule) =>
      rule.id === id ? { ...rule, [field]: value } : rule
    );
    onChange({ ...safeRequirements, business_rules: updated });
  };

  const handleAddBR = () => {
    const currentRules = safeRequirements.business_rules;
    const newId = `BR-${String(currentRules.length + 1).padStart(3, '0')}`;
    const newRule: BusinessRule = {
      id: newId,
      description: '新业务规则',
      condition: '请输入触发条件',
      action: '请输入执行动作',
    };
    onChange({
      ...safeRequirements,
      business_rules: [...currentRules, newRule],
    });
    setEditingId(newId);
    setEditingSection('br');
  };

  const handleDeleteBR = (id: string) => {
    const updated = safeRequirements.business_rules.filter((rule) => rule.id !== id);
    onChange({ ...safeRequirements, business_rules: updated });
  };

  // 数据需求编辑
  const handleEditDR = (index: number, field: keyof DataRequirement, value: any) => {
    const updated = safeRequirements.data_requirements.map((data, i) =>
      i === index ? { ...data, [field]: value } : data
    );
    onChange({ ...safeRequirements, data_requirements: updated });
  };

  const handleAddDR = () => {
    const currentData = safeRequirements.data_requirements;
    const newData: DataRequirement = {
      entity: '新数据实体',
      attributes: ['属性1'],
      source: '数据来源',
    };
    onChange({
      ...safeRequirements,
      data_requirements: [...currentData, newData],
    });
  };

  const handleDeleteDR = (index: number) => {
    const updated = safeRequirements.data_requirements.filter((_, i) => i !== index);
    onChange({ ...safeRequirements, data_requirements: updated });
  };

  const priorityColors = {
    high: 'bg-red-100 text-red-700 border-red-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-green-100 text-green-700 border-green-200',
  };

  return (
    <div className="space-y-6">
      {/* 标题和概述 - 可编辑 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
      >
        <input
          type="text"
          value={safeRequirements.title}
          onChange={(e) => onChange({ ...safeRequirements, title: e.target.value })}
          className="text-2xl font-bold text-gray-900 mb-4 w-full bg-transparent border-b-2 border-transparent hover:border-blue-300 focus:border-blue-500 focus:outline-none transition-colors"
        />
        <textarea
          value={safeRequirements.overview}
          onChange={(e) => onChange({ ...safeRequirements, overview: e.target.value })}
          rows={3}
          className="w-full text-gray-600 leading-relaxed bg-transparent border-2 border-transparent hover:border-blue-300 focus:border-blue-500 focus:outline-none rounded-lg p-2 transition-colors resize-none"
        />
      </motion.div>

      {/* 功能需求 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">功能需求</h3>
          <button
            onClick={handleAddFR}
            className="flex items-center gap-2 px-3 py-1.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
          >
            <PlusIcon className="w-4 h-4" />
            添加
          </button>
        </div>
        <div className="space-y-4">
          <AnimatePresence>
            {safeRequirements.functional_requirements.map((req, index) => (
              <motion.div
                key={req.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100 group"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-mono text-blue-600 bg-white px-2 py-1 rounded">
                        {req.id}
                      </span>
                      <input
                        type="text"
                        value={req.title}
                        onChange={(e) => handleEditFR(req.id, 'title', e.target.value)}
                        className="flex-1 font-semibold text-gray-900 bg-transparent border-b border-transparent hover:border-blue-300 focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <textarea
                      value={req.description}
                      onChange={(e) => handleEditFR(req.id, 'description', e.target.value)}
                      rows={2}
                      className="w-full text-gray-700 text-sm bg-white/50 rounded-lg p-2 border border-transparent hover:border-blue-300 focus:border-blue-500 focus:outline-none resize-none"
                    />
                  </div>
                  <div className="flex items-center gap-2 ml-2">
                    <select
                      value={req.priority}
                      onChange={(e) =>
                        handleEditFR(req.id, 'priority', e.target.value as 'high' | 'medium' | 'low')
                      }
                      className={`text-xs px-2 py-1 rounded-full border ${
                        priorityColors[req.priority]
                      } focus:outline-none`}
                    >
                      <option value="high">高</option>
                      <option value="medium">中</option>
                      <option value="low">低</option>
                    </select>
                    <button
                      onClick={() => handleDeleteFR(req.id)}
                      className="p-1 text-red-500 hover:bg-red-100 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* 非功能需求 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">非功能需求</h3>
          <button
            onClick={handleAddNFR}
            className="flex items-center gap-2 px-3 py-1.5 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors text-sm"
          >
            <PlusIcon className="w-4 h-4" />
            添加
          </button>
        </div>
        <div className="space-y-4">
          <AnimatePresence>
            {safeRequirements.non_functional_requirements.map((req, index) => (
              <motion.div
                key={req.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100 group"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-mono text-purple-600 bg-white px-2 py-1 rounded">
                        {req.id}
                      </span>
                      <input
                        type="text"
                        value={req.category}
                        onChange={(e) => handleEditNFR(req.id, 'category', e.target.value)}
                        className="text-xs bg-white text-purple-700 px-2 py-1 rounded-full border border-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-300"
                      />
                    </div>
                    <textarea
                      value={req.description}
                      onChange={(e) => handleEditNFR(req.id, 'description', e.target.value)}
                      rows={2}
                      className="w-full text-gray-700 text-sm bg-white/50 rounded-lg p-2 border border-transparent hover:border-purple-300 focus:border-purple-500 focus:outline-none resize-none mb-2"
                    />
                    <textarea
                      value={req.criteria}
                      onChange={(e) => handleEditNFR(req.id, 'criteria', e.target.value)}
                      rows={1}
                      placeholder="验收标准"
                      className="w-full text-xs text-gray-600 bg-white/50 rounded-lg p-2 border border-transparent hover:border-purple-300 focus:border-purple-500 focus:outline-none resize-none"
                    />
                  </div>
                  <button
                    onClick={() => handleDeleteNFR(req.id)}
                    className="p-1 text-red-500 hover:bg-red-100 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity ml-2"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* 业务规则 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">业务规则</h3>
          <button
            onClick={handleAddBR}
            className="flex items-center gap-2 px-3 py-1.5 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm"
          >
            <PlusIcon className="w-4 h-4" />
            添加
          </button>
        </div>
        <div className="space-y-4">
          <AnimatePresence>
            {safeRequirements.business_rules.map((rule, index) => (
              <motion.div
                key={rule.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl p-4 border border-orange-100 group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-1">
                    <span className="text-sm font-mono text-orange-600 bg-white px-2 py-1 rounded">
                      {rule.id}
                    </span>
                    <input
                      type="text"
                      value={rule.description}
                      onChange={(e) => handleEditBR(rule.id, 'description', e.target.value)}
                      className="flex-1 text-gray-900 font-medium bg-transparent border-b border-transparent hover:border-orange-300 focus:border-orange-500 focus:outline-none"
                    />
                  </div>
                  <button
                    onClick={() => handleDeleteBR(rule.id)}
                    className="p-1 text-red-500 hover:bg-red-100 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity ml-2"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-white/50 rounded-lg p-3 border border-orange-100">
                    <p className="text-xs font-semibold text-gray-600 mb-1">触发条件</p>
                    <input
                      type="text"
                      value={rule.condition}
                      onChange={(e) => handleEditBR(rule.id, 'condition', e.target.value)}
                      className="w-full text-sm text-gray-700 bg-transparent border-b border-transparent hover:border-orange-300 focus:border-orange-500 focus:outline-none"
                    />
                  </div>
                  <div className="bg-white/50 rounded-lg p-3 border border-orange-100">
                    <p className="text-xs font-semibold text-gray-600 mb-1">执行动作</p>
                    <input
                      type="text"
                      value={rule.action}
                      onChange={(e) => handleEditBR(rule.id, 'action', e.target.value)}
                      className="w-full text-sm text-gray-700 bg-transparent border-b border-transparent hover:border-orange-300 focus:border-orange-500 focus:outline-none"
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* 数据需求 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-gray-200/50"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">数据需求</h3>
          <button
            onClick={handleAddDR}
            className="flex items-center gap-2 px-3 py-1.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
          >
            <PlusIcon className="w-4 h-4" />
            添加
          </button>
        </div>
        <div className="space-y-4">
          <AnimatePresence>
            {safeRequirements.data_requirements.map((data, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-100 group"
              >
                <div className="flex items-center justify-between mb-3">
                  <input
                    type="text"
                    value={data.entity}
                    onChange={(e) => handleEditDR(index, 'entity', e.target.value)}
                    className="flex-1 font-semibold text-gray-900 bg-transparent border-b border-transparent hover:border-green-300 focus:border-green-500 focus:outline-none"
                  />
                  <input
                    type="text"
                    value={data.source}
                    onChange={(e) => handleEditDR(index, 'source', e.target.value)}
                    className="text-xs bg-white text-green-700 px-2 py-1 rounded-full border border-green-200 focus:outline-none focus:ring-2 focus:ring-green-300 ml-2"
                  />
                  <button
                    onClick={() => handleDeleteDR(index)}
                    className="p-1 text-red-500 hover:bg-red-100 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity ml-2"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {(data.attributes || []).map((attr, i) => (
                    <input
                      key={i}
                      type="text"
                      value={attr}
                      onChange={(e) => {
                        const newAttrs = Array.isArray(data.attributes) ? [...data.attributes] : [];
                        newAttrs[i] = e.target.value;
                        handleEditDR(index, 'attributes', newAttrs);
                      }}
                      className="text-xs bg-white text-gray-700 px-3 py-1 rounded-full border border-green-200 focus:outline-none focus:ring-2 focus:ring-green-300"
                    />
                  ))}
                  <button
                    onClick={() => {
                      const newAttrs = [...data.attributes, '新属性'];
                      handleEditDR(index, 'attributes', newAttrs);
                    }}
                    className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full border border-green-200 hover:bg-green-200 transition-colors"
                  >
                    + 属性
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
};

export default EditableRequirementsView;

// Made with Bob
