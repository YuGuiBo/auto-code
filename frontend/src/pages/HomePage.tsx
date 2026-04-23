import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../stores/authStore'
import { useSessionStore } from '../stores/sessionStore'

export default function HomePage() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const stage = useSessionStore((state) => state.stage)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="glass-effect border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold text-gray-900">BPM-Nova</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">欢迎, {user?.username}</span>
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-apple transition-colors"
              >
                退出登录
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Left Sidebar - Chat Panel */}
        <div className="w-96 border-r border-gray-200 bg-white flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">对话</h2>
            <p className="text-sm text-gray-500 mt-1">描述您的业务流程</p>
          </div>
          
          <div className="flex-1 p-4">
            <div className="text-center text-gray-500 mt-8">
              <p>Chat组件开发中...</p>
              <p className="text-sm mt-2">当前阶段: {stage}</p>
            </div>
          </div>
        </div>

        {/* Right Content Area */}
        <div className="flex-1 overflow-auto">
          <div className="max-w-5xl mx-auto p-8">
            <div className="card-apple p-8 text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                欢迎使用 BPM-Nova
              </h2>
              <p className="text-gray-600 mb-6">
                AI驱动的工作流设计工具，让流程设计变得简单高效
              </p>
              
              {/* Start Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/design')}
                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 transition-shadow mb-8"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                开始设计流程
              </motion.button>

              <div className="grid grid-cols-3 gap-4 mt-8">
                <div className="p-4 bg-blue-50 rounded-apple">
                  <div className="text-3xl mb-2">💬</div>
                  <h3 className="font-semibold text-gray-900">自然语言输入</h3>
                  <p className="text-sm text-gray-600 mt-1">用日常语言描述流程</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-apple">
                  <div className="text-3xl mb-2">🎨</div>
                  <h3 className="font-semibold text-gray-900">自动生成BPMN</h3>
                  <p className="text-sm text-gray-600 mt-1">AI自动创建流程图</p>
                </div>
                <div className="p-4 bg-pink-50 rounded-apple">
                  <div className="text-3xl mb-2">✅</div>
                  <h3 className="font-semibold text-gray-900">自动化测试</h3>
                  <p className="text-sm text-gray-600 mt-1">验证流程完整性</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Made with Bob
