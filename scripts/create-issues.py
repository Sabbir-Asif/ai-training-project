#!/usr/bin/env python3
"""Create GitHub labels, milestones and issues from the issue breakdown plan.

Usage:
  python3 scripts/create-issues.py            # dry run (prints what would happen)
  python3 scripts/create-issues.py --apply    # create everything via the gh CLI

Idempotent: skips issues whose title already exists, reuses labels/milestones.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parent.parent / "docs/superpowers/plans/2026-11-06-devpulse-issue-breakdown.md"
APPLY = "--apply" in sys.argv

DOD = """

---
### Definition of Done
- [ ] Implemented on a branch `feat/T##-slug`, one PR that closes this issue
- [ ] Automated tests added/updated and passing; lint, typecheck and build green in CI
- [ ] Input validated on the backend; ownership checks present where data is user-scoped
- [ ] Loading, empty, success and error states handled (frontend work)
- [ ] No secrets, passwords or tokens in code, logs or API responses
- [ ] Docs / `CLAUDE.md` updated if conventions or commands changed
"""

LABEL_COLORS = {"area": "1d76db", "type": "0e8a16", "priority": "d93f0b"}
MILESTONE_DESC = {
    "M0 Foundation": "Repo, tooling, CI, design system, backend/frontend cores, schema",
    "M1 Authentication": "Register, login, logout, JWT sessions",
    "M2 Tasks & Bugs": "Tasks/bugs API, list and Kanban views",
    "M3 Knowledge Vault": "Tags, Markdown notes, code snippets",
    "M4 Search & Command Palette": "Global search and Ctrl/Cmd+K palette",
    "M5 Dashboard": "Workspace overview",
    "M6 Hardening & Release": "Tests, a11y, security, deployment, docs, v1.0.0",
}


def gh(*args, check=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"gh {' '.join(args[:3])} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def parse():
    text = PLAN.read_text()
    issues = []
    for block in re.split(r"^## (?=T\d\d )", text, flags=re.M)[1:]:
        head, _, rest = block.partition("\n")
        m = re.match(r"(T\d\d) (.+)", head)
        tid, title = m.group(1), m.group(2).strip()
        meta, body = {}, []
        for line in rest.splitlines():
            mm = re.match(r"(Labels|Milestone|Depends): (.*)", line)
            if mm and not body:
                meta[mm.group(1)] = mm.group(2).strip()
            else:
                body.append(line)
        issues.append({
            "id": tid,
            "title": f"[{tid}] {title}",
            "labels": [x.strip() for x in meta["Labels"].split(",")],
            "milestone": meta["Milestone"],
            "depends": [] if meta["Depends"] == "none" else re.findall(r"T\d\d", meta["Depends"]),
            "body": "\n".join(body).strip().rstrip("-").strip(),
        })
    return issues


def main():
    issues = parse()
    labels = sorted({l for i in issues for l in i["labels"]})
    milestones = list(dict.fromkeys(i["milestone"] for i in issues))
    print(f"{len(issues)} issues, {len(labels)} labels, {len(milestones)} milestones")
    if not APPLY:
        for i in issues:
            print(f"  {i['title']}  [{i['milestone']}]  labels={i['labels']}  depends={i['depends']}")
        print("\nDry run only. Re-run with --apply to create.")
        return

    for l in labels:
        gh("label", "create", l, "--color", LABEL_COLORS.get(l.split(":")[0], "ededed"), "--force")
    existing_ms = {m["title"] for m in json.loads(gh("api", "repos/{owner}/{repo}/milestones?state=all&per_page=100"))}
    for m in milestones:
        if m not in existing_ms:
            gh("api", "repos/{owner}/{repo}/milestones", "-f", f"title={m}", "-f", f"description={MILESTONE_DESC.get(m, '')}")

    existing = {i["title"]: i["number"] for i in json.loads(gh("issue", "list", "--state", "all", "--limit", "500", "--json", "title,number"))}
    numbers = {}
    for i in issues:
        if i["title"] in existing:
            numbers[i["id"]] = existing[i["title"]]
            print(f"skip   {i['title']} (#{numbers[i['id']]})")
            continue
        body = i["body"]
        if i["depends"]:
            body = f"**Depends on:** {', '.join('#%d' % numbers[d] for d in i['depends'])}\n\n{body}"
        body = re.sub(r"\bT\d\d\b", lambda m: f"#{numbers[m.group(0)]}" if m.group(0) in numbers else m.group(0), body)
        body += DOD.replace("T##", i["id"])
        url = gh("issue", "create", "--title", i["title"], "--body", body,
                 "--milestone", i["milestone"], *[a for l in i["labels"] for a in ("--label", l)])
        numbers[i["id"]] = int(url.rstrip("/").split("/")[-1])
        print(f"create {i['title']} -> {url}")


if __name__ == "__main__":
    main()
