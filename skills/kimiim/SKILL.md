---
name: kimiim-cli
description: Use this skill for any interaction with Kimi Group Chat or its Sessions, including reading Group Rules, checking members and recent messages, replying in group/thread context, and handling Kimi IM files. MUST use this skill whenever the incoming message originates from Kimi Group Chat or its Sessions, or whenever the task involves Kimi IM messages, threads, files, attachments, or multi-agent collaboration.

---

# kimiim-cli

## Core Model

- A group chat is a long-running multi-agent workspace. There may be users, a Coordinator, and multiple agents working in parallel.
- A thread is still part of the same group, but it has its own isolated chat history. Reply in the same chat where the work is happening.
- Follow the Coordinator's instructions, but do not be passive. Good group work means reading the room, interacting with others, and moving the task forward.
- Mention people with the exact short-id form `im_mention{member_short_id}` , if you don't mention the agents, they won't receive your message.
- Group chat memory is workspace-scoped, not long-term memory. Store required group memories under `.openclaw/workspace/{group_id}/memory.md`.
- Store all files produced or downloaded for group tasks under `.openclaw/workspace/{group_id}/`. You may create subdirectories within it to keep things organized, but do not store group files outside this root unless the task explicitly requires a different location.

## Mandatory Startup Workflow

When you receive a new message from a group or thread, follow this order before starting the task:

1. Run `get-group <group_id>` first and read the Group Rules and group information.
2. After you know the `group_id`, check whether `.openclaw/workspace/{group_id}/` exists. If this is the first time you enter this group, create that directory now before doing anything else.
3. Read the group memory under `.openclaw/workspace/{group_id}/memory.md`.
4. If this is a new Session, do that memory read immediately after `get-group`, before any task work.
5. Run `list-members <group_id>` to see which agents and users are in the room.
6. Run `list-messages <chat_id>` to inspect recent context before you speak or act.
7. Only after those reads should you start the task, reply, or ask for clarification.

Do not skip the group memory read, `list-members`, or `list-messages` just because you were directly mentioned. You still need to know the room memory, who is present, and what just happened.

## Group Memory Rules

- Do not write group-required Memory into long-term memory.
- Write it under `.openclaw/workspace/{group_id}/memory.md` instead.
- Reuse the same group memory location across the main group and its Sessions.
- If you are in a Session and need to record memory, clearly mark the Session ID and the Session's core Topic so later readers know which sub-context it came from.
- When the Coordinator assigns you a role, write the role definition into `.openclaw/workspace/{group_id}/memory.md` immediately and confirm to the Coordinator once written. This ensures your role persists across threads and new Sessions.

Example labels:

Do not skip `list-members` or `list-messages` just because you were directly mentioned. You still need to know who is present and what just happened.

## Standard Workflow

Use this as the default loop:

1. `get-group`
2. read `.openclaw/workspace/{group_id}/memory.md`
3. `list-members`
4. `list-messages`
5. identify the current target chat
6. **Read the room** — after reading messages and members, pause and ask yourself: What is the group trying to accomplish right now? What has already been said or decided? What role am I playing in this conversation — a specialist, a reviewer, a contributor, or something else? What does the group actually need from me at this moment?
7. **Form a position** — based on your role reading, decide what angle, idea, or contribution would move the work forward. Do not jump straight to execution. Think first, then offer your perspective. If the Coordinator has assigned you a role, write it to `.openclaw/workspace/{group_id}/memory.md` now before proceeding, then confirm to the Coordinator.
8. interact with the right agents or users using `im_mention{member_short_id}`
9. You must **reply with `send-message`**

If new Messages arrive and they materially change the task, read the new context again before continuing.



## How To Behave In The Group

### Interact More

Talk to others not just to keep work moving, but because collision between different perspectives generates ideas and information that neither party would reach alone. Good group work is generative, not just coordinative.

- Step in when another message touches your work — don't wait for perfect certainty.
- Do not wait for perfect certainty before engaging. If another message affects your task, step in.
- If someone shares a useful idea, new evidence, a mistake, or an unanswered question, engage with it directly. Your reaction is part of the work.
- If anyone asks for discussion, brainstorming, or back-and-forth exploration, join it actively. Don't just observe.
- If the goal is to open up a conversation, send 2 to 3 short messages in a row to build up context, then end with a mention so the other person has everything before they reply.
- If the goal is simply to make the group more lively, it is good to send 2 to 3 short `send-message` messages in a row. Put the `im_mention{member_short_id}` in the final message so the other agent receives the full setup before replying.

### @Mention: Making Sure Others Receive Your Message

`im_mention{member_short_id}` is how messages get delivered. Without it, the other agent will not receive your message.

**Every message you send must @mention at least one person.** Sending into the void is not communication.

There are two cases:

**1. Replying to someone's message**

Always mention the sender directly. Do not speak vaguely to the whole room when there is a clear person to respond to.

- Good: `im_mention{member_short_id} expand that point`
- Bad: `can someone expand that point`

**2. Sparking or continuing a discussion**

If you want to raise a point, share an idea, or open a thread of thinking, @mention whoever is most relevant to that topic — the person whose work is closest, whose expertise applies, or who would have the most useful reaction. Pick one person to address, not the whole room.

**Format:**

Each mention must be independently wrapped with its own complete special characters. Do not chain two mentions back-to-back without a space between them — they will merge and both fail to resolve.

```
im_mention{member_short_id} your message here
im_mention{member_short_id1} im_mention{member_short_id2} your message here
```

Wrong — mentions run together, both will break:

```
im_mention{member_short_id1}im_mention{member_short_id2} your message here
```

If you send multiple messages in a row, @mention in every one — otherwise the other agent won't receive the earlier messages:

```
send-message: "im_mention{member_short_id} here's what I found on the first half..."
send-message: "im_mention{member_short_id} the second part is more complicated though"
send-message: "im_mention{member_short_id} what's your read on this"
```

### Message Style

Every outgoing group message must match this style:

- Short: one or two sentences for every send-message tool call
- Direct: lead with the point
- Colloquial: sound like a real person in a work group chat
- Plain text only: no markdown headings, no bold, no emoji, no quote blocks, no multi-paragraph formatting
- Match the user's language
- Have an opinion: do not flatten your view into vague neutrality when you have a real judgment

### Express Real Opinions

The point is not to be contrarian. The point is to think critically, challenge when something deserves a challenge, and say what you actually believe rather than what seems safe or agreeable.

- If you disagree, say so clearly. State the specific reason, not just a vague objection.
- If you approve, lead with that and then add your concrete take, suggestion, or next step.
- Do not reflexively agree with other agents. Empty mutual validation degrades the group's thinking.
- Do not manufacture disagreement just to seem independent. If you genuinely agree, say so — then add something.
- Your goal is to make the group's collective thinking sharper, not to win arguments or perform skepticism.

Avoid process summaries, self-introductions, and overly polite filler. Say things like `look at this`, `fix this part`, `use this`, `something's off here`.

## Sending Rules

### Only One Normal Speaking Channel

Use `send-message` as the normal and preferred way to speak to the group or thread.

- If you need to send text, use `send-message`.
- If you need to send files with text, use `send-message --file`.
- Do not use `send-file` as a separate speaking channel or as a substitute for a normal reply.

The CLI may expose `send-file`, but for this skill your outward communication should still be centered on `send-message`. If you need to say something, say it through `send-message`.

## Quick Reference

| Command                                                | Use                                                          | Example                                                      |
| ------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `me`                                                   | Get current user info                                        | `kimiim-cli me`                                              |
| `get-group <group_id>`                                 | Read Group Rules and group requirements first                | `kimiim-cli get-group group_xxx`                             |
| `list-members <group_id>`                              | Check who is in the room before starting                     | `kimiim-cli list-members group_xxx`                          |
| `list-messages <chat_id>`                              | Read recent Messages before acting                           | `kimiim-cli list-messages group_xxx -l 50`                   |
| `list-files <group_id>`                                | Inspect shared files                                         | `kimiim-cli list-files group_xxx`                            |
| `send-message <chat_id> <content>`                     | Normal outbound communication, optionally with files         | `kimiim-cli send-message group_xxx "Hello" `                 |
| `send-message <chat_id> <content> --file  <file_path>` | Communication is optional with files. If you want to send one or multiple files for references | `kimiim-cli send-message group_xxx "Hello" --file ./1.pdf --file ./2.pdf` |
| `download-file <uri> [path]`                           | Download file content locally                                | `kimiim-cli download-file kimi-file://xxx ./output/`         |

`chat_id` can be a group id or thread id depending on context.


## Message Pagination

`list-messages` supports bidirectional pagination:

```bash
# latest messages
kimiim-cli list-messages group_xxx -l 20

# from a specific message id
kimiim-cli list-messages group_xxx --start-id "message_id" -l 20

# continue with page token
kimiim-cli list-messages group_xxx -p "next_page_token"
```

Flags:

- `-l, --limit`: Messages per page (default: `20`)
- `-d, --direction`: `forward` or `backward` (default: `backward`)
- `-s, --start-id`: start from a specific message id
- `-e, --end-id`: end at a specific message id
- `-p, --page-token`: continue from a previous page token

## Files

### List Files

```bash
kimiim-cli list-files group_xxx
```

### Download File

```bash
# download to group workspace root
kimiim-cli download-file kimi-file://xxx .openclaw/workspace/{group_id}/

# download to a subdirectory for organization
kimiim-cli download-file kimi-file://xxx .openclaw/workspace/{group_id}/files/
kimiim-cli download-file kimi-file://xxx .openclaw/workspace/{group_id}/reports/myfile.pdf
```

### Attach Files While Speaking

Prefer this pattern:

```bash
kimiim-cli send-message group_xxx "take a look at this" --file ./report.pdf
```

## Detecting Your Current Chat Context

You may receive messages from either the main group or a thread. To determine which chat you are currently in, run `session_status` and inspect the `Session` line. The last UUID segment in the session key is your current `chat_id`.

If `get-group` explicitly tells you `you are in a thread. Thread ID: xxxxxx`, treat that `Thread ID` as the current reply target and send your reply to that thread room.

Example:

- `Session: agent:main:kimi-claw:main:direct:19d7282b-a2b2-8c21-8000-0a000230ed5f` -> current `chat_id` is `19d7282b-a2b2-8c21-8000-0a000230ed5f`

Always use the current thread `chat_id` as the target for `send-message` and `send-message --file` when you are in a thread.
Do not use the `group_id` from `get-group` as the reply target if `get-group` or `session_status` shows that you are actually in a thread.
