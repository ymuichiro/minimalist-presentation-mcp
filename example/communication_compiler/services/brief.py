from __future__ import annotations

from html import escape

from example.communication_compiler.models import SessionState


def build_brief_markdown(session: SessionState) -> str:
    if session.current_message_kernel is None:
        raise ValueError("MESSAGE_KERNEL_REQUIRED")
    kernel = session.current_message_kernel
    title = kernel.claim
    evidence = "\n".join(
        f"- **{item.title}** ({item.strength}, {item.source_ref}): {item.summary}"
        for item in session.supporting_evidence
    ) or "- 現時点で、この主張を直接支える社内データは確認できていません。"
    gaps = "\n".join(
        f"- **{gap.description}**: {gap.why_it_matters} Suggested source: {gap.suggested_source}"
        for gap in session.evidence_gaps
    ) or "- 根拠整理が未実行です。"
    objections = "\n".join(
        f"- **{item.objection}**: {item.response_strategy} Needed evidence: {item.evidence_needed}"
        for item in session.objections
    ) or "- 想定反論は未整理です。"
    notes = "\n".join(f"- {note}" for note in kernel.notes) or "- No additional notes."
    return f"""# {title}

## 1. 4-Line Message Kernel

| Line | Message |
|---|---|
| Audience Premise | {kernel.premise} |
| Complication | {kernel.complication} |
| Core Claim | {kernel.claim} |
| Requested Decision / Action | {kernel.action} |

## 2. Executive Summary

{session.audience or "聞き手"}に対して、現状の AI 投資を業務成果へ接続するため、主張・根拠・反論を分けて判断可能な形に整理します。

## 3. Why This Matters

{kernel.complication}

## 4. Core Argument

{kernel.claim}

この主張は、単なるツール導入ではなく、業務プロセス設計と投資配分の問題として扱うべきです。

## 5. Supporting Evidence

{evidence}

## 6. Evidence Gaps

{gaps}

## 7. Likely Objections and Responses

{objections}

## 8. Recommended Decision

{kernel.action}

## 9. Appendix: Agent Notes

{notes}
"""


def brief_markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    html_lines: list[str] = []
    in_ul = False
    in_table = False
    for raw in lines:
        line = raw.strip()
        if not line:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            continue
        if line.startswith("# "):
            html_lines.append(f"<h1>{escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            html_lines.append(f"<h2>{escape(line[3:])}</h2>")
        elif line.startswith("|") and "|" in line[1:]:
            if "---" in line:
                continue
            cells = [escape(cell.strip()) for cell in line.strip("|").split("|")]
            if not in_table:
                html_lines.append("<table><tbody>")
                in_table = True
            html_lines.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
        elif line.startswith("- "):
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{escape(line[2:])}</li>")
        else:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            html_lines.append(f"<p>{escape(line)}</p>")
    if in_ul:
        html_lines.append("</ul>")
    if in_table:
        html_lines.append("</tbody></table>")
    body = "\n".join(html_lines)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Communication Compiler Brief</title>
  <style>
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #111; background: #fff; }}
    main {{ width: min(880px, calc(100vw - 40px)); margin: 48px auto; }}
    h1 {{ font-size: 36px; line-height: 1.1; letter-spacing: 0; }}
    h2 {{ margin-top: 34px; font-size: 20px; letter-spacing: 0; }}
    p, li, td {{ line-height: 1.65; }}
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
    td {{ border: 1px solid #e5e5e5; padding: 10px; vertical-align: top; }}
  </style>
</head>
<body><main>{body}</main></body>
</html>"""
