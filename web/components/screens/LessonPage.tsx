'use client'

import React, { useEffect, useState } from 'react'
import { ArrowRight, BookOpen, Volume2, VolumeX, Languages, ExternalLink, ShieldCheck } from 'lucide-react'
import { api } from '@/lib/api'
import { getStudentId, getPreferredLanguage, loadState, saveState, type SessionState } from '@/lib/session'
import { Button, Shell, PageHeader, Thinking } from '@/components/ui-kit'

type LessonResult = { lesson: string; sourceIds?: string[]; sources?: {id:string;title:string;url?:string;snippet?:string;attribution?:string;license?:string}[]; language?: 'en'|'kn'|'hi'; glossary?:{en:string;local:string}[] }
const languageNames: Record<string,string> = { en:'English', kn:'Kannada', hi:'Hindi' }
const speechCodes: Record<string,string> = { en:'en-IN', kn:'kn-IN', hi:'hi-IN' }

export function LessonPage(){
  const [data,setData]=useState<LessonResult|null>(null)
  const [error,setError]=useState('')
  const [language,setLanguage]=useState<'en'|'kn'|'hi'>(()=>getPreferredLanguage())
  const [speaking,setSpeaking]=useState(false)
  const params = typeof window === 'undefined' ? new URLSearchParams() : new URLSearchParams(window.location.search)
  const session = loadState<SessionState>('learnlens_session',{subject:'',topic:'',conceptId:'',conceptName:''})
  const concept = params.get('concept') || session.conceptId || ''
  const name = params.get('name') || session.conceptName || session.topic || 'Learning topic'
  const subject = session.subject || ''
  const topic = session.topic || name
  const misconceptionTag = session.diagnosis?.misconceptionTag || session.diagnosis?.likelyMisconception || session.diagnosis?.questions?.find?.((q:any)=>q.misconceptionTag)?.misconceptionTag || 'other'
  useEffect(()=>{
    let active=true; setData(null); setError('')
    api<LessonResult>('/lesson/generate',{
      method:'POST', headers:{'content-type':'application/json'},
      body:JSON.stringify({studentId:getStudentId(),conceptId:concept,conceptName:name,subject,topic,language,misconceptionTag,evidence:(session.diagnosis?.evidence||[]).concat(session.verification ? [session.verification.feedback] : [])})
    }).then(d=>{if(!active)return;setData(d);saveState('learnlens_session',{...session,lesson:d,language})}).catch(e=>{if(active)setError(e instanceof Error?e.message:'Could not generate lesson.')})
    return ()=>{active=false}
  },[concept,name,subject,topic,language])
  useEffect(()=>()=>{if(typeof window!=='undefined'&&window.speechSynthesis)window.speechSynthesis.cancel()},[])
  function readAloud(){
    if(!data || typeof window==='undefined' || !('speechSynthesis' in window)){setError('Read-aloud is not supported by this browser.');return}
    if(speaking){window.speechSynthesis.cancel();setSpeaking(false);return}
    const utterance=new SpeechSynthesisUtterance(data.lesson); utterance.lang=speechCodes[language]||'en-IN'; utterance.onend=()=>setSpeaking(false); utterance.onerror=()=>setSpeaking(false); window.speechSynthesis.cancel(); window.speechSynthesis.speak(utterance); setSpeaking(true)
  }
  if(!data&&!error) return <Shell><div className="mx-auto max-w-3xl"><Thinking steps={['Reading your evidence','Retrieving related notes','Preparing a short lesson','Ready to learn']}/></div></Shell>
  if(error&&!data) return <Shell><div className="mx-auto max-w-3xl"><div className="rounded-2xl border border-[#f0cfc7] bg-[#fff3ef] p-6">{error}</div><Button href="/student" className="mt-5">Back to workspace</Button></div></Shell>
  return <Shell><div className="mx-auto max-w-4xl px-1"><PageHeader eyebrow="Personalized lesson" title={`Let's work on ${name}.`} description="A short explanation informed by your evidence and bundled teaching notes." action={<span className="rounded-full bg-[#e5f1ea] px-3 py-1.5 text-xs font-semibold text-[#39756d]">Provisional learning support</span>}/><div className="mb-4 flex flex-wrap items-center gap-3 rounded-2xl border border-border bg-card p-4"><label className="flex items-center gap-2 text-sm font-medium text-[#345b54]"><Languages className="size-4"/>Lesson language<select value={language} onChange={e=>{const v=e.target.value as 'en'|'kn'|'hi';setLanguage(v);saveState('learnlens_profile',{...loadState<any>('learnlens_profile',{}),language:v})}} className="rounded-lg border border-[#cbd9cf] bg-card px-3 py-2"><option value="en">English</option><option value="kn">ಕನ್ನಡ (Kannada)</option><option value="hi">हिन्दी (Hindi)</option></select></label><button onClick={readAloud} className="inline-flex items-center gap-2 rounded-xl bg-[#103c3b] px-4 py-2.5 text-sm font-semibold text-white">{speaking?<VolumeX className="size-4"/>:<Volume2 className="size-4"/>}{speaking?'Stop read-aloud':'Read aloud'}</button><span className="text-xs text-[#82908b]">Uses your browser's speech service.</span></div>{error&&<p className="mb-4 rounded-xl bg-[#fff3ef] p-3 text-sm text-[#8b463a]">{error}</p>}<div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]"><article className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-10"><div className="flex items-center gap-2 text-sm font-semibold text-brand-teal"><BookOpen className="size-4"/>Targeted lesson <span className="ml-auto text-xs font-normal text-[#82908b]">{languageNames[data?.language||language]}</span></div><div className="mt-8 max-w-[68ch] whitespace-pre-wrap font-serif text-[1.06rem] leading-[1.9] text-muted-foreground">{data?.lesson}</div>{(data?.glossary||[]).length>0&&<div className="mt-6 rounded-xl bg-[#f6f4ee] p-4"><h3 className="text-sm font-semibold text-[#183e3c]">Key vocabulary</h3><dl className="mt-3 grid gap-2 sm:grid-cols-2">{data?.glossary?.map((g,i)=><div key={i} className="text-sm"><dt className="font-medium text-[#345b54]">{g.en}</dt><dd className="text-muted-foreground">{g.local}</dd></div>)}</dl></div>}{(data?.sources||[]).length>0&&<div className="mt-7 border-t border-[#e8eee8] pt-5"><p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-[#82908b]"><ShieldCheck className="size-4"/>Retrieved note sources</p><div className="mt-3 flex flex-col gap-3">{data?.sources?.map(source=><div key={source.id} className="rounded-xl border border-border p-3"><div className="flex items-start justify-between gap-3"><div><p className="text-sm font-semibold text-[#345b54]">{source.title}</p><p className="mt-1 text-xs text-[#82908b]">{source.id} · {source.attribution || 'Bundled teaching note; provenance unspecified'}</p>{source.license && <p className="mt-1 text-[11px] text-[#82908b]">License: {source.license}</p>}</div>{source.url&&<a href={source.url} target="_blank" rel="noreferrer" className="text-[#39756d]" aria-label="Open source"><ExternalLink className="size-4"/></a>}</div>{source.snippet&&<p className="mt-2 text-sm leading-6 text-muted-foreground">{source.snippet}</p>}</div>)}</div><p className="mt-3 text-xs leading-5 text-[#82908b]">These are internal teaching notes, not a citation to an independently reviewed textbook. Ask a teacher to verify content for high-stakes use.</p></div>}<Button href={`/student/practice?concept=${encodeURIComponent(concept)}&name=${encodeURIComponent(name)}&subject=${encodeURIComponent(subject)}&topic=${encodeURIComponent(topic)}`} className="mt-8">Practice this skill <ArrowRight className="size-4"/></Button></article><aside className="rounded-2xl border border-border bg-[#103c3b] p-6 text-[#edf5ef]"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#9bc5b5]">What this is for</p><p className="mt-5 font-serif text-3xl leading-tight tracking-[-0.04em]">Fix the idea, not just the answer.</p><p className="mt-5 text-sm leading-7 text-[#b7d1c7]">Practice will use fresh variations of the same target so we can measure whether the learning transfers. Mastery remains provisional until a delayed retest is passed.</p><Button href="/student/privacy" variant="outline" className="mt-6 border-[#88b7a7] text-white">Privacy and delete data</Button></aside></div></div></Shell>
}

export default LessonPage;
