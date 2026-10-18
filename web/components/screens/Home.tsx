'use client'

import React, { useEffect, useMemo, useRef, useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { ArrowRight, BarChart3, BookOpen, BrainCircuit, Check, ChevronRight, CircleHelp, FileCheck2, FileText, Flame, Gauge, Menu, MoreHorizontal, Plus, RefreshCw, Search, Sparkles, Target, Upload, Users, X, AlertTriangle, Clock3, Pencil, RotateCcw, Send, Database, Activity } from 'lucide-react'
import { api, slugify } from '@/lib/api'
import { getStudentId, loadState, saveState, type SessionState } from '@/lib/session'

import { ProgressData, TeacherData, HealthData, normalizeProgressData, conceptLabel, Logo, Button, ProgressBar, StatCard, Shell, PageHeader, Thinking } from '@/components/ui-kit'

export function Home(){
  const [progress,setProgress]=useState<ProgressData|null>(null)
  const [health,setHealth]=useState<HealthData|null>(null)
  useEffect(()=>{
    Promise.all([
      api<ProgressData>(`/student/progress?studentId=${encodeURIComponent(getStudentId())}`).catch(()=>null),
      api<HealthData>('/health').catch(()=>null),
    ]).then(([p,h])=>{ if(p) setProgress(normalizeProgressData(p)); if(h) setHealth(h) })
  },[])
  const entries=Object.entries(progress?.mastery||{})
  const overall=entries.length?Math.round(entries.reduce((sum,[,v])=>sum+Number(v||0),0)/entries.length):0
  const latestAttempt=progress?.attempts?.[0]
  const latestDiagnosis=progress?.diagnoses?.[0]
  const snapshotConcept=latestAttempt?.concept_id || latestDiagnosis?.weakest_concept_id || entries[0]?.[0] || ''
  const snapshotName=conceptLabel(snapshotConcept, 'Your next concept')
  const snapshotGap=latestDiagnosis?.diagnosis || latestDiagnosis?.recommendation || (snapshotConcept ? `Recent activity is building evidence for ${snapshotName}.` : 'Start a real learning session and this snapshot will update from your saved progress.')
  const source=progress?.persistence?.source || (health?.supabaseConfigured ? 'persistent backend' : 'backend')
  return <div className="bg-[#f7f5ef]">
    <header className="mx-auto flex h-20 max-w-6xl items-center justify-between px-5">
      <Logo/><div className="flex items-center gap-4"><Link href="/join" className="hidden text-sm font-medium text-[#61746e] sm:block">Join a class</Link><Link href="/teacher" className="hidden text-sm font-medium text-[#61746e] sm:block">Teacher view</Link><Link href="/student" className="hidden text-sm font-medium text-[#61746e] sm:block">Enter workspace</Link><Button href="/student">Start learning <ArrowRight className="size-4"/></Button></div>
    </header>
    <main>
      <section className="mx-auto grid max-w-6xl items-center gap-14 px-5 pb-20 pt-16 lg:grid-cols-[1.1fr_0.9fr] lg:pb-28 lg:pt-24">
        <div>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#cfe0d6] bg-[#edf5ef] px-3 py-1.5 text-xs font-semibold text-[#39756d]"><span className="size-1.5 rounded-full bg-[#76a98c]"/>A clearer way to learn</div>
          <h1 className="max-w-2xl font-serif text-6xl leading-[0.98] tracking-[-0.055em] text-[#103c3b] sm:text-7xl">Learn what you <em className="text-[#a16b2b]">actually</em> need to learn.</h1>
          <p className="mt-7 max-w-xl text-lg leading-8 text-[#6f7e79]">LearnLens identifies learning gaps from your answers, verifies them, teaches the underlying concept, and measures what changes.</p>
          <div className="mt-9 flex flex-wrap items-center gap-3"><Button href="/student">Start learning <ArrowRight className="size-4"/></Button><Button href="#loop" variant="outline">See how it works</Button></div>
        </div>
        <div className="relative">
          <div className="rounded-[2rem] border border-[#d9e4dc] bg-white p-5 shadow-[0_24px_70px_rgba(33,73,66,0.1)]">
            <div className="flex items-center justify-between border-b border-[#e8eee8] pb-4"><div><p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#9b6c3e]">Live learning snapshot</p><p className="mt-1 text-lg font-semibold text-[#183e3c]">{snapshotName}</p></div><div className="flex items-center gap-2"><span className={`rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] ${health?.aiConfigured?'bg-[#e5f1ea] text-[#39756d]':'bg-[#f7ead0] text-[#9b6c3e]'}`}>{health?.aiConfigured?'AI ready':'AI status'}</span><span className="grid size-10 place-items-center rounded-xl bg-[#e5f1ea] text-[#39756d]"><BrainCircuit className="size-5"/></span></div></div>
            <div className="py-5"><div className="flex items-end justify-between"><div><p className="text-sm text-[#758580]">Current mastery</p><p className="mt-1 text-5xl font-semibold tracking-[-0.05em] text-[#103c3b]">{overall}%</p></div><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${overall>=80?'bg-[#e5f1ea] text-[#39756d]':'bg-[#f7ead0] text-[#9b6c3e]'}`}>{entries.length?(overall>=80?'Stable':'Needs practice'):'No session yet'}</span></div><div className="mt-4"><ProgressBar value={overall}/></div><div className="mt-5 rounded-xl bg-[#f6f4ee] p-4"><p className="text-sm font-semibold text-[#183e3c]">{entries.length?'Latest evidence':'Start your learning journey'}</p><p className="mt-1 text-sm leading-6 text-[#758580]">{snapshotGap}</p>{latestAttempt&&<div className="mt-3 flex items-center gap-2 text-xs font-medium text-[#39756d]"><Check className="size-3.5"/>Latest saved attempt: {latestAttempt.correct?'correct':'needs another pass'}</div>}</div></div>
            <div className="grid grid-cols-3 gap-2 border-t border-[#e8eee8] pt-4 text-center"><div><p className="text-lg font-semibold text-[#183e3c]">{progress?.attempts?.length||0}</p><p className="text-[11px] text-[#82908b]">saved attempts</p></div><div><p className="text-lg font-semibold text-[#183e3c]">{entries.length}</p><p className="text-[11px] text-[#82908b]">concepts tracked</p></div><div><p className="text-lg font-semibold text-[#183e3c]">{source==='supabase'?'Live':'Backend'}</p><p className="text-[11px] text-[#82908b]">progress source</p></div></div>
          </div>
        </div>
      </section>
      <section id="loop" className="border-y border-[#e1e7e0] bg-[#eff4ef] px-5 py-16"><div className="mx-auto max-w-6xl"><div className="max-w-xl"><p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9b6c3e]">The learning loop</p><h2 className="mt-3 font-serif text-4xl tracking-[-0.04em] text-[#163e3b]">A score is a starting point, not the whole story.</h2></div><div className="mt-10 grid gap-3 sm:grid-cols-4 lg:grid-cols-8">{['Your work','Evidence','Learning gap','Verification','Lesson','Practice','Retest','Mastery'].map((item,i)=><div key={item} className="flex items-center gap-2"><div className="flex-1 rounded-xl border border-[#d2e0d5] bg-white p-3"><span className="text-[10px] font-semibold text-[#9b6c3e]">0{i+1}</span><p className="mt-1 text-sm font-semibold text-[#245851]">{item}</p></div>{i<7&&<ChevronRight className="hidden size-4 shrink-0 text-[#8aafa0] sm:block"/>}</div>)}</div></div></section>
      <section className="mx-auto max-w-6xl px-5 py-20"><div className="mb-8 rounded-2xl border border-[#dbe4dc] bg-white p-6 sm:flex sm:items-center sm:justify-between"><div><h3 className="text-lg font-semibold text-[#183e3c]">Learning with a class?</h3><p className="mt-1 text-sm leading-6 text-[#758580]">Join using a class code and nickname. No student email or password is needed.</p></div><Button href="/join" variant="outline" className="mt-4 sm:mt-0">Join class <ArrowRight className="size-4"/></Button></div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9b6c3e]">Start where you are</p><h2 className="mt-3 max-w-xl font-serif text-4xl tracking-[-0.04em] text-[#163e3b]">Three ways in. One clearer path forward.</h2><div className="mt-10 grid gap-4 md:grid-cols-3">{[{icon:BookOpen,title:'I want to learn a topic',text:'Enter any subject and topic, then let LearnLens build a focused diagnostic.',href:'/student/learn'},{icon:Upload,title:'I have work I got wrong',text:'Show us a photo, screenshot, worksheet, assignment, or PDF.',href:'/student/work'},{icon:Target,title:'Test my understanding',text:'Take a short five-question check for any subject and topic, then choose whether to learn it.',href:'/student/test'}].map(({icon:Icon,title,text,href})=><Link key={title} href={href} className="rounded-2xl border border-[#dbe4dc] bg-white p-6 transition hover:-translate-y-0.5 hover:border-[#b6ccbe]"><span className="grid size-10 place-items-center rounded-xl bg-[#e5f1ea] text-[#39756d]"><Icon className="size-5"/></span><h3 className="mt-5 text-lg font-semibold text-[#183e3c]">{title}</h3><p className="mt-2 text-sm leading-6 text-[#758580]">{text}</p><span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#39756d]">Open <ArrowRight className="size-4"/></span></Link>)}</div></section>
    </main>
  </div>
}

export default Home;
