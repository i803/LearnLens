'use client'

import React, { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AlertTriangle, ArrowRight, Check, Clock3 } from 'lucide-react'
import { api } from '@/lib/api'
import { getPreferredLanguage, getStudentId, loadState, saveState } from '@/lib/session'
import {
  type ProgressData,
  normalizeProgressData,
  Button,
  Shell,
  PageHeader,
  Thinking,
} from '@/components/ui-kit'

type AttemptResult = {
  correct: boolean
  mastery: number
  explanation: string
  confirmed: boolean
  provisional: boolean
  nextDue?: string | null
}

type QuizItem = {
  questionId: string
  question: string
  options: string[]
  correctAnswer?: string
  explanation?: string
  difficulty?: number
}

export function QuestionFlow({ mode }: { mode: 'practice' | 'retest' }) {
  const router = useRouter()
  const query = typeof window !== 'undefined'
    ? new URLSearchParams(window.location.search)
    : new URLSearchParams()
  const session = loadState<any>('learnlens_session', {})
  const concept = query.get('concept') || session.conceptId || ''
  const name = query.get('name') || session.conceptName || session.topic || 'Learning topic'
  const subject = query.get('subject') || session.subject || ''
  const topic = query.get('topic') || session.topic || name
  const analysis = loadState<any>('learnlens_analysis', null)

  const [items, setItems] = useState<QuizItem[]>([])
  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [results, setResults] = useState<Array<AttemptResult & { questionId: string; question: string }>>([])
  const [currentAttempt, setCurrentAttempt] = useState<AttemptResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [mastery, setMastery] = useState(30)

  const evidenceContext = useMemo(() => {
    const questions = Array.isArray(analysis?.questions) ? analysis.questions : []
    return questions
      .filter((q: any) => !concept || q.conceptId === concept)
      .slice(0, 12)
      .map((q: any) => ({
        questionNumber: q.questionNumber,
        questionText: q.questionText,
        studentAnswer: q.studentAnswer,
        correctAnswer: q.correctAnswer,
        marksAwarded: q.marksAwarded,
        marksPossible: q.marksPossible,
        errorType: q.errorType,
        skill: q.skill,
        conceptName: q.conceptName,
      }))
  }, [analysis, concept])

  async function loadNext(ids: string[], currentMastery: number, cancelled = false) {
    if (cancelled) return
    setLoading(true)
    setError('')
    try {
      const data = await api<{ question: QuizItem }>('/quiz/generate', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          studentId: getStudentId(),
          conceptId: concept,
          conceptName: name,
          subject,
          topic,
          mode,
          mastery: currentMastery,
          previousQuestionIds: ids,
          misconception: session.verification?.likelyMisconception || session.diagnosis?.diagnosis || '',
          skill: session.verification?.likelySkill || session.diagnosis?.recommendation || session.diagnosis?.weakestConceptName || '',
          evidenceContext,
          language: getPreferredLanguage(),
        }),
      })
      if (cancelled) return
      if (!data?.question?.questionId || !Array.isArray(data.question.options)) {
        throw new Error('The question service returned an incomplete question. Please try again.')
      }
      setItems((old) => [...old, data.question])
      setAnswer('')
      setCurrentAttempt(null)
    } catch (e) {
      if (!cancelled) setError(e instanceof Error ? e.message : 'Could not create a question.')
      throw e
    } finally {
      if (!cancelled) setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false
    async function start() {
      try {
        const progress = await api<ProgressData>(`/student/progress?studentId=${encodeURIComponent(getStudentId())}`)
          .catch(() => normalizeProgressData({ studentId: getStudentId() }))
        const initial = Number(progress.mastery?.[concept] ?? (mode === 'practice' ? 30 : 50))
        if (!cancelled) setMastery(initial)
        const previousIds = mode === 'retest' ? loadState<string[]>('learnlens_practice_ids', []) : []
        await loadNext(previousIds, initial, cancelled)
      } catch {
        // loadNext already sets the user-facing error.
      }
    }
    void start()
    return () => { cancelled = true }
    // Query/session context is fixed for this route instance; a new concept opens a new route.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, concept])

  async function checkAnswer() {
    const question = items[index]
    if (!answer || !question || submitting || currentAttempt) return
    setSubmitting(true)
    setError('')
    try {
      const attempt = await api<AttemptResult>('/quiz/evaluate', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          studentId: getStudentId(),
          questionId: question.questionId,
          conceptId: concept,
          answer,
          mode,
        }),
      })
      if (typeof attempt?.mastery !== 'number' || typeof attempt.correct !== 'boolean') {
        throw new Error('The server did not confirm this attempt. Your answer has not been marked as saved.')
      }
      const safeAttempt: AttemptResult = {
        correct: attempt.correct,
        mastery: attempt.mastery,
        explanation: attempt.explanation || 'Your answer was checked by the server.',
        confirmed: Boolean(attempt.confirmed),
        provisional: Boolean(attempt.provisional),
        nextDue: attempt.nextDue || null,
      }
      setCurrentAttempt(safeAttempt)
      setMastery(safeAttempt.mastery)
      setResults((old) => [...old, { ...safeAttempt, questionId: question.questionId, question: question.question }])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save your attempt. Please retry.')
    } finally {
      setSubmitting(false)
    }
  }

  async function continueAfterAnswer() {
    if (!currentAttempt || submitting) return
    setSubmitting(true)
    setError('')
    try {
      const questionIds = items.map((item) => item.questionId)
      if (index >= 2) {
        const practiceRecord = {
          results,
          finalMastery: currentAttempt.mastery,
          confirmed: currentAttempt.confirmed,
          provisional: currentAttempt.provisional,
          nextDue: currentAttempt.nextDue || null,
          conceptId: concept,
          conceptName: name,
          subject,
          topic,
        }
        saveState(mode === 'practice' ? 'learnlens_practice_ids' : 'learnlens_retest_ids', questionIds)
        saveState('learnlens_session', {
          ...session,
          [mode]: practiceRecord,
          conceptId: concept,
          conceptName: name,
          subject,
          topic,
        })
        router.push('/student/progress')
        return
      }
      await loadNext(questionIds, currentAttempt.mastery)
      setIndex((old) => old + 1)
    } catch {
      // loadNext displays the reason and keeps the current checked answer on screen.
    } finally {
      setSubmitting(false)
    }
  }

  const current = items[index]
  const title = mode === 'practice' ? 'Practice the skill.' : 'Can you solve it on your own?'
  const dueDate = currentAttempt?.nextDue ? new Date(currentAttempt.nextDue) : null

  return (
    <Shell>
      <div className="mx-auto max-w-3xl px-1">
        <PageHeader
          eyebrow={mode === 'practice' ? 'Adaptive practice' : 'Spaced retest'}
          title={title}
          description={mode === 'practice'
            ? 'Fresh variations target the same underlying skill. Mastery updates come from the server, not a local score guess.'
            : 'The retest is checked against the saved attempt and its due time. A pass before the spacing window is still provisional.'}
          action={<span className="text-xs text-[#82908b]">Question {Math.min(index + 1, 3)} of 3</span>}
        />

        {error && <div role="alert" className="mb-4 rounded-xl border border-[#f0cfc7] bg-[#fff3ef] p-3 text-sm text-[#8b463a]">{error}</div>}

        {loading && !current ? (
          <Thinking steps={mode === 'practice'
            ? ['Reading your saved mastery state', 'Choosing the right difficulty', 'Creating a fresh question']
            : ['Reading the previous attempt', 'Checking the retest context', 'Creating a fresh transfer problem']} />
        ) : current ? (
          <div className="rounded-2xl border border-border bg-card p-6 sm:p-8">
            <div className="flex items-center justify-between gap-3">
              <span className="rounded-full bg-[#e5f1ea] px-3 py-1 text-xs font-semibold text-[#39756d]">{name}</span>
              <span className="text-xs text-[#82908b]">Difficulty {current.difficulty ?? 'adaptive'}</span>
            </div>
            <div className="mt-3 text-xs text-[#82908b]">Mastery before this question: {Math.round(results.length ? results[results.length - 1].mastery : mastery)}%</div>
            <div className="mt-6 rounded-xl bg-[#f6f4ee] p-5"><p className="text-base leading-7 text-[#183e3c]">{current.question}</p></div>

            <div className="mt-5 grid gap-3">
              {(current.options || []).map((option) => (
                <button
                  key={option}
                  type="button"
                  disabled={Boolean(currentAttempt) || submitting}
                  onClick={() => setAnswer(option)}
                  className={`flex items-center justify-between rounded-xl border p-4 text-left text-sm disabled:cursor-default ${answer === option ? 'border-[#72a68f] bg-[#eaf4ed] text-[#245851]' : 'border-border text-[#61746e] hover:border-[#a8c4b5]'}`}
                >
                  <span>{option}</span>{answer === option && <Check className="size-4" />}
                </button>
              ))}
            </div>

            {currentAttempt && (
              <div className={`mt-5 rounded-xl p-4 text-sm ${currentAttempt.correct ? 'bg-[#edf5ef] text-[#356c5f]' : 'bg-[#fff7eb] text-[#80603d]'}`} role="status">
                <p className="font-semibold">{currentAttempt.correct ? 'Correct' : 'Not quite'} · Server-calculated mastery {Math.round(currentAttempt.mastery)}%</p>
                <p className="mt-2 leading-6">{currentAttempt.explanation}</p>
                {currentAttempt.confirmed ? (
                  <p className="mt-2 flex items-center gap-2 font-semibold"><Check className="size-4" />Delayed retest passed — mastery confirmed.</p>
                ) : (
                  <p className="mt-2 flex items-start gap-2"><Clock3 className="mt-0.5 size-4 shrink-0" />Mastery is provisional until a correct retest after the 24-hour spacing window.{dueDate && ` Earliest next due: ${dueDate.toLocaleString()}.`}</p>
                )}
              </div>
            )}

            <div className="mt-7 flex items-center justify-between gap-3 border-t border-[#e8eee8] pt-5">
              <div className="text-xs text-[#82908b]">{results.length} of 3 checked</div>
              {!currentAttempt ? (
                <Button onClick={checkAnswer} disabled={!answer || submitting}>
                  {submitting ? 'Checking…' : 'Check answer'} <ArrowRight className="size-4" />
                </Button>
              ) : (
                <Button onClick={continueAfterAnswer} disabled={submitting}>
                  {submitting ? 'Saving…' : index >= 2 ? 'Finish and view progress' : 'Continue'} <ArrowRight className="size-4" />
                </Button>
              )}
            </div>
            {mode === 'retest' && !currentAttempt?.confirmed && <p className="mt-4 flex items-start gap-2 text-xs leading-5 text-[#82908b]"><AlertTriangle className="mt-0.5 size-4 shrink-0" />A correct answer alone does not override the spaced-retrieval rule. This prototype never treats a premature retest as confirmed mastery.</p>}
          </div>
        ) : (
          <div className="rounded-xl border border-border bg-card p-6 text-sm text-[#61746e]">A question could not be loaded. Fix the issue above and retry.</div>
        )}
      </div>
    </Shell>
  )
}

export default QuestionFlow
