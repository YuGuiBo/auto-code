import { create } from 'zustand';
import { Message } from '../components/Chat';
import { bpmnApi, AnalysisMatrix, StructuredRequirements, UserCase } from '../services/api';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  isSaving: boolean;
  isGenerating: boolean;
  currentProcessId: string | null;
  analysisMatrix: AnalysisMatrix | null;
  structuredRequirements: StructuredRequirements | null;
  userCases: UserCase[] | null;
  error: string | null;
  saveSuccess: boolean;

  // Actions
  addMessage: (content: string, role: 'user' | 'assistant') => void;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  setAnalysisMatrix: (matrix: AnalysisMatrix) => void;
  updateAnalysisMatrix: (matrix: AnalysisMatrix) => Promise<void>;
  setStructuredRequirements: (requirements: StructuredRequirements) => void;
  generateRequirements: () => Promise<void>;
  updateRequirements: (requirements: StructuredRequirements) => Promise<void>;
  setUserCases: (cases: UserCase[]) => void;
  generateUserCases: () => Promise<void>;
  updateUserCases: (cases: UserCase[]) => Promise<void>;
  setError: (error: string | null) => void;
  setSaveSuccess: (success: boolean) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  isSaving: false,
  isGenerating: false,
  currentProcessId: null,
  analysisMatrix: null,
  structuredRequirements: null,
  userCases: null,
  error: null,
  saveSuccess: false,

  addMessage: (content: string, role: 'user' | 'assistant') => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random()}`,
      content,
      role,
      timestamp: new Date(),
    };
    set((state) => ({
      messages: [...state.messages, newMessage],
    }));
  },

  sendMessage: async (content: string) => {
    const { addMessage } = get();

    // Add user message
    addMessage(content, 'user');

    // Set loading state
    set({ isLoading: true, error: null });

    try {
      // Call API to analyze requirements
      const response = await bpmnApi.analyzeRequirements(content);

      // Add AI response
      addMessage(response.message, 'assistant');

      // Update process ID and analysis matrix
      set({
        currentProcessId: response.process_id.toString(),
        analysisMatrix: response.analysis_matrix,
        isLoading: false,
      });
    } catch (error: any) {
      console.error('Failed to send message:', error);
      
      // Extract error message
      let errorMessage = '抱歉，处理您的请求时出现了错误。请稍后重试。';
      
      if (error.response?.data?.detail) {
        // Handle FastAPI validation errors (array of error objects)
        if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail
            .map((err: any) => `${err.loc?.join('.')}: ${err.msg}`)
            .join('; ');
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      addMessage(errorMessage, 'assistant');
      set({
        error: errorMessage,
        isLoading: false,
      });
    }
  },

  clearMessages: () => {
    set({
      messages: [],
      currentProcessId: null,
      analysisMatrix: null,
      error: null,
    });
  },

  setAnalysisMatrix: (matrix: AnalysisMatrix) => {
    set({ analysisMatrix: matrix });
  },

  updateAnalysisMatrix: async (matrix: AnalysisMatrix) => {
    const { currentProcessId } = get();
    
    if (!currentProcessId) {
      set({ error: '没有活动的流程ID' });
      return;
    }

    set({ isSaving: true, error: null, saveSuccess: false });

    try {
      await bpmnApi.updateMatrix(currentProcessId, matrix);
      set({
        analysisMatrix: matrix,
        isSaving: false,
        saveSuccess: true,
      });

      // Reset success message after 3 seconds
      setTimeout(() => {
        set({ saveSuccess: false });
      }, 3000);
    } catch (error: any) {
      console.error('Failed to update matrix:', error);
      
      let errorMessage = '保存失败，请稍后重试。';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string'
          ? error.response.data.detail
          : '保存失败';
      }
      
      set({
        error: errorMessage,
        isSaving: false,
        saveSuccess: false,
      });
    }
  },

  setStructuredRequirements: (requirements: StructuredRequirements) => {
    set({ structuredRequirements: requirements });
  },

  generateRequirements: async () => {
    const { currentProcessId } = get();
    
    if (!currentProcessId) {
      set({ error: '没有活动的流程ID' });
      return;
    }

    set({ isGenerating: true, error: null });

    try {
      const response = await bpmnApi.generateRequirements(currentProcessId);
      console.log('Generate requirements response:', response);
      set({
        structuredRequirements: response.structured_requirements,
        isGenerating: false,
      });
    } catch (error: any) {
      console.error('Failed to generate requirements:', error);
      
      let errorMessage = '生成需求文档失败，请稍后重试。';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string'
          ? error.response.data.detail
          : '生成需求文档失败';
      }
      
      set({
        error: errorMessage,
        isGenerating: false,
      });
    }
  },

  updateRequirements: async (requirements: StructuredRequirements) => {
    const { currentProcessId } = get();
    
    if (!currentProcessId) {
      set({ error: '没有活动的流程ID' });
      return;
    }

    set({ isSaving: true, error: null, saveSuccess: false });

    try {
      await bpmnApi.updateRequirements(currentProcessId, requirements);
      set({
        structuredRequirements: requirements,
        isSaving: false,
        saveSuccess: true,
      });

      // Reset success message after 3 seconds
      setTimeout(() => {
        set({ saveSuccess: false });
      }, 3000);
    } catch (error: any) {
      console.error('Failed to update requirements:', error);
      
      let errorMessage = '保存需求文档失败，请稍后重试。';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string'
          ? error.response.data.detail
          : '保存需求文档失败';
      }
      
      set({
        error: errorMessage,
        isSaving: false,
        saveSuccess: false,
      });
    }
  },

  setUserCases: (cases: UserCase[]) => {
    set({ userCases: cases });
  },

  generateUserCases: async () => {
    const { currentProcessId } = get();
    
    if (!currentProcessId) {
      set({ error: '没有活动的流程ID' });
      return;
    }

    set({ isGenerating: true, error: null });

    try {
      const response = await bpmnApi.generateUserCases(currentProcessId);
      console.log('Generate user cases response:', response);
      // 后端返回的是ProcessResponse，user_cases在response.user_cases中
      set({
        userCases: response.user_cases || [],
        isGenerating: false,
      });
    } catch (error: any) {
      console.error('Failed to generate user cases:', error);
      
      let errorMessage = '生成用户用例失败，请稍后重试。';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string'
          ? error.response.data.detail
          : '生成用户用例失败';
      }
      
      set({
        error: errorMessage,
        isGenerating: false,
      });
    }
  },

  updateUserCases: async (cases: UserCase[]) => {
    const { currentProcessId } = get();
    
    if (!currentProcessId) {
      set({ error: '没有活动的流程ID' });
      return;
    }

    set({ isSaving: true, error: null, saveSuccess: false });

    try {
      await bpmnApi.updateUserCases(currentProcessId, cases);
      set({
        userCases: cases,
        isSaving: false,
        saveSuccess: true,
      });

      // Reset success message after 3 seconds
      setTimeout(() => {
        set({ saveSuccess: false });
      }, 3000);
    } catch (error: any) {
      console.error('Failed to update user cases:', error);
      
      let errorMessage = '保存用户用例失败，请稍后重试。';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string'
          ? error.response.data.detail
          : '保存用户用例失败';
      }
      
      set({
        error: errorMessage,
        isSaving: false,
        saveSuccess: false,
      });
    }
  },

  setError: (error: string | null) => {
    set({ error });
  },

  setSaveSuccess: (success: boolean) => {
    set({ saveSuccess: success });
  },
}));

// Made with Bob
