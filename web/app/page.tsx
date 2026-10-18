'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowRight, BrainCircuit, Check, ChevronRight, FileText, Languages, ShieldCheck, Sparkles, Target, Users } from 'lucide-react'
import { Button, Logo } from '@/components/ui-kit'

const steps = [
  { number: '01', title: 'Show your work', text: 'Upload a worksheet or answer a short diagnostic.' },
  { number: '02', title: 'Find the why', text: 'See the misconception behind the mistake, not just a red mark.' },
  { number: '03', title: 'Repair the gap', text: 'Learn in your language, practise, and prove it with a later retest.' },
]

const features = [
  { icon: BrainCircuit, title: 'Misconception diagnosis', text: 'Turn wrong answers into a clear hypothesis about what got mixed up.' },
  { icon: Languages, title: 'Lessons that meet you there', text: 'Short, grounded explanations in English, Kannada, or Hindi where available.' },
  { icon: Target, title: 'Mastery that earns trust', text: 'Keep provisional progress separate from skills confirmed by a delayed retest.' },
  { icon: Users, title: 'A clearer class picture', text: 'Help teachers see patterns across a class and plan the next 10-minute reteach.' },
]

type BackendHealth = {
  aiConfigured?: boolean
}

function BackendStatusBanner() {
  const [status, setStatus] = useState<'checking' | 'healthy' | 'unavailable'>('checking')

  useEffect(() => {
    let active = true

    fetch('/api/health', { cache: 'no-store' })
      .then(async (response) => {
        const data = (await response.json().catch(() => null)) as BackendHealth | null
        if (active) setStatus(response.ok && data?.aiConfigured !== false ? 'healthy' : 'unavailable')
      })
      .catch(() => {
        if (active) setStatus('unavailable')
      })

    return () => {
      active = false
    }
  }, [])

  if (status !== 'unavailable') return null

  return (
    <div className="border-b border-[#e7c98f] bg-[#fff8e8] px-5 py-3 text-sm text-[#76551c]" role="status" aria-live="polite">
      <div className="mx-auto flex max-w-7xl items-start gap-3 lg:px-3">
        <span className="mt-1 size-2 shrink-0 rounded-full bg-[#c98a28]" aria-hidden="true" />
        <p><span className="font-semibold">Learning services are unavailable.</span> The backend could not be reached, so some learning features may not work right now.</p>
      </div>
    </div>
  )
}

export default function Home() {
  return <div className="min-h-screen bg-[#f8f9fc] text-[#17233f]">
    <BackendStatusBanner />
    <header className="border-b border-[#e5e9f2] bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 lg:px-8"><Logo /><nav className="hidden items-center gap-7 text-sm font-medium text-[#68748d] md:flex"><a href="#how-it-works" className="hover:text-[#17233f]">How it works</a><a href="#for-teachers" className="hover:text-[#17233f]">For teachers</a><a href="#responsible" className="hover:text-[#17233f]">Responsible AI</a></nav><div className="flex items-center gap-3"><Link href="/teacher" className="hidden text-sm font-semibold text-[#59657c] sm:block">Teacher view</Link><Button href="/join">Join a class <ArrowRight className="size-4" /></Button></div></div>
    </header>
    <main>
      <section className="mx-auto grid max-w-7xl items-center gap-14 px-5 pb-20 pt-16 lg:grid-cols-[1.02fr_0.98fr] lg:px-8 lg:pb-28 lg:pt-24">
        <div><div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#d9def9] bg-[#f0f1ff] px-3 py-1.5 text-xs font-bold uppercase tracking-[0.14em] text-[#5d61c8]"><span className="size-1.5 rounded-full bg-[#6d70e1]" /> Personalized learning, made visible</div><h1 className="max-w-2xl text-5xl font-semibold leading-[1.02] tracking-[-0.06em] text-[#17233f] sm:text-7xl">Understand the mistake. <span className="text-[#676bd6]">Fix the idea.</span></h1><p className="mt-7 max-w-xl text-lg leading-8 text-[#69758d]">LearnLens helps students discover why an answer went wrong, repair the underlying misconception, and prove what they know next.</p><div className="mt-9 flex flex-wrap gap-3"><Button href="/student">Start learning <ArrowRight className="size-4" /></Button><Button href="#how-it-works" variant="outline">See the learning loop</Button></div><div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-[#69758d]"><span className="inline-flex items-center gap-2"><Check className="size-4 text-[#1aa184]" /> No email required to join</span><span className="inline-flex items-center gap-2"><ShieldCheck className="size-4 text-[#1aa184]" /> AI never grades you</span></div></div>
        <div className="relative"><div className="absolute -inset-5 rounded-[2.5rem] bg-[#eceeff] blur-2xl" /><div className="relative overflow-hidden rounded-[1.75rem] border border-[#e1e5f4] bg-white shadow-[0_24px_70px_rgba(44,53,101,0.12)]"><div className="flex items-center justify-between border-b border-[#edf0f6] px-5 py-4"><div className="flex items-center gap-2"><span className="size-2 rounded-full bg-[#50c4a3]" /><span className="text-xs font-bold uppercase tracking-[0.13em] text-[#7c88a0]">Learning snapshot</span></div><span className="rounded-full bg-[#edf9f5] px-2.5 py-1 text-[11px] font-bold text-[#16856d]">Saved evidence</span></div><div className="p-6 sm:p-8"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-medium text-[#7c88a0]">Possible misconception</p><h2 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-[#17233f]">Open vs. closed intervals</h2></div><span className="grid size-11 place-items-center rounded-2xl bg-[#f0f1ff] text-[#676bd6]"><BrainCircuit className="size-5" /></span></div><div className="mt-7 rounded-2xl border border-[#e8eaf7] bg-[#fafaff] p-5"><div className="flex items-center gap-3"><span className="grid size-8 place-items-center rounded-lg bg-[#fff4dc] text-[#bd7c1d]"><FileText className="size-4" /></span><div><p className="text-sm font-semibold text-[#27334f]">Evidence from questions 5 and 6</p><p className="mt-0.5 text-xs text-[#7c88a0]">Observed work, ready to review</p></div></div><p className="mt-4 text-sm leading-6 text-[#64718a]">The endpoints are being treated the same way in both answers. LearnLens keeps this as a hypothesis until you verify it.</p></div><div className="mt-6 flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.13em] text-[#7c88a0]">Next best step</p><p className="mt-1 font-semibold text-[#27334f]">Take a 3-question check</p></div><Link href="/student/work" aria-label="Take a 3-question check" className="grid size-10 place-items-center rounded-xl bg-[#17233f] text-white"><ArrowRight className="size-4" /></Link></div></div></div></div>
      </section>
      <section id="how-it-works" className="border-y border-[#e5e9f2] bg-white"><div className="mx-auto max-w-7xl px-5 py-20 lg:px-8"><div className="max-w-2xl"><p className="text-xs font-bold uppercase tracking-[0.18em] text-[#676bd6]">The learning loop</p><h2 className="mt-3 text-4xl font-semibold tracking-[-0.05em] text-[#17233f] sm:text-5xl">A score is a starting point, not the whole story.</h2></div><div className="mt-12 grid gap-4 md:grid-cols-3">{steps.map((step, index) => <div key={step.number} className="relative rounded-2xl border border-[#e5e9f2] bg-[#fafbfe] p-6"><span className="text-sm font-bold text-[#9ba5bc]">{step.number}</span><h3 className="mt-12 text-xl font-semibold text-[#27334f]">{step.title}</h3><p className="mt-2 text-sm leading-6 text-[#6d7890]">{step.text}</p>{index < 2 && <ChevronRight className="absolute right-5 top-1/2 hidden size-5 translate-x-1/2 text-[#b5bdd0] md:block" />}</div>)}</div></div></section>
      <section id="for-teachers" className="mx-auto max-w-7xl px-5 py-20 lg:px-8"><div className="grid gap-10 lg:grid-cols-[0.82fr_1.18fr] lg:items-end"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-[#676bd6]">Built for the next lesson</p><h2 className="mt-3 text-4xl font-semibold tracking-[-0.05em] text-[#17233f]">Less marking after the fact. More useful teaching tomorrow.</h2><p className="mt-5 text-base leading-7 text-[#69758d]">Students get a focused path forward. Teachers get an aggregated view of misconceptions before they become another exam result.</p><Link href="/teacher" className="mt-7 inline-flex items-center gap-2 text-sm font-bold text-[#5d61c8]">Open teacher workspace <ArrowRight className="size-4" /></Link></div><div className="grid gap-3 sm:grid-cols-2">{features.map(({ icon: Icon, title, text }) => <div key={title} className="rounded-2xl border border-[#e5e9f2] bg-white p-5 shadow-[0_8px_30px_rgba(44,53,101,0.04)]"><span className="grid size-10 place-items-center rounded-xl bg-[#f0f1ff] text-[#676bd6]"><Icon className="size-5" /></span><h3 className="mt-5 font-semibold text-[#27334f]">{title}</h3><p className="mt-2 text-sm leading-6 text-[#6d7890]">{text}</p></div>)}</div></div></section>
      <section id="responsible" className="border-t border-[#e5e9f2] bg-[#17233f] text-white"><div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-12 sm:flex-row sm:items-center sm:justify-between lg:px-8"><div><div className="flex items-center gap-2 text-sm font-bold"><ShieldCheck className="size-4 text-[#69d2b6]" /> Designed for responsible learning support</div><p className="mt-2 max-w-2xl text-sm leading-6 text-[#b9c2d6]">LearnLens shows evidence separately from AI interpretation, keeps confidence honest, and leaves the final teaching decision with students and educators.</p></div><Button href="/student/privacy" variant="quiet">Privacy controls <ArrowRight className="size-4" /></Button></div></section>
    </main>
    <footer className="bg-white"><div className="mx-auto flex max-w-7xl flex-col gap-3 px-5 py-8 text-sm text-[#7c88a0] sm:flex-row sm:items-center sm:justify-between lg:px-8"><Logo /><p>LearnLens AI · Learn what you actually need to learn.</p></div></footer>
  </div>
}
