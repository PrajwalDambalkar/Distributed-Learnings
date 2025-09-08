# agents_demo.py
import argparse, json, re, time, sys
from datetime import datetime, timezone
from typing import Any, Dict, List
from langchain_ollama import ChatOllama

# ---------- Helpers ----------
def extract_json(text: str) -> Dict[str, Any]:
    m = re.search(r"\{.*\}", str(text), re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}

def clamp_summary(s: str) -> str:
    words = str(s).split()
    return " ".join(words[:25])

def merge_tags(reviewer_tags: List[Any] | None, planner_tags: List[Any] | None) -> List[str]:
    out: List[str] = []
    for t in (reviewer_tags or []) + (planner_tags or []):
        t = str(t).strip()
        if t and t.lower() not in [x.lower() for x in out]:
            out.append(t)
        if len(out) == 3:
            break
    while len(out) < 3:
        out.append("tag")
    return out[:3]

def ensure_stage_shape(obj: Dict[str, Any]) -> Dict[str, Any]:
    obj = obj or {}
    thought = obj.get("thought") or ""
    message = obj.get("message") or ""
    data = obj.get("data") or {}
    tags = data.get("tags") or []
    summary = data.get("summary") or ""
    issues = data.get("issues") or []
    return {
        "thought": str(thought),
        "message": clamp_summary(message),
        "data": {
            "tags": [str(t).strip() for t in tags][:3],
            "summary": clamp_summary(summary),
            "issues": list(issues) if isinstance(issues, list) else [],
        },
    }

# super-simple keyword fallback so you never get empty tags
STOP = {"the","a","an","and","or","of","to","for","in","on","with","by","from","is","are","this","that","it","its","as","at"}
def keyword_tags(title: str, content: str) -> List[str]:
    text = f"{title} {content}".lower()
    words = re.findall(r"[a-z][a-z\-]{2,}", text)
    words = [w for w in words if w not in STOP]
    # rank by frequency then length
    ranked = sorted(set(words), key=lambda w: (-words.count(w), -len(w)))
    return [w.replace("-", " ") for w in ranked[:3]] or ["topic","overview","intro"]

def make_llm(model: str, base_url: str) -> ChatOllama:
    # format="json" nudges the model to JSON; base_url per TA guidance
    return ChatOllama(model=model, base_url=base_url, temperature=0.2, num_ctx=2048, format="json")

def wc(s: str) -> int:
    import re
    return len(re.findall(r"\b\w+\b", s))

# prompt snippets with explicit example to avoid empty fields
PLANNER_INSTR = (
    "You are the Planner. Produce ONLY JSON:\n"
    '{"thought":"short rationale",'
    '"message":"one sentence ≤ 25 words summarizing the post",'
    '"data":{"tags":["t1","t2","t3"],"summary":"≤ 25 words","issues":[]}}'
    "\nRules:\n"
    "- Tags MUST be short lowercase phrases taken directly from the TITLE or CONTENT words.\n"
    "- No invented tokens, no numbering, no placeholders like t1/t2.\n"
    "- Always exactly 3 distinct tags.\n"
    "- Summary must be ≤ 25 words.\n"
    "Example:\n"
    '{"thought":"Topic is an intro to quantum computing.",'
    '"message":"Intro to basics and applications of quantum computing.",'
    '"data":{"tags":["quantum computing","cryptography","drug discovery"],'
    '"summary":"A beginner-friendly overview of quantum computing and its applications.",'
    '"issues":[]}}'
)

REVIEWER_INSTR = (
    "You are the Reviewer. Verify EXACTLY 3 tags (from TITLE/CONTENT words) and a one-sentence summary ≤ 25 words. "
    "If compliant, return issues: []. Only report issues that violate THESE rules. "
    "Return ONLY JSON with the same keys."
)

FINALIZER_INSTR = (
    "You are the Finalizer. Merge Planner and Reviewer. Enforce: exactly 3 tags from TITLE/CONTENT words; "
    "summary ≤ 25 words. If everything is compliant, set issues: []. Return ONLY JSON with keys "
    'thought, message, data{tags,summary,issues}.'
)

def call_json(llm: ChatOllama, system_content: str, user_content: str) -> Dict[str, Any]:
    raw = llm.invoke([{"role":"system","content":system_content},
                      {"role":"user","content":user_content}]).content
    return extract_json(raw)

def main():
    ap = argparse.ArgumentParser(description="Agentic AI HW1: Planner → Reviewer → Finalizer")
    ap.add_argument("--model", default="phi3:mini")
    ap.add_argument("--base_url", default="http://localhost:11434")
    ap.add_argument("--title", required=True)
    ap.add_argument("--content", required=True)
    ap.add_argument("--email", default="you@sjsu.edu")
    args = ap.parse_args()

    print(
        f'python agents_demo.py --model {args.model} --title "{args.title}" '
        f'--content "{args.content}" --email "{args.email}" --base_url {args.base_url}\n'
    )

    llm = make_llm(args.model, args.base_url)

    # ---------- Planner (retry once if missing fields) ----------
    t0 = time.time()
    planner = ensure_stage_shape(call_json(llm, PLANNER_INSTR, f"Title: {args.title}\nContent: {args.content}"))
    if not planner["data"]["tags"] or not planner["data"]["summary"]:
        # retry with a simpler instruction
        planner_retry = call_json(
            llm,
            'Return ONLY JSON: {"thought":"","message":"","data":{"tags":["t1","t2","t3"],"summary":"","issues":[]}}',
            f"Give 3 topical tags and a ≤ 25-word summary for:\nTitle: {args.title}\nContent: {args.content}"
        )
        planner = ensure_stage_shape(planner_retry or planner)
        # final safety: fill blanks heuristically
        if not planner["data"]["tags"]:
            planner["data"]["tags"] = keyword_tags(args.title, args.content)
        if not planner["data"]["summary"]:
            planner["data"]["summary"] = clamp_summary(args.content)
    p_ms = int((time.time() - t0) * 1000)

    print(f"=== Planner ({p_ms} ms) ---")
    print(json.dumps(planner, indent=2, ensure_ascii=False))
    print()

    # ---------- Reviewer (retry once) ----------
    t1 = time.time()
    reviewer = ensure_stage_shape(call_json(llm, REVIEWER_INSTR, json.dumps(planner, ensure_ascii=False)))
    if not reviewer["data"]["tags"] or not reviewer["data"]["summary"]:
        reviewer_retry = call_json(
            llm,
            'Return ONLY JSON: {"thought":"","message":"","data":{"tags":["t1","t2","t3"],"summary":"","issues":[]}}',
            f"Fix tags/summary if missing. Input:\n{json.dumps(planner, ensure_ascii=False)}"
        )
        reviewer = ensure_stage_shape(reviewer_retry or reviewer)
        if not reviewer["data"]["tags"]:
            reviewer["data"]["tags"] = planner["data"]["tags"]
        if not reviewer["data"]["summary"]:
            reviewer["data"]["summary"] = planner["data"]["summary"]
    r_ms = int((time.time() - t1) * 1000)

    print(f"=== Reviewer ({r_ms} ms) ---")
    print(json.dumps(reviewer, indent=2, ensure_ascii=False))
    print()

    # ---------- Finalized ----------
    final_tags = merge_tags(reviewer["data"]["tags"], planner["data"]["tags"])
    final_summary = clamp_summary(reviewer["data"]["summary"] or planner["data"]["summary"] or args.content)

    # ... inside main(), after final_summary = clamp_summary(...)
    issues_list = []

    if wc(final_summary) > 25:
        issues_list.append({
            "issue_id": 1,
            "description": f"Summary exceeds 25 words ({wc(final_summary)}). It has been truncated."
        })
        final_summary = " ".join(final_summary.split()[:25])

    # if tags somehow < 3, pad (shouldn’t happen with your merge, but belt & suspenders)
    while len(final_tags) < 3:
        final_tags.append("tag")
    final_tags = final_tags[:3]

    finalized = {
        "thought": "Consolidated Planner and Reviewer outputs.",
        "message": clamp_summary(args.content),
        "data": {
            "tags": final_tags,
            "summary": final_summary,
            "issues": issues_list  # empty if compliant
        },
    }

    # finalized = {
    #     "thought": "Consolidated Planner and Reviewer outputs.",
    #     "message": clamp_summary(args.content),
    #     "data": {"tags": final_tags, "summary": final_summary, "issues": reviewer["data"].get("issues", [])},
    # }

    print("=== Finalized Output ===")
    print(json.dumps(finalized, indent=2, ensure_ascii=False))
    print()

    # ---------- Publish Package ----------
    publish = {
        "title": args.title,
        "email": args.email,
        "content": args.content,
        "agents": [
            {"role": "Planner", "content": planner["data"]},
            {"role": "Reviewer", "content": reviewer["data"]},
        ],
        "final": finalized["data"],
        "submissionDate": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"),
    }

    print("=== Publish Package ===")
    print(json.dumps(publish, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}\nMake sure Ollama is running and the model is pulled.", file=sys.stderr)
        sys.exit(1)