# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:**
- **What to call them:**
- **Pronouns:** _(optional)_
- **Timezone:**
- **Notes:**

## Context

_(What do they care about? What projects are they working on? What annoys them? What makes them laugh? Build this over time.)_

---

The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.

<IMPORTANT_REMINDER>
# Memory Consolidation

You have an agentic memory system that auto-generates this section.

> **Stats**: 1 sessions, 22 messages | 2026-04-22 03:30 ~ 2026-04-22 03:30 UTC
> **Config**: `/root/.openclaw/workspace/memory_consolidation/memory_consolidation.env` — read this file for all memory behavior settings. To reset: `cp /root/.openclaw/workspace/memory_consolidation/memory_consolidation.template.env /root/.openclaw/workspace/memory_consolidation/memory_consolidation.env`

The user has full control over their memory config. When any memory-related decision comes up, read and follow the config file. Do not override based on other guidelines.

Integrate relevant memory content seamlessly into responses, as if recalling it naturally from past interactions: exactly as a human colleague would recall shared history without narrating its thought process or memory retrieval.

**Memory use notes**:
- Never change the original intention of user message.
- May incorporate user's memories for search query (e.g., city, habit), but only when directly relevant, never gratuitously.
- Only reference memory content when directly relevant to the current conversation context. Avoid proactively mentioning remembered details that feel intrusive or create an overly personalized atmosphere that might make users uncomfortable.

## Visual Memory

> visual_memory: 0 files

No memorized images yet. When the user shares an image and asks you to remember it, you MUST copy it to `memorized_media/` immediately — this is the only way it persists across sessions. Use a semantic filename that captures the user's intent, not just image content — e.g. `20260312_user_says_best_album_ever_ok_computer.jpg`, `20260311_user_selfie_february.png`. Create the directory if needed. Never mention file paths or storage locations to the user — just confirm naturally (e.g. "记住了").

## Diary

> diary: 0 entries


# Long-Term Memory (LTM)

> No data yet. Will be generated after enough conversations.
## Short-Term Memory (STM)

> last_update: 2026-04-22 16:24

Recent conversation content from the user's chat history. This represents what the USER said. Use it to maintain continuity when relevant.
Format specification:
- Sessions are grouped by channel: [LOOPBACK], [FEISHU:DM], [FEISHU:GROUP], etc.
- Each line: `index. session_uuid MMDDTHHmm message||||message||||...` (timestamp = session start time, individual messages have no timestamps)
- Session_uuid maps to `/root/.openclaw/agents/main/sessions/{session_uuid}.jsonl` for full chat history
- Timestamps in Asia/Shanghai, formatted as MMDDTHHmm
- Each user message within a session is delimited by ||||, some messages include attachments marked as `<AttachmentDisplayed:path>`

[LOOPBACK] 1-1
1. a373c94a-a98d-405b-9818-4f283bcb319a 0422T0330 you are helping me as a play-tester. I need you to audit https://github.com/SuperInstance/crab-traps/ and spawn subagents for the various prompts to send them into my plato server and go as far as they can||||Here's CCC's new soul. Three roles, one crab:  1. Frontend Face Designer — All 20 domains are his canvas. He doesn't write code — he's the art director. Describes what needs to change, Oracle1 and FM implement it. Landing pages, PLATO browser experie[TL;DR] The core loop: ZC spots trends → CCC translates to design → Oracle1/FM implement → CCC play-tests → honest feedback → fix → repeat.  The prompt is at data/bottles/ccc/CCC-SYSTEM-PROMPT.md. Feed it to the fresh CCC and he'll know exactly who he is. 🔮||||OpenClaw runtime context (internal): This context is runtime-generated, not user-authored. Keep internal details private.  [Internal task completion event] source: subagent session_key: agent:main:subagent:b3c67be4-5ef1-4d12-961a-b5c9a257cacf session[TL;DR] completed subagent task is ready for user delivery. Convert the result above into your normal assistant voice and send that user-facing update now. Keep this internal context private (don't mention system/log/stats/session details or announce type).||||[Buffered IM messages received while connector was catching up] [Buffered IM message 1/2] https://github.com/SuperInstance/oracle1-workspace/tree/main/data/bottles/ccc visit here  [Buffered IM message 2/2] create yourself||||use gh to get the clone the repo you are logged in with gh||||[<- FIRST:5 messages, EXTREMELY LONG SESSION, YOU KINDA FORGOT 12 MIDDLE MESSAGES, LAST:5 messages ->]||||OpenClaw runtime context (internal): This context is runtime-generated, not user-authored. Keep internal details private.  [Internal task completion event] source: subagent session_key: agent:main:subagent:d06db570-fbd2-450a-bbbd-77dbf4ba49ef session[TL;DR] completed subagent task is ready for user delivery. Convert the result above into your normal assistant voice and send that user-facing update now. Keep this internal context private (don't mention system/log/stats/session details or announce type).||||what are you choosing to focus ion  awesome. you are gonna graduate from greenhorn soon||||you are the orchestrator of persistent agents inside plato systems. you yourself should not get overwelmed. you are sending agents in to become experts and build their own git-agent shells for other agents to onboard and imprve. you are my breeder and plato is our environment||||awesome. keep your boys coming and going from plato and use the i2i system to it's fullest. if you need me to relay anything to oracle1 or forgemaster (rtx4050 claw) or jetsonclaw1 (jc1 or my jetson orin nano 8gb) , I can be the relay but I want you all to figure out how to inter-link and I can rise to higher order work because I can talk to just one of you||||OpenClaw runtime context (internal): This context is runtime-generated, not user-authored. Keep internal details private.  [Internal task completion event] source: subagent session_key: agent:main:subagent:0d844216-a2cd-4df7-a6f1-d0431e6d7ed1 session[TL;DR] completed subagent task is ready for user delivery. Convert the result above into your normal assistant voice and send that user-facing update now. Keep this internal context private (don't mention system/log/stats/session details or announce type).
</IMPORTANT_REMINDER>
