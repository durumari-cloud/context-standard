# Durumari Context Standard

**Version 0.1.0 (draft)** — a document format and a small set of rules that let any AI
agent, and any person, read and write a team's shared context the same way.

Teams now work with several coding agents at once. Each agent forgets between sessions,
and each reads its own instruction file. The Durumari Context Standard gives them one
shared memory with a fixed shape:

- **Documents with immutable revisions.** Every change is a new revision; nothing is
  overwritten. Readers can ask for the current text or pin an old revision.
- **Addressable sections.** A body is split at Markdown headings by one exact algorithm.
  Each section has a stable id and a SHA-256, so an agent can cite exactly what it read
  and a writer can refuse to overwrite text that changed underneath it.
- **Thirteen kinds** (decision, spec, plan, report, issue, …) with writing templates,
  and **document types** with typed columns on top of them.
- **Provenance and supersession.** A revision says where it came from and which earlier
  text it replaces; the current view hides replaced text without deleting history.
- **Work logs** that let one agent hand a task to another.
- **Writing conventions** (`<topic> — <conclusion>` titles, conclusion-first summaries,
  issue keys as tags) and the **agent instruction block** for `AGENTS.md`, `CLAUDE.md`
  and `GEMINI.md`.

## Repository layout

| Path | Content |
|---|---|
| [`spec/`](spec/README.md) | The specification. Normative rules and implementation-defined values are kept apart. |
| `schemas/` | JSON Schemas (draft 2020-12) for documents, revisions, sections, provenance, supersession, document types, properties and work logs. |
| `registry/` | Machine-readable kinds, writing templates and standard document types. |
| `templates/` | `AGENTS.md`, `CLAUDE.md` and `GEMINI.md`, generated from `templates/source/` by `templates/generate.py`. |
| `examples/` | Synthetic example documents, a work log, a custom type and a property event. |
| `conformance/` | The conformance suite: reference algorithms, section test vectors, invalid fixtures and tests. |

## Running the conformance suite

```sh
python -m pip install --require-hashes -r conformance/requirements.txt
python -m pytest -q conformance
```

or, with [uv](https://docs.astral.sh/uv/): `uv run --no-project --with jsonschema --with pytest pytest -q conformance`.

To check your own exported files:

```sh
python conformance/checks.py my-export/*.json
```

The checker validates each file against its schema and then applies the rules a schema
cannot express: sections recomputed from the body, section hashes, consecutive
revisions, effective state recomputed from supersession effects, property values against
their column types, and the work-log format.

To write the instruction files into a repository:

```sh
python templates/generate.py --project <your-project-id> --out path/to/repo
```

Text outside the managed markers is kept.

## Status

v0.1 is a draft derived from the Durumari reference implementation. Feedback and
independent implementations are welcome; see `CHANGELOG.md` for changes.

## Licensing

- Specification text (`spec/`, this README, `CHANGELOG.md`): **CC BY 4.0** — see
  [`LICENSE-docs`](LICENSE-docs).
- Schemas, registries, templates, examples and code: **Apache License 2.0** — see
  [`LICENSE`](LICENSE).

`.reuse/dep5` records which license applies to which path; source files also carry SPDX
headers.

**Trademark.** "Durumari" and the Durumari logo are trademarks of their owner. Neither
license grants permission to use them. You may state that an implementation "conforms to
the Durumari Context Standard v0.1" when it passes the conformance suite; do not use the
name in a way that suggests endorsement.

---

## 한국어 안내

**두루마리 Context 표준 v0.1(초안)** 은 여러 AI Agent와 사람이 팀의 공유 맥락(결정,
명세, 계획, 결과 보고, 규칙, 작업 기록)을 같은 방식으로 읽고 쓰기 위한 문서 형식과
규칙입니다.

- **판본(revision)은 고치지 않습니다.** 바꿀 때마다 새 판본이 생기고, 현재 본문과 고정한
  옛 판본을 구분해 읽습니다.
- **절(section) 단위로 읽고 고칩니다.** 본문은 Markdown 제목에서 정해진 알고리즘으로
  나뉘고, 절마다 고정 id와 sha256이 있어 읽은 근거를 정확히 남기고, 그사이 바뀐 절을
  덮어쓰지 않습니다.
- **13가지 kind**(결정·명세·계획·보고·쟁점 등)와 작성 템플릿, 그 위의 **문서 유형**과
  컬럼이 있습니다.
- **출처(provenance)와 대체(supersession).** 새 문서가 옛 문서의 일부나 전체를
  대체하면 현재 보기에서는 가려지되 이력은 남습니다.
- **작업 기록**으로 다른 Agent에게 일을 넘깁니다.
- **작성 규칙**: 제목은 `<주제> — <결론>`, 요약 첫 문장은 결론, 이슈 키는 태그로.
  `AGENTS.md` 관리 블록 하나를 `CLAUDE.md`·`GEMINI.md`가 가져다 씁니다.

명세(`spec/`)는 영어가 기준이며, 규범(normative) 규칙과 구현이 정하는 운영 값(보관
단계 일수, 토큰 한도 등, 11장)을 나눠 적었습니다. 적합성 시험은 위의 명령으로 실행합니다.

라이선스: 명세 본문은 CC BY 4.0, 스키마·템플릿·코드는 Apache-2.0입니다.
"두루마리(Durumari)"는 상표이며 두 라이선스 어느 쪽도 상표 사용을 허락하지 않습니다.
