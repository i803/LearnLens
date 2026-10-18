from __future__ import annotations
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field

ErrorType = Literal["none", "conceptual", "procedural", "arithmetic", "sign_error", "misreading", "incomplete_reasoning", "careless", "unknown"]

class ExtractedQuestion(BaseModel):
    questionId: str
    questionNumber: str
    questionText: str
    studentAnswer: str
    correctAnswer: str = ""
    marksAwarded: float = 0
    marksPossible: float = 0
    marksSource: Literal["teacher", "estimated", "unknown"] = "unknown"
    gradingConfidence: float = Field(0, ge=0, le=1)
    teacherFeedback: str = ""
    conceptId: str
    conceptName: str
    skill: str = ""
    errorType: ErrorType = "unknown"
    extractionConfidence: float = Field(0, ge=0, le=1)
    diagnosisConfidence: float = Field(0, ge=0, le=1)
    needsHumanReview: bool = False
    misconceptionTag: str = "other"

class WorkAnalysis(BaseModel):
    totalMarks: float = 0
    marksPossible: float = 0
    scorePercent: float = Field(0, ge=0, le=100)
    questions: list[ExtractedQuestion]
    possibleLearningGaps: list[str]
    overallConfidence: float = Field(0, ge=0, le=1)
    source: str = "ai"
    subject: str = ""
    topic: str = ""
    provider: str = "unknown"
    fromCache: bool = False

class DiagnosisRequest(BaseModel):
    studentId: str
    extractedQuestions: list[ExtractedQuestion]
    topic: str = ""
    subject: str = ""

class DiagnosisResponse(BaseModel):
    weakestConceptId: str
    weakestConceptName: str
    confidence: float = Field(0, ge=0, le=1)
    evidence: list[str]
    diagnosis: str
    recommendation: str
    misconceptionTag: str = "other"

class DiagnosticGenerateRequest(BaseModel):
    studentId: str
    conceptId: str
    conceptName: str
    count: int = Field(ge=3, le=5)
    mode: Literal["work", "topic"] = "work"
    subject: str = ""
    topic: str = ""
    sourceQuestions: list[dict] = Field(default_factory=list)
    sourceTopics: list[str] = Field(default_factory=list)

class DiagnosticQuestion(BaseModel):
    questionId: str
    conceptId: str
    conceptName: str
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correctAnswer: str
    difficulty: int = Field(ge=1, le=4)
    skill: str = ""

class DiagnosticGenerateResponse(BaseModel):
    questions: list[DiagnosticQuestion]

class DiagnosticEvaluateRequest(BaseModel):
    studentId: str
    conceptId: str
    answers: dict[str, str]

class DiagnosticEvaluateResponse(BaseModel):
    correct: int
    total: int
    scorePercent: float
    confirmedWeakness: bool
    confidence: float
    feedback: str
    likelyMisconception: str = ""
    likelySkill: str = ""

class LessonGenerateRequest(BaseModel):
    studentId: str
    conceptId: str
    conceptName: str
    subject: str = ""
    topic: str = ""
    evidence: list[str] = []
    language: Literal["en", "kn", "hi"] = "en"
    misconceptionTag: str = "other"

class LessonSource(BaseModel):
    id: str
    title: str
    url: str = ""
    snippet: str = ""
    attribution: str = "Bundled teaching note; provenance unspecified"
    license: str = "Review licensing before external reuse"

class GlossaryEntry(BaseModel):
    en: str
    local: str

class LessonResponse(BaseModel):
    lesson: str
    sourceIds: list[str] = []
    sources: list[LessonSource] = []
    language: Literal["en", "kn", "hi"] = "en"
    glossary: list[GlossaryEntry] = []

class QuizGenerateRequest(BaseModel):
    studentId: str
    conceptId: str
    conceptName: str
    subject: str = ""
    topic: str = ""
    mode: Literal["practice", "retest"] = "practice"
    mastery: float = Field(0, ge=0, le=100)
    previousQuestionIds: list[str] = []
    misconception: str = ""
    skill: str = ""
    evidenceContext: list[dict] = Field(default_factory=list)
    language: Literal["en", "kn", "hi"] = "en"

class QuizQuestion(BaseModel):
    questionId: str
    conceptId: str
    conceptName: str
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correctAnswer: str
    difficulty: int = Field(ge=1, le=4)
    explanation: str

class QuizGenerateResponse(BaseModel):
    question: QuizQuestion

class QuizEvaluateRequest(BaseModel):
    studentId: str
    questionId: str
    conceptId: str
    answer: str
    correctAnswer: str = ""
    mode: Literal["practice", "retest"] = "practice"
    asOf: datetime | None = None

class QuizEvaluateResponse(BaseModel):
    correct: bool
    mastery: float
    explanation: str
    confirmed: bool = False
    provisional: bool = True
    nextDue: str | None = None

class ProgressResponse(BaseModel):
    studentId: str
    mastery: dict[str, float]
    attempts: list[dict]
    diagnoses: list[dict]
    timeline: list[dict] = Field(default_factory=list)
    persistence: dict = Field(default_factory=dict)

class TeacherAnalyticsResponse(BaseModel):
    concepts: list[dict]
    studentsTracked: int
    persistence: dict = Field(default_factory=dict)

class FeedbackRequest(BaseModel):
    studentId: str
    sessionId: str | None = None
    rating: int = Field(ge=1, le=5)
    helpfulAspects: list[str] = Field(default_factory=list)
    confusingAspects: list[str] = Field(default_factory=list)
    wouldUseAgain: Literal["yes", "maybe", "no"] | None = None
    comment: str | None = Field(default=None, max_length=1000)

class FeedbackSummaryResponse(BaseModel):
    responses: int
    averageRating: float
    recentComments: list[str] = Field(default_factory=list)


class JoinRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    classCode: str = Field(min_length=3, max_length=24)
    language: Literal["en", "kn", "hi"] = "en"
    consent: bool = True

class CreateClassRequest(BaseModel):
    className: str = Field(min_length=2, max_length=80)
    teacherName: str = Field(min_length=1, max_length=50)

class DeleteDataRequest(BaseModel):
    studentId: str = Field(min_length=1, max_length=100)
