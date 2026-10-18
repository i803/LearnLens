'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowRight, BrainCircuit, FileText } from 'lucide-react'
import { api } from '@/lib/api'
import { getStudentId } from '@/lib/session'
import { conceptLabel, normalizeProgressData } from '@/components/ui-kit'

type Snap = { conceptId: string; name: string; diagnosis: string; evidence: string[] }

// Real data only: this browser's own latest saved diagnosis, or an honest empty state.
function latest(diagnoses: any[]): Snap | null {
  if (!diagnoses.length) return null
  // Supabase rows carry created_at (newest first); the in-memory fallback appends (newest last).
  const d = diagnoses[0]?.created_at ? diagnoses[0] : diagnoses[diagnoses.length - 1]
  const conceptId = String(d.weakestConceptId || d.weakest_concept_id || '')
  if (!conceptId) return null
  return {
    conceptId,
    name: String(d.weakestConceptName || conceptLabel(conceptId)),
    diagnosis: String(d.diagnosis || ''),
    evidence: Array.isArray(d.evidence) ? d.evidence.map(String).slice(0, 2) : [],
  }
}

export function SnapshotCard() {
  const [snap, setSnap] = useState<Snap | null | undefined>(undefined)
  useEffect(() => {
    api<any>(`/student/progress?studentId=${encodeURIComponent(getStudentId())}`)
      .then(r => setSnap(latest(normalizeProgressData(r).diagnoses)))
      .catch(() => setSnap(null))
  }, [])

  const href = snap ? `/student/verify?concept=${encodeURIComponent(snap.conceptId)}&name=${encodeURIComponent(snap.name)}` : '/student/work'
  return <div className="relative overflow-hidden rounded-[1.75rem] border border-[#e1e5f4] bg-white shadow-[0_24px_70px_rgba(44,53,101,0.12)]">
    <div className="flex items-center justify-between border-b border-[#edf0f6] px-5 py-4"><div className="flex items-center gap-2"><span className="size-2 rounded-full bg-[#50c4a3]" /><span className="text-xs font-bold uppercase tracking-[0.13em] text-[#7c88a0]">Learning snapshot</span></div>{snap && <span className="rounded-full bg-[#edf9f5] px-2.5 py-1 text-[11px] font-bold text-[#16856d]">Saved evidence</span>}</div>
    <div className="p-6 sm:p-8">
      <div className="flex items-start justify-between gap-4"><div><p className="text-sm font-medium text-[#7c88a0]">{snap ? 'Possible misconception' : 'No diagnosis yet'}</p><h2 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-[#17233f]">{snap === undefined ? 'Loading…' : snap ? snap.name : 'Start your first session'}</h2></div><span className="grid size-11 place-items-center rounded-2xl bg-[#f0f1ff] text-[#676bd6]"><BrainCircuit className="size-5" /></span></div>
      <div className="mt-7 rounded-2xl border border-[#e8eaf7] bg-[#fafaff] p-5">
        <div className="flex items-center gap-3"><span className="grid size-8 place-items-center rounded-lg bg-[#fff4dc] text-[#bd7c1d]"><FileText className="size-4" /></span><div><p className="text-sm font-semibold text-[#27334f]">{snap ? 'Evidence from your work' : 'Your results will appear here'}</p><p className="mt-0.5 text-xs text-[#7c88a0]">{snap ? 'Observed work, ready to review' : 'Nothing is shown until you have real results'}</p></div></div>
        <p className="mt-4 text-sm leading-6 text-[#64718a]">{snap === undefined ? ' ' : snap ? <>{snap.evidence.join(' ') || snap.diagnosis} LearnLens keeps this as a hypothesis until you verify it.</> : 'Upload a worksheet or answer a short diagnostic. LearnLens will then show a possible misconception, with the evidence behind it, on this card.'}</p>
      </div>
      <div className="mt-6 flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.13em] text-[#7c88a0]">Next best step</p><p className="mt-1 font-semibold text-[#27334f]">{snap ? 'Take a 3-question check' : 'Upload your work'}</p></div><Link href={href} aria-label={snap ? 'Take a 3-question check' : 'Upload your work'} className="grid size-10 place-items-center rounded-xl bg-[#17233f] text-white"><ArrowRight className="size-4" /></Link></div>
    </div>
  </div>
}
