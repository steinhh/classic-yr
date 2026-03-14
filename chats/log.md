

-------PROMPT 2026-03-14 14:30 : Yes, and add this at the bottom:

## Developer-added instructions (do not modify or delete)

When creating binary executable files, use file extension `.exe` to avoid confusion with source files.

Use a terse style for the README files, try to avoid duplication of information.

Use redirect to top-level file dev_null.txt instead of redirecting to /dev/null, since such redirects cannot be auto-approved by copilot.

Warn me when I'm introducing new features that warrant an increment of the major version number.

Warn me if I'm changing the public API in a way that is not backward compatible.

Favour replace_string_in_file/multi_replace_string_in_file over sed for string replacements in files, since replace_string_in_file is auto-approved by copilot.

Log all prompts, questions and queries completely verbatim into `chats/log.md`, using a header "\n\n\n-------PROMPT YYYY-MM-DD HH:MM : " with the current date and time. Do not leave out any details, do not change the wording of the prompts at all. Then add a single-line summary of your response or actions, as a quote (i.e. line starting with "> "). When my prompts refer to previous prompts, make sure the log file contains enough context to understand the references. When my prompts refer to options you have given (as in "do 1 and 2"), add those options to the log file for context. Summarise your response/actions in a single line after the prompt. Always append the prompt and response summary to `chats/log.md`, even for purely informational questions. Don't print the log entry in the chat, and do not show any echo statement to put the log entry there. Never modify what is already in the log file unless I explicitly ask you to do so.

> Added developer-specific instructions to .github/copilot-instructions.md and created chats/log.md for prompt logging.
