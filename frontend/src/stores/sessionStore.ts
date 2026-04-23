import { create } from 'zustand'

export type ProcessStage = 'analysis' | 'bpmn' | 'test' | 'deploy'

export interface AnalysisMatrix {
  roles: string[]
  activities: string[]
  conditions: Array<{ condition: string; branches: string[] }>
  dataFields: Array<{ name: string; type: string; required: boolean }>
  exceptions: string[]
}

export interface RequirementsSpecification {
  overview: string
  functionalRequirements: string[]
  nonFunctionalRequirements: string[]
  businessRules: string[]
  userStories: string[]
}

export interface UserCase {
  id: string
  name: string
  actors: string[]
  preconditions: string[]
  mainFlow: string[]
  alternativeFlows: string[]
  postconditions: string[]
}

interface SessionState {
  processId: string | null
  stage: ProcessStage
  description: string
  matrix: AnalysisMatrix | null
  requirements: RequirementsSpecification | null
  userCases: UserCase[]
  bpmnXml: string | null
  
  setProcessId: (id: string) => void
  setStage: (stage: ProcessStage) => void
  setDescription: (description: string) => void
  setMatrix: (matrix: AnalysisMatrix) => void
  setRequirements: (requirements: RequirementsSpecification) => void
  setUserCases: (userCases: UserCase[]) => void
  setBpmnXml: (xml: string) => void
  reset: () => void
}

const initialState = {
  processId: null,
  stage: 'analysis' as ProcessStage,
  description: '',
  matrix: null,
  requirements: null,
  userCases: [],
  bpmnXml: null,
}

export const useSessionStore = create<SessionState>((set) => ({
  ...initialState,
  
  setProcessId: (id) => set({ processId: id }),
  setStage: (stage) => set({ stage }),
  setDescription: (description) => set({ description }),
  setMatrix: (matrix) => set({ matrix }),
  setRequirements: (requirements) => set({ requirements }),
  setUserCases: (userCases) => set({ userCases }),
  setBpmnXml: (bpmnXml) => set({ bpmnXml }),
  reset: () => set(initialState),
}))

// Made with Bob
