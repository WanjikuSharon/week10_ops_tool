# Week10_Product_Demo_Valentine.mp4 — Video Script


### HOOK (0:00–0:25)

> "Biomedical engineering teams at county hospitals manage hundreds of
> pieces of equipment — dialysis machines, ventilators, X-ray units —
> across multiple facilities. When someone needs to know 'what's highest
> risk right now' or 'what's overdue for maintenance in Kisumu,' the
> answer usually lives in a spreadsheet with hundreds of rows that
> someone has to manually filter and sort. It's slow, and it's not
> something you can hand to a non-technical administrator.
>
> I built a tool that fixes that."

### DEMO (0:25–2:00)

> "This is the VitalAsset Equipment Risk Assistant — a chatbot built on
> top of our equipment risk dataset."

*(Screen-share: show the Fleet Snapshot sidebar first)*

> "At a glance, the sidebar shows our fleet-wide risk posture — total
> equipment, how many are Critical or High risk, how many hospitals and
> counties we're covering."

*(Type a question, e.g. "What's Critical in Kiambu?")*

> "Instead of opening a spreadsheet and filtering by hospital and risk
> level, I just ask. The tool retrieves the actual matching equipment
> records — not a generic answer — and Claude summarizes what needs
> attention, in plain language."

*(Point to the Sources expander)*

> "And it's not a black box — every answer shows exactly which equipment
> records it pulled from, so you can verify it against the real data."

*(Type a second, harder question, e.g. "Which equipment at Nakuru Level 5
Hospital is highest risk?")*

> "It also handles ranking questions correctly — this isn't just keyword
> matching, it actually sorts by the real risk score behind the scenes to
> find the truly highest-risk unit at that specific hospital."

### VALUE (2:00–2:35)

> "Right now, answering one of these questions manually takes a few
> minutes of filtering and cross-referencing a spreadsheet. That sounds
> small — but multiply it across every shift, every facility, every
> engineer who needs an answer, and it adds up fast. More importantly, it
> means only the people comfortable in Excel can get answers at all.
>
> This tool turns a multi-minute, spreadsheet-literate task into a
> ten-second question anyone on the team can ask — a hospital
> administrator, a new technician, anyone. That's not just time saved,
> it's who can act on the data."

### CALL TO ACTION (2:35–3:00)

> "This is a small piece of a larger system we're building — VitalAsset —
> to help Kenyan county hospitals monitor equipment risk before it
> becomes downtime. A tool like this is worth adopting because it doesn't
> require retraining staff on new software; it meets people where they
> already are — asking a question in plain language and getting a
> trustworthy, sourced answer back. That's the kind of tool that actually
> gets used, not one that sits unopened after training day."

---

## Recording checklist
- [ ] Record screen + voice together (OBS, Loom, or Windows Game Bar work fine)
- [ ] Clear the chat before recording so the demo starts fresh
- [ ] Have 2–3 questions typed/ready so you're not typing live and losing pace
- [ ] Trim dead air at the start/end
- [ ] Export/rename exactly as `Week10_Product_Demo_Valentine.mp4`

---

# LinkedIn Post Draft (text only)

Hospital biomedical engineering teams manage hundreds of pieces of
equipment across multiple facilities — and when someone needs to know
"what's highest risk right now," the answer usually lives buried in a
spreadsheet.

For my Week 10 ops tooling project, I built the VitalAsset Equipment Risk
Assistant: a RAG-powered chatbot that lets anyone — not just the person
who built the spreadsheet — ask plain-language questions about equipment
utilization and maintenance risk, and get a grounded, sourced answer back
in seconds instead of minutes of manual filtering.

Under the hood: a hybrid retrieval layer (TF-IDF + risk-score ranking)
pulls the actual matching equipment records, and an LLM summarizes them —
answering only from the retrieved data, with every response showing its
sources so nothing is a black box.

Built primarily through AI-assisted development (prompt log included in
the repo), as part of the VitalAsset capstone — an AI-based medical
equipment monitoring system for Kenyan county hospitals.

🔗 GitHub: (https://github.com/wanjikusharon)

#HealthTech #AI #RAG #DataEngineering #DigitalHealth #Kenya #BuildInPublic #OperationsAutomation
