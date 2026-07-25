import type { User } from './auth'

export interface AdminSummary {
  users: { total: number; patients: number; administrators: number }
  consultations: { total: number; in_progress: number; completed: number; cancelled: number }
  reports: number
}

export interface AdminConsultation {
  id: string
  patient: Pick<User, 'id' | 'full_name' | 'email'>
  status: string
  knowledge_version: string | null
  knowledge_fingerprint: string | null
  risk: { id: string; label: string; rank: number } | null
  created_at: string
  completed_at: string | null
}

export interface AuditItem {
  id: string
  action: string
  actor: Pick<User, 'id' | 'full_name' | 'email'> | null
  resource_type: string | null
  resource_id: string | null
  event_data: Record<string, unknown> | null
  created_at: string
}

export interface CollectionDiff {
  before: number
  after: number
  added: string[]
  removed: string[]
  changed: string[]
}

export interface KnowledgeVersion {
  id: string
  package_id: string | null
  schema_version: string | null
  content_version: string | null
  fingerprint: string | null
  title: string | null
  status: 'invalid' | 'validated' | 'published' | 'retired'
  is_valid: boolean
  is_active: boolean
  validation_report: {
    valid: boolean
    issues: { code: string; location: string; message: string }[]
  }
  diff_summary: {
    collections: Record<string, CollectionDiff>
    affected_rule_ids: string[]
    warnings: string[]
  } | null
  uploaded_at: string
  published_at: string | null
  retired_at: string | null
}

export interface AdminReport {
  consultation_id: string
  patient: User
  status: string
  knowledge: {
    package_id: string | null
    content_version: string | null
    fingerprint: string | null
  }
  result: Record<string, unknown> | null
  created_at: string
  completed_at: string | null
}
