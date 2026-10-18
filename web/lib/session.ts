export type SessionState = { subject: string; topic: string; conceptId: string; conceptName: string; diagnosis?: any; verification?: any; lesson?: any; practice?: any; retest?: any; topicDiagnosticResult?: any; studentId?: string; language?: 'en'|'kn'|'hi'; classCode?: string }

export function loadState<T = any>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback
  try { return JSON.parse(localStorage.getItem(key) || 'null') ?? fallback } catch { return fallback }
}

export function saveState(key: string, value: any) {
  if (typeof window !== 'undefined') localStorage.setItem(key, JSON.stringify(value))
}

export function getStudentId(): string {
  if (typeof window === 'undefined') return 'demo-student'
  try {
    const profile = JSON.parse(localStorage.getItem('learnlens_profile') || 'null')
    if (typeof profile?.studentId === 'string' && profile.studentId) return profile.studentId
    // Not joined yet: give this browser its own private id instead of the shared 'demo-student'.
    // shortcut: per-browser only, not per-person across devices; upgrade by adding real login.
    let id = localStorage.getItem('learnlens_anon_id')
    if (!id) { id = 'stu_anon_' + crypto.randomUUID().replace(/-/g, ''); localStorage.setItem('learnlens_anon_id', id) }
    return id
  } catch { return 'demo-student' }
}

export function getPreferredLanguage(): 'en'|'kn'|'hi' {
  if (typeof window === 'undefined') return 'en'
  try { const p = JSON.parse(localStorage.getItem('learnlens_profile') || 'null'); return p?.language === 'kn' || p?.language === 'hi' ? p.language : 'en' } catch { return 'en' }
}
