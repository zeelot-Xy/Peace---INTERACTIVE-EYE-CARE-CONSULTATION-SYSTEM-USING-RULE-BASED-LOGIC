export type ConsultationStatus = 'in_progress' | 'completed' | 'cancelled'

export interface ChoiceOption {
  value: string
  label: string
}

export interface ConsultationQuestion {
  id: string
  fact_id: string
  prompt: string
  help_text: string | null
  answer_type: 'yes_no' | 'integer' | 'single_choice'
  required: boolean
  safety_critical: boolean
  options: ChoiceOption[]
  citation_ids: string[]
}

export interface KnowledgeItem {
  id?: string
  label?: string
  name?: string
  title?: string
  possible_indication_label?: string
  summary?: string
  limitations?: string
  message?: string
  action_window?: string
  rank?: number
  urgency?: string
  risk_label?: string
  organization?: string
  url?: string
  rationale?: string
  explanation?: string
  rule_id?: string
}

export interface SafetyAlert {
  requires_immediate_action: true
  risk: KnowledgeItem
  red_flags: KnowledgeItem[]
  recommendations: KnowledgeItem[]
  disclaimer: string
}

export interface SavedAnswer {
  question_id: string
  fact_id: string
  answer: boolean | number | string
  question: ConsultationQuestion
}

export interface Consultation {
  id: string
  status: ConsultationStatus
  revision: number
  knowledge: {
    package_id: string
    content_version: string
    fingerprint: string
  }
  progress: {
    resolved: number
    total_applicable: number
    percentage: number
  }
  next_question: ConsultationQuestion | null
  answers: SavedAnswer[]
  skipped_question_ids: string[]
  safety_alert: SafetyAlert | null
  created_at: string
  updated_at: string
  completed_at: string | null
  cancelled_at: string | null
}

export interface HistoryItem {
  id: string
  status: ConsultationStatus
  revision: number
  knowledge_version: string
  created_at: string
  updated_at: string
  completed_at: string | null
  cancelled_at: string | null
  risk: KnowledgeItem | null
}

export interface ConsultationResult {
  outcome_state: string
  completeness_state: string
  knowledge: Consultation['knowledge']
  overall_risk: KnowledgeItem | null
  matched_rules: KnowledgeItem[]
  possible_indications: KnowledgeItem[]
  recommendations: KnowledgeItem[]
  red_flags: KnowledgeItem[]
  evidence: KnowledgeItem[]
  inference_trace: KnowledgeItem[]
  disclaimer: string
  match_score_notice: string
}
