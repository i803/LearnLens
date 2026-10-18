'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BrainCircuit, BookOpen, Gauge, BarChart3, Sparkles, X, Menu, CircleHelp, Target, FileText } from 'lucide-react'
import { getStudentId } from '@/lib/session'

export const navItems = [
  { href: '/student', label: 'Overview', icon: Gauge },
  { href: '/student/learn', label: 'Learn', icon: BookOpen },
  { href: '/student/work', label: 'My work', icon: FileText },
  { href: '/student/progress', label: 'Progress', icon: BarChart3 },
]

export const teacherItems = [
  { href: '/teacher', label: 'Class overview', icon: Gauge },
  { href: '/teacher/analytics', label: 'Insights', icon: BarChart3 },
]

export type ProgressData = { studentId: string; mastery: Record<string, number>; attempts: any[]; diagnoses: any[]; timeline?: any[]; persistence?: {source?: string; available?: boolean} }

export type TeacherData = { concepts: any[]; studentsTracked: number; persistence?: {source?: string; available?: boolean} }

export type HealthData = { status: string; aiEnabled?: boolean; demoMode?: boolean; aiConfigured?: boolean; model?: string; supabaseConfigured?: boolean; supabaseAvailable?: boolean }

export function normalizeProgressData(raw: any): ProgressData {
  return {
    studentId: String(raw?.studentId || getStudentId()),
    mastery: raw?.mastery && typeof raw.mastery === 'object' ? raw.mastery : {},
    attempts: Array.isArray(raw?.attempts) ? raw.attempts : [],
    diagnoses: Array.isArray(raw?.diagnoses) ? raw.diagnoses : [],
    timeline: Array.isArray(raw?.timeline) ? raw.timeline : [],
    persistence: raw?.persistence && typeof raw.persistence === 'object' ? raw.persistence : undefined,
  }
}

export function conceptLabel(id: string, fallback = 'Concept') {
  if (!id) return fallback
  return id.replace(/[-_]+/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export function Logo() {
  return <Link href="/" className="flex items-center gap-2.5 text-[#103c3b]">
    <span className="grid size-9 place-items-center rounded-xl bg-[#17233f] text-white"><Sparkles className="size-4" /></span>
    <span className="font-semibold tracking-[-0.03em]">LearnLens</span>
    <span className="rounded-full bg-[#eef0ff] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#676bd6]">AI</span>
  </Link>
}

export function Button({ children, variant = 'primary', onClick, href, className = '', disabled = false, type = 'button' }: { children: React.ReactNode; variant?: 'primary'|'quiet'|'outline'; onClick?: () => void; href?: string; className?: string; disabled?: boolean; type?: 'button'|'submit'|'reset' }) {
  const styles = variant === 'primary' ? 'bg-primary text-primary-foreground hover:bg-primary/90' : variant === 'outline' ? 'border border-border bg-card text-foreground hover:bg-accent' : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
  const content = <span className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors ${disabled ? 'cursor-not-allowed opacity-50' : styles} ${className}`}>{children}</span>
  if (href && !disabled) return <Link href={href}>{content}</Link>
  return <button type={type} onClick={onClick} disabled={disabled} aria-disabled={disabled}>{content}</button>
}

export function ProgressBar({ value }: { value: number }) {
  const safe = Math.max(0, Math.min(100, Number.isFinite(value) ? value : 0))
  return <div className="h-1.5 overflow-hidden rounded-full bg-secondary"><div className="h-full rounded-full bg-brand-teal transition-[width] duration-700" style={{ width: `${safe}%` }} /></div>
}

export function StatCard({ label, value, detail, icon: Icon, accent = 'green' }: { label: string; value: string; detail: string; icon: React.ElementType; accent?: 'green'|'gold' }) {
  return <div className="rounded-2xl border border-border bg-card p-5 shadow-sm"><div className="flex items-start justify-between gap-4"><div><p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">{label}</p><p className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-foreground">{value}</p></div><span className={`grid size-10 place-items-center rounded-xl ${accent === 'gold' ? 'bg-brand-gold/20 text-brand-gold' : 'bg-brand-sage/35 text-brand-teal'}`}><Icon className="size-5" /></span></div><p className="mt-3 text-sm text-muted-foreground">{detail}</p></div>
}

export function Shell({ children, teacher = false }: { children: React.ReactNode; teacher?: boolean }) {
  const pathname = usePathname(); const [open, setOpen] = useState(false); const items = teacher ? teacherItems : navItems
  return <div className="min-h-screen bg-background text-foreground">
    <header className="sticky top-0 z-30 border-b border-border/80 bg-background/95 backdrop-blur"><div className="mx-auto flex h-18 max-w-[1440px] items-center justify-between px-5 lg:px-10"><div className="flex items-center gap-8"><button className="lg:hidden" onClick={() => setOpen(!open)} aria-label="Toggle menu">{open ? <X /> : <Menu />}</button><Logo /><span className="hidden h-6 w-px bg-border lg:block" /><span className="hidden text-sm text-muted-foreground lg:block">{teacher ? 'Teacher workspace' : 'Student workspace'}</span></div><div className="flex items-center gap-3"><Link href="/feedback" className="hidden text-sm font-medium text-[#61746e] hover:text-[#103c3b] sm:block">Share feedback</Link><span className="grid size-9 place-items-center rounded-full bg-[#d3e4db] text-sm font-semibold text-[#245851]">DS</span></div></div></header>
    <div className="mx-auto flex max-w-[1440px] px-5 lg:px-10"><aside className={`${open ? 'block' : 'hidden'} absolute left-0 top-[73px] z-20 w-64 border-r border-border bg-background p-5 lg:static lg:block lg:w-60 lg:shrink-0 lg:border-0 lg:bg-transparent lg:px-0 lg:py-8 lg:pr-8`}><nav className="flex flex-col gap-1">{items.map(({href,label,icon:Icon})=><Link key={href} href={href} onClick={()=>setOpen(false)} className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${pathname===href?'bg-accent text-accent-foreground':'text-muted-foreground hover:bg-accent hover:text-accent-foreground'}`}><Icon className="size-4"/>{label}</Link>)}<div className="my-5 h-px bg-border"/>{!teacher&&<Link href="/student/privacy" onClick={()=>setOpen(false)} className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-[#758580] hover:bg-[#edf2ed]"><CircleHelp className="size-4"/>Privacy controls</Link>}<Link href="/" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-[#758580] hover:bg-[#edf2ed]"><CircleHelp className="size-4"/>How it works</Link></nav><div className="mt-10 rounded-2xl bg-primary p-4 text-primary-foreground"><p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#9bc5b5]">Your learning loop</p><div className="mt-3 flex items-center gap-2 text-sm"><span className="grid size-7 place-items-center rounded-full bg-[#2f655d]"><Target className="size-3.5"/></span><span>Diagnose → improve</span></div><p className="mt-3 text-xs leading-5 text-[#b7d1c7]">Every answer becomes evidence for what to learn next.</p></div></aside><main className="min-w-0 flex-1 py-8 lg:py-10">{children}</main></div>
  </div>
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: React.ReactNode }) { return <div className="mb-8 flex flex-col justify-between gap-5 border-b border-border pb-7 sm:flex-row sm:items-end"><div>{eyebrow && <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-brand-coral">{eyebrow}</p>}<h1 className="font-serif text-4xl leading-[1.05] tracking-[-0.055em] text-foreground sm:text-5xl">{title}</h1>{description&&<p className="mt-3 max-w-2xl text-base leading-7 text-muted-foreground">{description}</p>}</div>{action}</div> }

export function Thinking({ title='LearnLens is thinking', steps, error }: { title?: string; steps: string[]; error?: string }) { const [stage,setStage]=useState(0); useEffect(()=>{const t=setInterval(()=>setStage(s=>Math.min(steps.length-1,s+1)),1600);return()=>clearInterval(t)},[steps.length]); return <div className="rounded-2xl border border-[#dbe4dc] bg-white p-6"><div className="flex items-center gap-4"><div className="grid size-12 place-items-center rounded-full bg-[#e5f1ea] text-[#39756d]"><BrainCircuit className="size-6" /></div><div><p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#9b6c3e]">{title}</p><h3 className="mt-1 text-lg font-semibold text-[#183e3c]">{steps[stage]}</h3><p className="text-sm text-[#758580]">Creating a targeted learning step. This may take a moment.</p></div><div className="ml-auto"><span className="inline-block size-3 animate-pulse rounded-full bg-[#4e8b7c]" /></div></div><div className="mt-6 h-2 overflow-hidden rounded-full bg-[#e6ede7]"><div className="h-full bg-[#4e8b7c] transition-all duration-700" style={{width:`${Math.max(10,(stage+1)/steps.length*100)}%`}}/></div>{error&&<div className="mt-4 rounded-xl border border-[#f0cfc7] bg-[#fff3ef] p-3 text-sm text-[#8b463a]">{error}</div>}</div> }

