'use client'

import React, { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { AlertTriangle, ArrowDownToLine, ArrowRight, Check, Clipboard, Database, KeyRound, RefreshCw, ShieldCheck, Sparkles, Users, WandSparkles } from 'lucide-react'
import { api } from '@/lib/api'
import { loadState, saveState } from '@/lib/session'
import { TeacherData, Button, ProgressBar, StatCard, Shell, PageHeader, Thinking } from '@/components/ui-kit'

type StudentRow = { id: string; label: string; mastery: Record<string, number>; provisional: Record<string, boolean>; synthetic?: boolean; joinedAt?: string | null; language?: string; attempts?: number; lastActive?: string | null; average?: number | null }
type Concept = { id: string; name: string }
type Heatmap = { students: StudentRow[]; concepts: Concept[]; topMisconceptions: { tag: string; label: string; count: number }[]; synthetic: boolean; dataMode?: string; classCode: string; className: string; sampleNotice?: string; summary?: { joined: number; started: number; attempts: number; averageMastery: number | null }; persistence?: { source?: string; configured?: boolean; available?: boolean } }
type Reteach = { plan: { minutes: number; steps: { t: string; what: string }[]; groups: { misconception: string; studentLabels: string[]; activity: string }[]; checkQuestion: string }; provider: string; generatedByAI: boolean; synthetic: boolean }

const DEMO_CODE = 'CSE-A'
const DEMO_KEY = 'demo-teacher-key'
const fmt = (v?: string | null) => (v ? new Date(v).toLocaleString() : '—')

function teacherDataForClass(result: Heatmap): TeacherData {
  const concepts = result.concepts.flatMap(concept => {
    const scores = result.students
      .filter(student => student.mastery?.[concept.id] !== undefined)
      .map(student => Number(student.mastery[concept.id]))
      .filter(Number.isFinite)
    return scores.length ? [{
      conceptId: concept.id,
      conceptName: concept.name,
      averageMastery: Math.round(scores.reduce((total, score) => total + score, 0) / scores.length * 10) / 10,
      students: scores.length,
    }] : []
  })
  return {
    concepts,
    studentsTracked: result.students.length,
    persistence: {
      source: result.persistence?.source || (result.synthetic ? 'bundled demo' : 'classroom data'),
      available: result.persistence?.available ?? !result.synthetic,
    },
  }
}

export function TeacherPage({ analytics = false }: { analytics?: boolean }) {
  const [d, setD] = useState<TeacherData | null>(null)
  const [heatmap, setHeatmap] = useState<Heatmap | null>(null)
  const [reteach, setReteach] = useState<Reteach | null>(null)
  const [classCode, setClassCode] = useState('')
  const [teacherKey, setTeacherKey] = useState('')
  const [demoDataEnabled, setDemoDataEnabled] = useState(false)
  const [hosted, setHosted] = useState(false)
  const [persistenceConfigured, setPersistenceConfigured] = useState(false)
  const [className, setClassName] = useState('Year 1 Mathematics')
  const [teacherName, setTeacherName] = useState('Teacher')
  const [created, setCreated] = useState<{ classCode: string; className: string; teacherKey: string } | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [fb, setFb] = useState<{ responses: number; averageRating: number; recentComments: string[] } | null>(null)

  useEffect(() => {
    let active = true
    api<any>('/teacher/analytics').then(meta => {
      if (!active) return
      const hasDemo = Boolean(meta?.demoDataEnabled)
      setDemoDataEnabled(hasDemo)
      setHosted(Boolean(meta?.hosted))
      setPersistenceConfigured(Boolean(meta?.persistence?.configured))
      setD({ concepts: [], studentsTracked: 0, persistence: meta?.persistence || { source: 'unavailable', available: false } })

      // Sample student records are opened only when the backend explicitly says
      // this is an unconfigured local checkout. Hosted/configured instances never
      // guess a demo key or silently fall back to fictional students.
      const mine = loadState<{ code?: string; key?: string }>('learnlens_teacher_class', {})
      if (hasDemo) {
        setClassCode(DEMO_CODE)
        setTeacherKey(DEMO_KEY)
        void loadHeatmap(DEMO_CODE, DEMO_KEY)
      } else if (mine.code && mine.key) {
        setClassCode(mine.code)
        setTeacherKey(mine.key)
        void loadHeatmap(mine.code, mine.key)
      } else {
        setClassCode('')
        setTeacherKey('')
        setHeatmap(null)
        setNotice('Real-data mode is active. Enter the class code and teacher key, or create a classroom. No sample students are loaded.')
      }
    }).catch(e => {
      if (!active) return
      setD({ concepts: [], studentsTracked: 0, persistence: { source: 'unavailable', available: false } })
      setError(e instanceof Error ? e.message : 'Could not connect to the teacher data service.')
    })
    return () => { active = false }
  }, [])

  // Live roster: re-read a real class every 10s so new joins and progress show up without a manual refresh.
  useEffect(() => {
    if (!heatmap || heatmap.synthetic || !classCode || !teacherKey) return
    const t = setInterval(() => {
      api<Heatmap>(`/teacher/classes/${encodeURIComponent(classCode)}/heatmap`, { headers: { 'X-Teacher-Key': teacherKey } })
        .then(result => { setHeatmap(result); setD(teacherDataForClass(result)) })
        .catch(() => {})
    }, 10000)
    return () => clearInterval(t)
  }, [heatmap?.synthetic, classCode, teacherKey])

  async function loadHeatmap(code = classCode, key = teacherKey) {
    if (!code.trim() || !key.trim()) {
      setError('Enter both the class code and teacher key to load a classroom.')
      return
    }
    setBusy(true); setError(''); setNotice(''); setReteach(null)
    try {
      const result = await api<Heatmap>(`/teacher/classes/${encodeURIComponent(code.trim())}/heatmap`, { headers: { 'X-Teacher-Key': key.trim() } })
      api<any>(`/feedback/summary?classCode=${encodeURIComponent(code.trim())}`, { headers: { 'X-Teacher-Key': key.trim() } }).then(setFb).catch(() => setFb(null))
      setHeatmap(result)
      setD(teacherDataForClass(result))
      setClassCode(code.trim().toUpperCase())
      setTeacherKey(key.trim())
      if (!result.synthetic) saveState('learnlens_teacher_class', { code: code.trim().toUpperCase(), key: key.trim() })
      setNotice(result.synthetic ? 'Illustrative classroom loaded. These are not real student measurements.' : 'Classroom learning signals loaded for this class.')
    } catch (e) {
      setHeatmap(null)
      setFb(null)
      setD({ concepts: [], studentsTracked: 0, persistence: { source: 'unavailable', available: false } })
      setError(e instanceof Error ? e.message : 'Could not load class heatmap.')
    } finally { setBusy(false) }
  }

  async function createClass(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setError(''); setNotice('')
    try {
      const result = await api<any>('/teacher/classes', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ className, teacherName }) })
      setCreated(result); setClassCode(result.classCode); setTeacherKey(result.teacherKey); setHeatmap(null); await loadHeatmap(result.classCode, result.teacherKey); setNotice('Class created. Save the teacher key now; the server stores only its hash.')
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not create class.') } finally { setBusy(false) }
  }

  async function makeReteachPlan() {
    setBusy(true); setError('')
    try { setReteach(await api<Reteach>(`/teacher/classes/${encodeURIComponent(classCode)}/reteach-plan`, { method: 'POST', headers: { 'X-Teacher-Key': teacherKey } })) }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not make reteach plan.') } finally { setBusy(false) }
  }

  function exportCsv() {
    if (!heatmap) return
    const rows = heatmap.students.flatMap(s => heatmap.concepts.map(c => [s.label, c.name, s.mastery?.[c.id] === undefined ? '' : Math.round(Number(s.mastery[c.id])), s.mastery?.[c.id] === undefined ? 'Not started' : s.provisional?.[c.id] ? 'Provisional' : 'Confirmed']))
    const csv = [['Student nickname', 'Concept', 'Mastery probability (%)', 'Status'], ...rows].map(row => row.map(v => { const text = String(v); return `"${(/^[=+\-@]/.test(text) ? "'" + text : text).replaceAll('"', '""')}"` }).join(',')).join('\r\n')
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' })); const a = document.createElement('a'); a.href = url; a.download = `learnlens-${classCode.toLowerCase()}-heatmap.csv`; a.click(); URL.revokeObjectURL(url)
  }

  const sorted = useMemo(() => [...(d?.concepts || [])].sort((a, b) => Number(a.averageMastery) - Number(b.averageMastery)), [d])
  if (!d) return <Shell teacher><Thinking steps={['Reading class evidence', 'Aggregating concepts', 'Preparing teacher insight']} /></Shell>

  return <Shell teacher>
    <PageHeader eyebrow={analytics ? 'Class insights' : 'Teacher classroom'} title={analytics ? 'Turn class signals into a next move.' : 'See the room. Plan the response.'} description="LearnLens keeps the teacher in the loop: inspect evidence, spot a shared misconception, then choose what happens next." action={<Link href={analytics ? '/teacher' : '/teacher/analytics'} className="inline-flex items-center gap-2 text-sm font-semibold text-[#39756d]">{analytics ? 'Class overview' : 'Open insights'} <ArrowRight className="size-4" /></Link>} />

    <div className="grid gap-4 md:grid-cols-3">
      <StatCard label="Students tracked" value={String(d.studentsTracked)} detail="Saved progress records" icon={Users} />
      <StatCard label="Concepts observed" value={String(d.concepts.length)} detail="Across saved mastery" icon={Database} />
      <StatCard label="Priority concept" value={sorted[0]?.conceptName || 'None yet'} detail={sorted[0] ? `${Math.round(sorted[0].averageMastery)}% average mastery` : 'Waiting for evidence'} icon={AlertTriangle} accent="gold" />
    </div>

    <section className="mt-4 rounded-2xl border border-[#dbe4dc] bg-white p-5">
      <h2 className="font-semibold">Student feedback</h2>
      {fb && fb.responses > 0 ? <><p className="mt-1 text-sm text-[#61746e]">{fb.responses} responses · average rating {fb.averageRating}/5</p><ul className="mt-3 space-y-2 text-sm">{fb.recentComments.map((c, i) => <li key={i} className="rounded-lg bg-[#f6f4ee] p-3">{c}</li>)}</ul></> : <p className="mt-1 text-sm text-[#61746e]">No feedback yet from this class. Students who joined with your class code can submit it at /feedback.</p>}
    </section>

    <section className="mt-6 rounded-2xl border border-[#dbe4dc] bg-white p-5">
      <div className="flex items-start gap-3"><Database className="mt-0.5 size-5 shrink-0 text-[#39756d]" /><div>
        <h2 className="font-semibold text-[#183e3c]">{demoDataEnabled ? 'Classroom access' : 'Real classroom data'}</h2>
        <p className="mt-1 text-sm leading-6 text-[#61746e]">{demoDataEnabled ? 'The offline sample is enabled for this local checkout. Enter another class code and teacher key to open a real classroom instead.' : 'Synthetic student records are disabled. Only students who join one of your real class codes and generate learning evidence can appear here.'}</p>
        {hosted && !persistenceConfigured && <p className="mt-2 text-sm leading-6 text-[#8b463a]">Before using the hosted site, configure <code>SUPABASE_URL</code> and <code>SUPABASE_SECRET_KEY</code> in the backend environment. Class creation and student joining are blocked until durable storage is available.</p>}
      </div></div>
      <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_auto]">
        <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Class code<input id="classCode" value={classCode} onChange={e => setClassCode(e.target.value.toUpperCase())} placeholder="e.g. LL-7F2K9" className="mt-2 block w-full rounded-xl border border-[#cbd9cf] bg-[#fbfcfa] px-3 py-2.5 text-sm font-normal text-[#183e3c]" /></label>
        <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Teacher key<input id="teacherKey" value={teacherKey} onChange={e => setTeacherKey(e.target.value)} type="password" autoComplete="off" placeholder="Private teacher key" className="mt-2 block w-full rounded-xl border border-[#cbd9cf] bg-[#fbfcfa] px-3 py-2.5 text-sm font-normal text-[#183e3c]" /></label>
        <div className="flex items-end"><Button onClick={() => loadHeatmap()} disabled={busy || !classCode.trim() || !teacherKey.trim()}><RefreshCw className="size-4" />Load class</Button></div>
      </div>
      {notice && <p className="mt-4 rounded-xl bg-[#edf5ef] p-3 text-sm text-[#39756d]">{notice}</p>}
      {error && <p role="alert" className="mt-4 rounded-xl bg-[#fff3ef] p-3 text-sm text-[#8b463a]">{error}</p>}
    </section>

    {heatmap && <section className="mt-8 rounded-[26px] border border-border bg-card p-6 sm:p-8">
      <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#9b6c3e]">Class roster</p><h2 className="mt-1 text-xl font-semibold text-[#183e3c]">{heatmap.className || heatmap.classCode}</h2><p className="mt-1 text-sm text-muted-foreground">{heatmap.synthetic ? 'Sample class with synthetic students. Create your own class below to see real students.' : 'Students appear here the moment they join with this code. Updates every 10 seconds.'}</p></div><div className="rounded-xl bg-[#f1f6f1] px-4 py-3 text-right"><p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">Class code to share</p><p className="font-mono text-2xl font-semibold tracking-wider text-[#183e3c]">{heatmap.classCode}</p><button type="button" onClick={() => navigator.clipboard?.writeText(`${window.location.origin}/join (class code ${heatmap.classCode})`)} className="mt-1 inline-flex items-center gap-1 text-xs font-semibold text-[#39756d]"><Clipboard className="size-3" />Copy join instructions</button></div></div>
      {heatmap.summary && <div className="mt-5 grid gap-3 sm:grid-cols-4">{[['Joined', heatmap.summary.joined], ['Started learning', heatmap.summary.started], ['Answers recorded', heatmap.summary.attempts], ['Class average', heatmap.summary.averageMastery === null ? '—' : `${Math.round(heatmap.summary.averageMastery)}%`]].map(([l, v]) => <div key={String(l)} className="rounded-xl border border-border p-4"><p className="text-xs text-muted-foreground">{l}</p><p className="mt-1 text-2xl font-semibold text-[#183e3c]">{v}</p></div>)}</div>}
      <div className="mt-5 overflow-x-auto rounded-2xl border border-border"><table className="w-full min-w-[640px] text-left text-sm"><thead className="bg-muted/60 text-xs uppercase tracking-wide text-muted-foreground"><tr><th className="p-3">Nickname</th><th className="p-3">Joined</th><th className="p-3">Language</th><th className="p-3">Answers</th><th className="p-3">Last active</th><th className="p-3">Avg mastery</th><th className="p-3">Status</th></tr></thead><tbody>{heatmap.students.length === 0 && <tr><td colSpan={7} className="p-4 text-muted-foreground">No students yet. Share the class code and ask them to open /join.</td></tr>}{heatmap.students.map(s => { const avg = s.average ?? null; const status = !s.attempts && !Object.keys(s.mastery || {}).length && !heatmap.synthetic ? 'Joined, not started' : avg === null ? (heatmap.synthetic ? 'Sample' : 'No mastery yet') : avg >= 75 ? 'Strong' : avg >= 50 ? 'Watch' : 'Needs reteach'; return <tr key={s.id} className="border-t border-[#e8eee8]"><td className="p-3 font-medium text-[#345b54]">{s.label}</td><td className="p-3">{fmt(s.joinedAt)}</td><td className="p-3 uppercase">{s.language || '—'}</td><td className="p-3">{s.attempts ?? '—'}</td><td className="p-3">{fmt(s.lastActive)}</td><td className="p-3">{avg === null ? '—' : `${Math.round(avg)}%`}</td><td className="p-3">{status}</td></tr> })}</tbody></table></div>
    </section>}

    <section className="mt-8 overflow-hidden rounded-[26px] border border-border bg-card shadow-[0_18px_45px_rgba(25,60,55,0.05)]">
      <div className="border-b border-[#e5ece6] bg-[#f1f6f1] px-6 py-6 sm:px-8"><div className="flex flex-wrap items-start justify-between gap-5"><div><div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-[#9b6c3e]"><span className="grid size-7 place-items-center rounded-lg bg-card text-[#39756d]"><Sparkles className="size-3.5" /></span> Evidence workspace</div><h2 className="mt-3 text-2xl font-semibold tracking-[-0.03em] text-[#183e3c]">What does the class need next?</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">Compare student × concept mastery. A provisional signal is a useful lead, not a final judgment.</p></div><Button variant="outline" onClick={exportCsv} disabled={!heatmap}><ArrowDownToLine className="size-4" />Export evidence</Button></div>
        <div className="mt-6 flex flex-wrap gap-2"><span className="rounded-full bg-[#dfeee5] px-3 py-1.5 text-xs font-semibold text-[#39756d]">75–100 · Strong</span><span className="rounded-full bg-[#fbf0d6] px-3 py-1.5 text-xs font-semibold text-[#8a6732]">50–74 · Watch</span><span className="rounded-full bg-[#f8e4df] px-3 py-1.5 text-xs font-semibold text-[#8b463a]">0–49 · Reteach</span></div>
      </div>
      <div className="p-6 sm:p-8">
        {heatmap && <>
          <div className="mt-6 overflow-x-auto rounded-2xl border border-border"><table className="w-full min-w-[760px] border-collapse text-left text-sm"><caption className="sr-only">Student by concept mastery heatmap. Values are provisional unless marked confirmed.</caption><thead className="bg-muted/60"><tr><th className="p-4 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Student</th>{heatmap.concepts.map(c => <th key={c.id} className="p-4 text-xs font-semibold text-muted-foreground">{c.name}</th>)}</tr></thead><tbody>{heatmap.students.map(student => <tr key={student.id} className="border-t border-[#e8eee8]"><th className="whitespace-nowrap p-4 font-medium text-[#345b54]">{student.label}<span className="mt-1 block text-[10px] font-normal text-[#82908b]">{student.synthetic || heatmap.synthetic ? 'SYNTHETIC DEMO' : 'Nickname only'}</span></th>{heatmap.concepts.map(concept => { if (student.mastery?.[concept.id] === undefined) return <td key={concept.id} className="p-2"><div className="rounded-xl border border-dashed border-[#cbd9cf] p-3 text-xs text-muted-foreground">Not started</div></td>; const value = Number(student.mastery?.[concept.id] || 0); const provisional = student.provisional?.[concept.id] !== false; const tone = value >= 75 ? ['#e0efe5', '#bfdac9'] : value >= 50 ? ['#fbf0d6', '#ead7ab'] : ['#f8e4df', '#e7c4bd']; return <td key={concept.id} className="p-2"><div className="rounded-xl border p-3" style={{ backgroundColor: tone[0], borderColor: tone[1] }}><div className="flex items-center justify-between gap-2"><span className="font-semibold text-[#345b54]">{Math.round(value)}%</span>{provisional ? <span className="rounded-full bg-card/70 px-1.5 py-0.5 text-[10px] text-muted-foreground">P</span> : <Check className="size-3.5 text-[#39756d]" />}</div><div className="mt-2 h-1.5 overflow-hidden rounded-full bg-card/70"><div className="h-full rounded-full bg-[#39756d]" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} /></div><p className="mt-1.5 text-[10px] text-muted-foreground">{provisional ? 'Provisional' : 'Confirmed'}</p></div></td> })}</tr>)}</tbody></table></div>
          <p className="mt-3 text-xs leading-5 text-[#82908b]">{heatmap.sampleNotice || 'Names are nicknames only. Review records before making instructional decisions.'}</p>
          <div className="mt-7 grid gap-5 lg:grid-cols-[0.8fr_1.2fr]"><div className="rounded-2xl bg-[#f6f4ee] p-5"><p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#9b6c3e]">Shared signals</p><h3 className="mt-2 font-semibold text-[#183e3c]">Top misconceptions</h3><div className="mt-4 flex flex-col gap-3">{(heatmap.topMisconceptions || []).map(item => <div key={item.tag} className="flex items-center justify-between gap-3 rounded-xl bg-card px-3 py-3"><span className="text-sm text-[#345b54]">{item.label}</span><span className="rounded-full bg-[#f8e4df] px-2 py-1 text-xs font-semibold text-[#8b463a]">{item.count} students</span></div>)}</div></div><div className="rounded-2xl border border-border p-5"><div className="flex items-start justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#9b6c3e]">Next intervention</p><h3 className="mt-2 font-semibold text-[#183e3c]">Make a reteach plan</h3><p className="mt-1 text-sm leading-6 text-muted-foreground">Generate a small-group starting point from the class evidence. You stay in control of the final plan.</p></div><WandSparkles className="size-5 text-[#39756d]" /></div><Button className="mt-5" onClick={makeReteachPlan} disabled={busy}><WandSparkles className="size-4" />{busy ? 'Working…' : 'Draft reteach plan'}</Button></div></div>
          {reteach && <div className="mt-5 rounded-2xl border border-[#bcd8c7] bg-[#f1f8f3] p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#39756d]">Suggested plan · {reteach.plan.minutes} minutes</p><h3 className="mt-2 text-lg font-semibold text-[#183e3c]">A focused response for this class</h3></div><span className="rounded-full bg-card px-3 py-1 text-xs font-semibold text-[#39756d]">{reteach.generatedByAI ? 'AI-assisted' : 'Rule-based'}</span></div><div className="mt-4 grid gap-3 sm:grid-cols-3">{reteach.plan.steps.map(step => <div key={step.t} className="rounded-xl bg-card p-4"><p className="text-xs font-semibold uppercase tracking-wide text-[#9b6c3e]">{step.t}</p><p className="mt-2 text-sm leading-5 text-[#345b54]">{step.what}</p></div>)}</div><p className="mt-4 rounded-xl bg-card p-4 text-sm text-[#345b54]"><strong>Check for transfer:</strong> {reteach.plan.checkQuestion}</p></div>}
        </>}
      </div>
    </section>

    <section className="mt-8 rounded-[26px] border border-border bg-card p-6 sm:p-8"><div className="flex items-center gap-3"><span className="grid size-10 place-items-center rounded-xl bg-[#e5f1ea] text-[#39756d]"><ShieldCheck className="size-5" /></span><div><p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#9b6c3e]">Set up a real class</p><h2 className="mt-1 text-xl font-semibold text-[#183e3c]">Create a private classroom code</h2></div></div><p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">Share the class code with students and keep the teacher key private. The server stores only a hash of the key.</p><form onSubmit={createClass} className="mt-5 grid gap-4 sm:grid-cols-3"><label className="text-xs font-semibold text-muted-foreground">Class name<input required minLength={2} maxLength={80} value={className} onChange={e => setClassName(e.target.value)} className="mt-2 block w-full rounded-xl border border-[#cbd9cf] px-3 py-2.5 text-sm font-normal text-[#183e3c]" /></label><label className="text-xs font-semibold text-muted-foreground">Teacher name<input required minLength={1} maxLength={50} value={teacherName} onChange={e => setTeacherName(e.target.value)} className="mt-2 block w-full rounded-xl border border-[#cbd9cf] px-3 py-2.5 text-sm font-normal text-[#183e3c]" /></label><div className="flex items-end"><Button type="submit" disabled={busy}><Users className="size-4" />Create class</Button></div></form>{created && <div className="mt-5 rounded-2xl border border-[#ead7ab] bg-[#fffaf1] p-4"><p className="font-semibold text-[#604c37]">Save this teacher key now</p><div className="mt-3 grid gap-2 sm:grid-cols-2"><div className="rounded-xl bg-card p-3"><p className="text-xs uppercase tracking-wide text-[#82908b]">Class code</p><p className="mt-1 text-xl font-semibold text-[#183e3c]">{created.classCode}</p></div><div className="rounded-xl bg-card p-3"><p className="flex items-center gap-1 text-xs uppercase tracking-wide text-[#82908b]"><KeyRound className="size-3.5" />Teacher key</p><p className="mt-1 break-all font-mono text-sm text-[#183e3c]">{created.teacherKey}</p></div></div></div>}</section>

    <section className="mt-8 rounded-[26px] border border-border bg-card p-6 sm:p-8"><p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#9b6c3e]">Aggregate view</p><h2 className="mt-2 text-xl font-semibold text-[#183e3c]">Concept overview</h2><div className="mt-5 grid gap-5 md:grid-cols-2">{sorted.map(c => <div key={c.conceptId}><div className="mb-2 flex items-center justify-between gap-4"><span className="text-sm font-medium text-[#345b54]">{c.conceptName}</span><span className="text-xs text-muted-foreground">{Number(c.averageMastery).toFixed(0)}% · {c.students} students</span></div><ProgressBar value={Number(c.averageMastery)} /></div>)}</div><p className="mt-5 text-xs leading-5 text-[#82908b]">Aggregates are limited to the currently loaded classroom. They remain empty until that class has saved mastery evidence.</p></section>
  </Shell>
}

export default TeacherPage
