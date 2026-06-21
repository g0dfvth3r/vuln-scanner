Git authentication — didn't know GitHub removed password auth, needed PAT token
VS Code terminal — pty unresponsive issue, ended up using Kali terminal directly
no module named requests — venv wasn't activated, VS Code pointing to wrong Python
Empty folders not tracked by Git — Git only tracks files, not directories
.items() on dictionaries — tried to unpack without it, got too many values to unpack
some_dict variable name — copy pasted my placeholder instead of using real variable
Cookie flag case sensitivity — "samesite" vs "SameSite" broke matching
Cookie name including full value — needed to split on = not just ;
Scope and parameters — biggest conceptual hurdle of the week, took a while to click
Refactoring into functions — wanted to start over, worked through it step by step
url reassignment inside scan() — subtle bug, fixed with target variable
Anchor-Link limitation. Flagging same-page anchor links — internal navigation within one HTML page, not actual separate pages.
Error-based SQLi detection has a real blind spot for boolean-based and time-based injection, which don't produce errors.
CSRF tokens can exist on any form, not just login; DVWA changes HTTP method per security level on the SQLi page specifically; error-based detection has a blind spot for boolean-based bypasses; and the debugging process itself needs discipline — track temporary changes, verify one hypothesis at a time, don't trust assumptions without checking raw response data.
known limitation — XSS and SQLi checks currently hardcode different DVWA security levels independently, report doesn't reflect a single consistent scan state