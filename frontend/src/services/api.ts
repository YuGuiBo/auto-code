import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface AnalysisMatrix {
  actors: string[];
  scenarios: string[];
  data: string[];
  rules: string[];
  exceptions: string[];
}

export interface ProcessAnalysisResponse {
  process_id: number;
  message: string;
  analysis_matrix: AnalysisMatrix | null;
  stage: string;
  suggestions?: string[];
}

export interface ProcessDetail {
  id: string;
  name: string;
  description: string;
  analysis_matrix: AnalysisMatrix;
  requirements_doc: string | null;
  user_cases: any[] | null;
  bpmn_xml: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

// 结构化需求文档类型
export interface FunctionalRequirement {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  actors: string[];
}

export interface NonFunctionalRequirement {
  id: string;
  category: string;
  description: string;
  criteria: string;
}

export interface BusinessRule {
  id: string;
  description: string;
  condition: string;
  action: string;
}

export interface DataRequirement {
  entity: string;
  attributes: string[];
  source: string;
}

export interface StructuredRequirements {
  title: string;
  overview: string;
  functional_requirements: FunctionalRequirement[];
  non_functional_requirements: NonFunctionalRequirement[];
  business_rules: BusinessRule[];
  data_requirements: DataRequirement[];
}

export interface RequirementDocument {
  processId: string;
  document: string;
}

export interface UserCase {
  id: string;
  title: string;
  description: string;
  steps: string[];
  preconditions: string[];
  postconditions: string[];
}

// API Functions
export const bpmnApi = {
  // Analyze user requirements
  analyzeRequirements: async (userInput: string): Promise<ProcessAnalysisResponse> => {
    const response = await api.post('/api/bpmn/analyze', {
      message: userInput,
      process_id: null,
      context: []
    });
    return response.data;
  },

  // Get process details
  getProcess: async (processId: string): Promise<ProcessDetail> => {
    const response = await api.get(`/api/bpmn/process/${processId}`);
    return response.data;
  },

  // Update analysis matrix
  updateMatrix: async (
    processId: string,
    matrix: AnalysisMatrix
  ): Promise<{ message: string }> => {
    const response = await api.put(`/api/bpmn/process/${processId}/matrix`, {
      analysis_matrix: matrix
    });
    return response.data;
  },

  // Generate requirements document
  generateRequirements: async (processId: string): Promise<any> => {
    const response = await api.post(`/api/bpmn/process/${processId}/requirements`);
    return response.data;
  },

  // Update requirements document
  updateRequirements: async (
    processId: string,
    requirements: StructuredRequirements
  ): Promise<any> => {
    const response = await api.put(`/api/bpmn/process/${processId}/requirements`, {
      structured_requirements: requirements,
    });
    return response.data;
  },

  // Generate user cases
  generateUserCases: async (processId: string): Promise<any> => {
    const response = await api.post(`/api/bpmn/process/${processId}/cases`);
    return response.data;
  },

  // Update user cases
  updateUserCases: async (
    processId: string,
    cases: UserCase[]
  ): Promise<{ message: string }> => {
    const response = await api.put(`/api/bpmn/process/${processId}/cases`, {
      user_cases: cases
    });
    return response.data;
  },

  // Generate BPMN
  generateBPMN: async (processId: string): Promise<{ bpmn_xml: string }> => {
    const response = await api.post(`/api/bpmn/process/${processId}/generate`);
    return response.data;
  },

  // List all processes
  listProcesses: async (): Promise<ProcessDetail[]> => {
    const response = await api.get('/api/bpmn/processes');
    return response.data;
  },
};

export default api;

// Made with Bob
