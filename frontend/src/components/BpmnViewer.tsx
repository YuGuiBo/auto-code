import { FC, useEffect, useRef, useState } from 'react';
import BpmnJS from 'bpmn-js/lib/Viewer';
import { motion } from 'framer-motion';
import {
  MagnifyingGlassPlusIcon,
  MagnifyingGlassMinusIcon,
  ArrowsPointingOutIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import 'bpmn-js/dist/assets/diagram-js.css';
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn.css';

interface BpmnViewerProps {
  xml: string;
  className?: string;
}

export const BpmnViewer: FC<BpmnViewerProps> = ({ xml, className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<BpmnJS | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!containerRef.current) return;

    let viewer: BpmnJS | null = null;
    let mounted = true;

    // 加载 BPMN XML
    const loadBpmn = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // 确保容器已经渲染，添加小延迟
        await new Promise(resolve => setTimeout(resolve, 100));
        
        if (!mounted || !containerRef.current) return;
        
        // 创建 BPMN Viewer 实例
        viewer = new BpmnJS({
          container: containerRef.current,
          width: '100%',
          height: '100%',
        });

        viewerRef.current = viewer;
        
        // 直接导入 BPMN XML（后端 AI 已经生成了包含图形信息的完整 BPMN）
        await viewer.importXML(xml);
        
        if (!mounted) return;
        
        // 获取画布和事件总线
        const canvas = viewer.get('canvas') as any;
        const eventBus = viewer.get('eventBus') as any;
        
        // 手动实现鼠标滚轮缩放功能
        const container = containerRef.current;
        if (container) {
          const handleWheel = (e: WheelEvent) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            const currentZoom = canvas.zoom();
            const newZoom = Math.max(0.1, Math.min(4, currentZoom + delta));
            canvas.zoom(newZoom);
          };
          
          container.addEventListener('wheel', handleWheel, { passive: false });
          
          // 保存清理函数
          (viewer as any)._wheelHandler = () => {
            container.removeEventListener('wheel', handleWheel);
          };
        }
        
        // 手动实现画布拖动功能
        let isPanning = false;
        let startX = 0;
        let startY = 0;
        let lastX = 0;
        let lastY = 0;
        
        if (container) {
          const handleMouseDown = (e: MouseEvent) => {
            // 鼠标左键或中键都可以拖动
            if (e.button === 0 || e.button === 1) {
              // 检查是否点击在BPMN元素上（排除工具栏按钮）
              const target = e.target as HTMLElement;
              const isToolbarButton = target.closest('button');
              
              if (!isToolbarButton) {
                e.preventDefault();
                isPanning = true;
                startX = e.clientX;
                startY = e.clientY;
                const viewbox = canvas.viewbox();
                lastX = viewbox.x;
                lastY = viewbox.y;
                container.style.cursor = 'grabbing';
              }
            }
          };
          
          const handleMouseMove = (e: MouseEvent) => {
            if (isPanning) {
              e.preventDefault();
              const dx = startX - e.clientX;
              const dy = startY - e.clientY;
              const currentZoom = canvas.zoom();
              canvas.viewbox({
                x: lastX + dx / currentZoom,
                y: lastY + dy / currentZoom,
                width: canvas.viewbox().width,
                height: canvas.viewbox().height
              });
            }
          };
          
          const handleMouseUp = (e: MouseEvent) => {
            if (isPanning) {
              e.preventDefault();
              isPanning = false;
              container.style.cursor = 'grab';
            }
          };
          
          const handleMouseLeave = () => {
            if (isPanning) {
              isPanning = false;
              container.style.cursor = 'default';
            }
          };
          
          // 设置默认光标为可抓取
          container.style.cursor = 'grab';
          
          container.addEventListener('mousedown', handleMouseDown);
          document.addEventListener('mousemove', handleMouseMove);
          document.addEventListener('mouseup', handleMouseUp);
          container.addEventListener('mouseleave', handleMouseLeave);
          
          // 保存清理函数
          (viewer as any)._panHandlers = () => {
            container.removeEventListener('mousedown', handleMouseDown);
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            container.removeEventListener('mouseleave', handleMouseLeave);
            container.style.cursor = 'default';
          };
        }
        
        // 自动居中并适应画布
        canvas.zoom('fit-viewport', 'auto');
        
        setIsLoading(false);
        console.log('BPMN loaded successfully with custom pan and zoom');
      } catch (err: any) {
        console.error('Failed to load BPMN:', err);
        if (mounted) {
          setError(err.message || '加载 BPMN 流程图失败');
          setIsLoading(false);
        }
      }
    };

    loadBpmn();

    // 清理函数
    return () => {
      mounted = false;
      if (viewer) {
        try {
          // 清理自定义事件监听器
          if ((viewer as any)._wheelHandler) {
            (viewer as any)._wheelHandler();
          }
          if ((viewer as any)._panHandlers) {
            (viewer as any)._panHandlers();
          }
          viewer.destroy();
        } catch (e) {
          console.warn('Error destroying viewer:', e);
        }
      }
    };
  }, [xml]);

  // 缩放控制函数
  const handleZoomIn = () => {
    if (!viewerRef.current) return;
    const canvas = viewerRef.current.get('canvas') as any;
    const currentZoom = canvas.zoom();
    canvas.zoom(currentZoom + 0.1);
  };

  const handleZoomOut = () => {
    if (!viewerRef.current) return;
    const canvas = viewerRef.current.get('canvas') as any;
    const currentZoom = canvas.zoom();
    canvas.zoom(Math.max(0.1, currentZoom - 0.1));
  };

  const handleZoomReset = () => {
    if (!viewerRef.current) return;
    const canvas = viewerRef.current.get('canvas') as any;
    canvas.zoom('fit-viewport', 'auto');
  };

  const handleZoomActual = () => {
    if (!viewerRef.current) return;
    const canvas = viewerRef.current.get('canvas') as any;
    canvas.zoom(1);
  };

  return (
    <div className={`relative ${className}`}>
      {/* 工具栏 */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleZoomIn}
          className="p-2 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow border border-gray-200"
          title="放大"
        >
          <MagnifyingGlassPlusIcon className="w-5 h-5 text-gray-700" />
        </motion.button>
        
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleZoomOut}
          className="p-2 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow border border-gray-200"
          title="缩小"
        >
          <MagnifyingGlassMinusIcon className="w-5 h-5 text-gray-700" />
        </motion.button>
        
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleZoomReset}
          className="p-2 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow border border-gray-200"
          title="适应画布"
        >
          <ArrowsPointingOutIcon className="w-5 h-5 text-gray-700" />
        </motion.button>
        
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleZoomActual}
          className="p-2 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow border border-gray-200"
          title="实际大小"
        >
          <ArrowPathIcon className="w-5 h-5 text-gray-700" />
        </motion.button>
      </div>

      {/* BPMN 画布容器 */}
      <div
        ref={containerRef}
        className="w-full h-full bg-white rounded-xl"
        style={{ minHeight: '900px' }}
      />

      {/* 加载状态 */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-xl">
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-600">加载流程图中...</p>
          </div>
        </div>
      )}

      {/* 错误状态 */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-xl">
          <div className="max-w-md p-6 bg-red-50 border border-red-200 rounded-xl">
            <h3 className="text-lg font-semibold text-red-900 mb-2">加载失败</h3>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default BpmnViewer;