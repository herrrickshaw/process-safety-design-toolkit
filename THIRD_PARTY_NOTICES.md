# Third-party notices

## agent-skills (Addy Osmani)

The files under `.claude/skills/` and `.claude/references/` are copied unmodified from
https://github.com/addyosmani/agent-skills (commit fetched 2026-11-06) and are used under the MIT licence below.
Six of its twenty-five skills were kept: source-driven-development, doubt-driven-development, test-driven-development,
debugging-and-error-recovery, code-review-and-quality, documentation-and-adrs, plus the four reference files they link to.

    MIT License
    
    Copyright (c) 2025 Addy Osmani
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## gstack (Garry Tan)

No files were copied from https://github.com/garrytan/gstack (MIT). Its skills call gstack's own installed scripts
(`gstack-skill-start`, update checks, optional telemetry), so vendoring them would add runtime dependencies this
toolkit does not allow. The working rules in `CLAUDE.md` (root cause before fix, review before ship, freeze the
scope when debugging, regression test for every fix) are our own wording of the same ideas.
