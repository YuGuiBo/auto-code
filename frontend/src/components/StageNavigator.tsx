import { motion } from 'framer-motion';
import { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../stores/chatStore';
import {
  ChatBubbleLeftRightIcon,
  TableCellsIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CubeIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';

interface Stage {
  id: number;
  name: string;
  path: string;
  icon: typeof ChatBubbleLeftRightIcon;
}

const stages: Stage[] = [
  {
    id: 0,
    name: '分析矩阵',
    path: '/design',
    icon: TableCellsIcon,
  },
  {
    id: 1,
    name: '需求文档',
    path: '/requirements',
    icon: DocumentTextIcon,
  },
  {
    id: 2,
    name: '测试案例',
    path: '/cases',
    icon: UserGroupIcon,
  },
  {
    id: 3,
    name: 'BPMN流程',
    path: '/bpmn',
    icon: CubeIcon,
  },
];

interface StageNavigatorProps {
  currentStage: number;
}

export const StageNavigator: FC<StageNavigatorProps> = ({ currentStage }) => {
  const navigate = useNavigate();
  const { analysisMatrix, structuredRequirements, testCases } = useChatStore();

  // 判断阶段是否可访问
  const isStageAccessible = (stageId: number): boolean => {
    switch (stageId) {
      case 0: // 分析矩阵阶段始终可访问
        return true;
      case 1: // 需求文档需要有矩阵
        return !!analysisMatrix;
      case 2: // 测试案例需要有需求文档
        return !!structuredRequirements;
      case 3: // BPMN需要有测试案例
        return !!testCases && testCases.test_cases && testCases.test_cases.length > 0;
      default:
        return false;
    }
  };

  // 判断阶段是否已完成
  const isStageCompleted = (stageId: number): boolean => {
    switch (stageId) {
      case 0:
        return !!analysisMatrix;
      case 1:
        return !!structuredRequirements;
      case 2:
        return !!testCases && testCases.test_cases && testCases.test_cases.length > 0;
      case 3:
        return false; // BPMN是最后阶段，不需要完成标记
      default:
        return false;
    }
  };

  const handleStageClick = (stage: Stage) => {
    if (isStageAccessible(stage.id)) {
      navigate(stage.path);
    }
  };

  return (
    <div className="w-full bg-white/80 backdrop-blur-xl border-b border-gray-200 px-6 py-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between">
          {stages.map((stage, index) => {
            const Icon = stage.icon;
            const isAccessible = isStageAccessible(stage.id);
            const isCompleted = isStageCompleted(stage.id);
            const isCurrent = stage.id === currentStage;

            return (
              <div key={stage.id} className="flex items-center flex-1">
                {/* 阶段按钮 */}
                <motion.button
                  onClick={() => handleStageClick(stage)}
                  disabled={!isAccessible}
                  whileHover={isAccessible ? { scale: 1.05 } : {}}
                  whileTap={isAccessible ? { scale: 0.95 } : {}}
                  className={`
                    relative flex items-center gap-2 px-4 py-2 rounded-xl
                    transition-all duration-300 min-w-[140px]
                    ${
                      isCurrent
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/30'
                        : isCompleted
                        ? 'bg-green-500 text-white shadow-md'
                        : isAccessible
                        ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        : 'bg-gray-50 text-gray-400 cursor-not-allowed opacity-50'
                    }
                  `}
                >
                  {/* 激活指示器 */}
                  {isCurrent && (
                    <motion.div
                      layoutId="activeStage"
                      className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl"
                      transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                    />
                  )}

                  {/* 图标 */}
                  <div className="relative z-10">
                    {isCompleted ? (
                      <CheckIcon className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>

                  {/* 文字 */}
                  <span className="relative z-10 font-medium text-sm">
                    {stage.name}
                  </span>
                </motion.button>

                {/* 连接线 */}
                {index < stages.length - 1 && (
                  <div className="flex-1 h-0.5 mx-2 bg-gray-200 relative overflow-hidden">
                    {/* 进度填充 */}
                    {isCompleted && (
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: '100%' }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                        className="absolute inset-0 bg-gradient-to-r from-green-400 to-green-500"
                      />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// Made with Bob
