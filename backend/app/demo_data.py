from __future__ import annotations
from typing import Any

CONCEPTS = {
    "sets-builder": {"name": "Set-builder notation", "skill": "Translate between roster and set-builder forms"},
    "sets-types": {"name": "Types of sets", "skill": "Identify empty, finite and infinite sets"},
    "sets-operations": {"name": "Set operations and intervals", "skill": "Apply union, difference, intervals and cardinality"},
}

SAMPLE_QUESTIONS = [
    {"questionId":"q1","questionNumber":"1","questionText":"Write the set B = {3, 9, 27, 81} in set-builder form.","studentAnswer":"B = {3, 9, 27, 81}","marksAwarded":2,"marksPossible":2,"teacherFeedback":"Correct","conceptId":"sets-builder","conceptName":"Set-builder notation","skill":"Translate between roster and set-builder forms","errorType":"none","extractionConfidence":0.98,"diagnosisConfidence":0.95,"needsHumanReview":False},
    {"questionId":"q2","questionNumber":"2A","questionText":"Which of the following is an empty set? A = {x : x ∈ N and 3 < x < 4}","studentAnswer":"A is not empty","marksAwarded":0,"marksPossible":1,"teacherFeedback":"No natural number lies strictly between 3 and 4","conceptId":"sets-types","conceptName":"Types of sets","skill":"Identify empty sets","errorType":"conceptual","extractionConfidence":0.97,"diagnosisConfidence":0.9,"needsHumanReview":False},
    {"questionId":"q3","questionNumber":"3","questionText":"The set of all the points on the circumference of a circle is finite or infinite? Justify.","studentAnswer":"Finite","marksAwarded":0,"marksPossible":2,"teacherFeedback":"The circumference contains infinitely many points","conceptId":"sets-types","conceptName":"Types of sets","skill":"Distinguish finite and infinite sets","errorType":"conceptual","extractionConfidence":0.96,"diagnosisConfidence":0.9,"needsHumanReview":False},
    {"questionId":"q4","questionNumber":"4","questionText":"Are A = {-2, 2}, B = {x : x ∈ Z, x² − 4 = 0} equal? Why?","studentAnswer":"No","marksAwarded":0,"marksPossible":2,"teacherFeedback":"Both sets contain -2 and 2","conceptId":"sets-builder","conceptName":"Set-builder notation","skill":"Evaluate a set-builder condition","errorType":"conceptual","extractionConfidence":0.95,"diagnosisConfidence":0.92,"needsHumanReview":False},
    {"questionId":"q5","questionNumber":"5","questionText":"Write (-5,9] in set-builder form.","studentAnswer":"{x : -5 < x < 9}","marksAwarded":1,"marksPossible":2,"teacherFeedback":"Right endpoint should be included","conceptId":"sets-operations","conceptName":"Set operations and intervals","skill":"Translate intervals to set-builder form","errorType":"conceptual","extractionConfidence":0.95,"diagnosisConfidence":0.86,"needsHumanReview":False},
    {"questionId":"q6","questionNumber":"6","questionText":"If A=[-3,5], B=(0,6], find A−B and A∪B.","studentAnswer":"A−B=[-3,0] and A∪B=[-3,6]","marksAwarded":2,"marksPossible":3,"teacherFeedback":"Check endpoint inclusion at 0","conceptId":"sets-operations","conceptName":"Set operations and intervals","skill":"Apply interval operations","errorType":"careless","extractionConfidence":0.94,"diagnosisConfidence":0.72,"needsHumanReview":False},
    {"questionId":"q7","questionNumber":"7","questionText":"Are A={1,2,3,4}, B={x : x ∈ N and 5 ≤ x ≤ 7} disjoint? Why?","studentAnswer":"No, they share values","marksAwarded":0,"marksPossible":1,"teacherFeedback":"They have no common elements","conceptId":"sets-types","conceptName":"Types of sets","skill":"Check disjointness","errorType":"misreading","extractionConfidence":0.93,"diagnosisConfidence":0.68,"needsHumanReview":False},
    {"questionId":"q8","questionNumber":"8","questionText":"If n(X)=19, n(Y)=37 and n(X∩Y)=12, find n(X∪Y).","studentAnswer":"68","marksAwarded":1,"marksPossible":2,"teacherFeedback":"Use n(X∪Y)=n(X)+n(Y)−n(X∩Y)","conceptId":"sets-operations","conceptName":"Set operations and intervals","skill":"Use cardinality formula","errorType":"arithmetic","extractionConfidence":0.93,"diagnosisConfidence":0.62,"needsHumanReview":False},
]

DEMO_ANALYSIS = {
    "totalMarks":7,"marksPossible":15,"scorePercent":46.7,
    "questions": SAMPLE_QUESTIONS,
    "possibleLearningGaps":["Types of sets", "Set-builder notation", "Set operations and intervals"],
    "overallConfidence":0.92,
    "source":"demo"
}

DIAGNOSTICS = {
    "sets-types": [
        {"questionId":"verify-types-1","conceptId":"sets-types","conceptName":"Types of sets","question":"Is the set {x ∈ N : 10 < x < 11} empty?","options":["Yes, empty","No, one element","No, infinitely many","Cannot determine"],"correctAnswer":"Yes, empty","difficulty":1,"skill":"Identify empty sets"},
        {"questionId":"verify-types-2","conceptId":"sets-types","conceptName":"Types of sets","question":"Is the set of integers between -2 and 3 inclusive finite?","options":["Yes","No","Only if zero is included","Cannot determine"],"correctAnswer":"Yes","difficulty":2,"skill":"Identify finite sets"},
        {"questionId":"verify-types-3","conceptId":"sets-types","conceptName":"Types of sets","question":"The set of real numbers in [0,1] is:","options":["Empty","Finite","Infinite","A singleton"],"correctAnswer":"Infinite","difficulty":3,"skill":"Identify infinite sets"},
    ],
    "sets-builder": [
        {"questionId":"verify-builder-1","conceptId":"sets-builder","conceptName":"Set-builder notation","question":"Which set-builder form represents {2,4,6,8}?","options":["{x ∈ N : x is even and x≤8}","{x ∈ N : x<8}","{x ∈ Z : x is odd}","{x : x≥2}"],"correctAnswer":"{x ∈ N : x is even and x≤8}","difficulty":1,"skill":"Translate roster to rule"},
        {"questionId":"verify-builder-2","conceptId":"sets-builder","conceptName":"Set-builder notation","question":"For {x ∈ Z : x²=9}, the elements are:","options":["{3}","{-3,3}","{0,9}","{-9,9}"],"correctAnswer":"{-3,3}","difficulty":2,"skill":"Evaluate set-builder conditions"},
        {"questionId":"verify-builder-3","conceptId":"sets-builder","conceptName":"Set-builder notation","question":"Which notation describes numbers greater than 4 but at most 9?","options":["{x : 4<x≤9}","{x : 4≤x<9}","{x : x<4 or x>9}","{x : 4<x<9}"],"correctAnswer":"{x : 4<x≤9}","difficulty":3,"skill":"Read endpoint inclusion"},
    ],
    "sets-operations": [
        {"questionId":"verify-op-1","conceptId":"sets-operations","conceptName":"Set operations and intervals","question":"For A=[-3,5] and B=(0,6], which numbers are in A−B?","options":["[-3,0]","[-3,0)","(0,5]","[-3,6]"],"correctAnswer":"[-3,0]","difficulty":1,"skill":"Set difference"},
        {"questionId":"verify-op-2","conceptId":"sets-operations","conceptName":"Set operations and intervals","question":"What is [1,4] ∪ (3,7]?","options":["[1,3]","[1,7]","(3,4]","[1,4)"],"correctAnswer":"[1,7]","difficulty":2,"skill":"Union of intervals"},
        {"questionId":"verify-op-3","conceptId":"sets-operations","conceptName":"Set operations and intervals","question":"If n(X)=12, n(Y)=15, n(X∩Y)=5, then n(X∪Y)=?","options":["22","27","8","20"],"correctAnswer":"22","difficulty":3,"skill":"Cardinality formula"},
    ],
}

QUIZ_BANK = {
    "sets-types": [
        {"questionId":"quiz-types-1","conceptId":"sets-types","conceptName":"Types of sets","question":"Which set is infinite?","options":["{1,2,3}","{x∈N : x<10}","The set of integers","{x∈N : x=7}"],"correctAnswer":"The set of integers","difficulty":2,"explanation":"Integers continue without an endpoint."},
        {"questionId":"quiz-types-2","conceptId":"sets-types","conceptName":"Types of sets","question":"How many elements are in {x∈N : 2<x<6}?","options":["2","3","4","Infinite"],"correctAnswer":"3","difficulty":1,"explanation":"The natural numbers are 3, 4 and 5."},
    ],
    "sets-builder": [
        {"questionId":"quiz-builder-1","conceptId":"sets-builder","conceptName":"Set-builder notation","question":"Which matches (-2,3]?","options":["{x : -2<x≤3}","{x : -2≤x<3}","{x : x<-2 or x>3}","{x : -2≤x≤3}"],"correctAnswer":"{x : -2<x≤3}","difficulty":2,"explanation":"Open at -2 and closed at 3."},
        {"questionId":"quiz-builder-2","conceptId":"sets-builder","conceptName":"Set-builder notation","question":"Which condition gives {1,2,3,4}?","options":["x∈N and x≤4","x∈N and x<4","x∈Z and x≤4","x>0"],"correctAnswer":"x∈N and x≤4","difficulty":1,"explanation":"Natural numbers up to 4 are 1,2,3,4."},
    ],
    "sets-operations": [
        {"questionId":"quiz-op-1","conceptId":"sets-operations","conceptName":"Set operations and intervals","question":"If n(A)=9, n(B)=11 and n(A∩B)=4, find n(A∪B).","options":["24","16","20","14"],"correctAnswer":"16","difficulty":2,"explanation":"Use n(A∪B)=n(A)+n(B)-n(A∩B)."},
        {"questionId":"quiz-op-2","conceptId":"sets-operations","conceptName":"Set operations and intervals","question":"Which interval contains 5 but not 2?","options":["[2,5]","(2,6]","[-1,5)","[0,2]"],"correctAnswer":"(2,6]","difficulty":1,"explanation":"It includes numbers greater than 2 through 6."},
    ],
}

LESSONS = {
    "sets-types": "A set can be empty, finite or infinite. Empty means it has no elements. Finite means the elements can be counted and the list ends. Infinite means the process of finding new elements never ends. For example, {x∈N : 3<x<4} is empty because there is no natural number strictly between 3 and 4. A circle's circumference contains infinitely many points, even though the circle itself is a bounded shape. Remember: ask whether the elements themselves run out, not whether the picture or interval looks physically limited.",
    "sets-builder": "Set-builder notation describes a set by giving a rule that every member satisfies. Read {x : condition} as 'all x such that the condition is true.' For x²=9 over the integers, both -3 and 3 satisfy the rule, so the set is {-3,3}. For an interval like (-5,9], the left endpoint is excluded and the right endpoint is included, so the rule is -5<x≤9. Remember: parentheses mean excluded; square brackets mean included.",
    "sets-operations": "Set operations work like careful membership rules. A−B keeps elements in A that are not in B. A∪B includes everything in either set. For intervals, endpoint brackets matter. The cardinality rule n(A∪B)=n(A)+n(B)−n(A∩B) avoids double-counting the overlap. Remember: when combining finite sets, subtract the intersection once.",
}

def demo_analysis() -> dict[str, Any]:
    return DEMO_ANALYSIS
