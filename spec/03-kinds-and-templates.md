# 3. Kinds and writing templates

## 3.1 Kinds

Every revision has exactly one **kind**. A kind classifies the content; it is
independent of confirmation and of execution authority (an `instruction` document does
not grant anyone new permissions, a `decision` document is not human-confirmed because
of its kind).

The kind values are normative and closed in v0.1:

| Kind | Question it answers |
|---|---|
| `request` | Who asked for what, and why? |
| `idea` | What possibility is being considered? |
| `spec` | What must be satisfied? |
| `architecture` | How is it structured and connected? |
| `resource` | Who or what plays which role? |
| `decision` | Why was this direction chosen? |
| `plan` | In what order will it proceed? |
| `action` | What must be done? (also the kind of Context-form work logs) |
| `issue` | What is unconfirmed or unresolved? |
| `instruction` | Which rule or procedure applies? (also the kind of Policies) |
| `report` | What was actually done and observed? |
| `glossary` | What does this term mean here? |
| `note` | What background or knowledge is kept? Use only when nothing else fits. |

## 3.2 Writing templates

Each kind has a **writing template**: a guiding question, four section headings and a
caution. A new document of that kind SHOULD use the template's headings as `#`
headings. Templates are prompts for the writer, never pre-filled facts.

Headings are given in English with the reference implementation's Korean labels. An
implementation MAY localize headings; the kind and the order of the four parts are
what the template fixes.

| Kind | Sections (English / Korean) | Caution |
|---|---|---|
| request | Original request / 요청 원문 · Target and scope / 대상과 범위 · Source / 출처 · Open questions / 미결 사항 | Keep the requester's words and corrections; separate the agent's interpretation from the original. |
| idea | Proposal / 제안 · Expected effect / 기대 효과 · Alternatives and constraints / 대안과 제약 · Points to review / 검토할 점 | Do not write a proposal under review as a decision or an instruction. |
| spec | Purpose and scope / 목적과 범위 · Requirements / 요구사항 · Acceptance criteria / 수용 기준 · Out of scope / 제외 범위 | Write observable, verifiable behaviour and conditions. |
| architecture | Structure and responsibilities / 구조와 책임 · Data flow / 데이터 흐름 · Integration boundaries / 연동 경계 · Failure and recovery / 실패와 복구 | Separate component responsibilities from trust and permission boundaries. |
| resource | Resources and roles / 자원과 역할 · Capabilities and use / 능력과 용도 · Constraints and availability / 제약과 가용성 · Sources and related material / 출처와 관련 자료 | Describing a participant, device, service or dataset is not access to it. |
| decision | What was chosen / 선택한 내용 · Reasons and evidence / 이유와 근거 · Alternatives considered / 검토한 대안 · Impact and replacement / 영향과 대체 관계 | State who confirmed it and when only with evidence; the kind alone is not human confirmation. |
| plan | Goal / 목표 · Steps and dependencies / 단계와 의존성 · Resources needed / 필요한 자원 · Verification plan / 검증 계획 | Do not present planned dates or owners as agreed when they are not. |
| action | Work to do / 수행할 작업 · Done when / 완료 조건 · Dependencies and constraints / 의존성과 제약 · Owner, due date and evidence / 담당·기한·관련 근거 | Write only known owners and dates; leave unknowns as unknown. |
| issue | Problem or question / 문제 또는 질문 · Observations and evidence / 관측과 근거 · Impact and risk / 영향과 위험 · Resolution conditions / 해결·확인 조건 | Distinguish questions, assumptions, bugs and blockers; separate observation from guess. |
| instruction | Scope / 적용 범위 · Rule or procedure / 규칙 또는 절차 · Exceptions and stop conditions / 예외와 중단 조건 · Source / 출처 | Separate policy from procedure; the document grants no new execution authority. |
| report | What was done / 수행 내용 · Results and evidence / 결과와 증거 · Verification scope and limits / 검증 범위와 한계 · Remaining work / 남은 작업 | Separate when it was done from when it was reported; keep failures and unverified scope. |
| glossary | Term and aliases / 용어와 별칭 · Definition / 정의 · Scope and examples / 적용 범위와 예시 · Source and history / 출처와 변경 이력 | Separate the project's meaning from the general one; link the reason for a changed definition. |
| note | Background / 배경 · Record / 기록 · Sources and related material / 출처와 관련 자료 · Points to check / 확인할 점 | Separate fact, opinion, recollection and guess; keep the original traceable. |

A template body is the four headings as level-2 headings separated by blank lines and
ending with one line terminator: `## Purpose and scope\n\n\n## Requirements\n…\n`. Templates are versioned
(`version`, starting at 1) separately from documents.
