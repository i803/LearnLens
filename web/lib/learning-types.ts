export type PersistenceStatus = { source?: string; available?: boolean }
export type ProgressData = { studentId: string; mastery: Record<string, number>; attempts: any[]; diagnoses: any[]; timeline?: any[]; persistence?: PersistenceStatus }
export type HealthData = { status: string; aiEnabled?: boolean; demoMode?: boolean; aiConfigured?: boolean; model?: string; supabaseConfigured?: boolean; supabaseAvailable?: boolean }
