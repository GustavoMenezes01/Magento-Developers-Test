#!/usr/bin/env python3
"""AD0-E724 Adobe Commerce quiz — generates questions from study notes via Claude API."""

import json
import os
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path

import anthropic

STUDY_FILE = Path(__file__).parent / "AD0-E724_guia_completo.md"
PROGRESS_FILE = Path(__file__).parent / "progress.json"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

DOMAIN_LABELS = {
    0: "Todos os domínios",
    1: "Arquitetura (52%)",
    2: "Customizações (36%)",
    3: "Cloud (12%)",
}

DOMAIN_PATTERNS = {
    1: r"(# DOMÍNIO 1.*?)(?=\n# DOMÍNIO 2|\Z)",
    2: r"(# DOMÍNIO 2.*?)(?=\n# DOMÍNIO 3|\Z)",
    3: r"(# DOMÍNIO 3.*?)$",
}


def extract_domain(content: str, domain: int) -> str:
    if domain == 0:
        return content
    match = re.search(DOMAIN_PATTERNS[domain], content, re.DOTALL)
    return match.group(1).strip() if match else content


def generate_questions(section: str, count: int, client: anthropic.Anthropic) -> list[dict]:
    system_prompt = (
        "You are an Adobe Commerce (Magento 2) AD0-E724 exam question generator. "
        "Generate realistic multiple-choice questions that test practical developer knowledge — "
        "not just memorization, but understanding of WHY things work the way they do. "
        "Return valid JSON only. No markdown fences, no extra text outside the JSON array."
    )

    user_content = (
        f"Generate exactly {count} multiple-choice questions from the study material below.\n\n"
        "Return a JSON array with this exact structure:\n"
        "[\n"
        "  {\n"
        '    "question": "question text",\n'
        '    "options": {"a": "...", "b": "...", "c": "...", "d": "..."},\n'
        '    "correct": "a",\n'
        '    "explanation": "brief explanation of why this answer is correct",\n'
        '    "topic": "short topic label"\n'
        "  }\n"
        "]\n\n"
        "Rules:\n"
        "- Exactly 4 options per question\n"
        "- Exactly 1 correct answer\n"
        "- Distribute difficulty: ~30% easy, ~50% medium, ~20% hard\n"
        "- Wrong options must be plausible, not obviously wrong\n\n"
        f"Study material:\n\n{section}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_content,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
            }
        ],
    )

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
    raw = re.sub(r"\n?```\s*$", "", raw)
    return json.loads(raw)


def run_quiz(questions: list[dict], domain_label: str) -> dict:
    correct_count = 0
    wrong_topics: list[str] = []

    sep = "━" * 52
    thin = "─" * 52

    print(f"\n{BOLD}{CYAN}{sep}{RESET}")
    print(f"{BOLD}  AD0-E724 · {domain_label} · {len(questions)} perguntas{RESET}")
    print(f"{CYAN}{sep}{RESET}\n")

    for i, q in enumerate(questions, 1):
        topic = q.get("topic", "")
        print(f"{BOLD}[{i}/{len(questions)}]{RESET}  {DIM}{topic}{RESET}")
        print(f"\n{q['question']}\n")

        for key in ("a", "b", "c", "d"):
            print(f"  {CYAN}{key}{RESET}) {q['options'][key]}")

        while True:
            answer = input(f"\n{BOLD}Resposta (a/b/c/d): {RESET}").strip().lower()
            if answer in ("a", "b", "c", "d"):
                break
            print("  Digite a, b, c ou d.")

        if answer == q["correct"]:
            correct_count += 1
            print(f"\n  {GREEN}✓ Correto!{RESET}  Score parcial: {correct_count}/{i}")
        else:
            correct_text = q["options"][q["correct"]]
            print(f"\n  {RED}✗ Errado.{RESET}  Correto: {CYAN}{q['correct']}{RESET}) {correct_text}")
            print(f"  {DIM}{q.get('explanation', '')}{RESET}")
            wrong_topics.append(topic)

        print(f"\n{DIM}{thin}{RESET}\n")

    pct = round(correct_count / len(questions) * 100)
    color = GREEN if pct >= 78 else (YELLOW if pct >= 60 else RED)
    status = "Aprovado no simulado!" if pct >= 78 else "Abaixo da meta (78%)"

    print(f"{BOLD}{color}Resultado: {correct_count}/{len(questions)} ({pct}%) — {status}{RESET}")

    if wrong_topics:
        unique_topics = list(dict.fromkeys(wrong_topics))
        print(f"{YELLOW}Revisar: {', '.join(unique_topics[:4])}{RESET}")

    print()

    return {
        "date": datetime.now().isoformat(),
        "domain": domain_label,
        "total": len(questions),
        "correct": correct_count,
        "percentage": pct,
    }


def save_progress(result: dict) -> None:
    data: list[dict] = []
    if PROGRESS_FILE.exists():
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    data.append(result)
    PROGRESS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def show_stats() -> None:
    if not PROGRESS_FILE.exists():
        print("Nenhum histórico ainda. Faz um quiz primeiro.")
        return

    data: list[dict] = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    print(f"\n{BOLD}Histórico — últimas {min(len(data), 15)} sessões{RESET}")
    print(f"{'─' * 56}")

    for r in data[-15:]:
        color = GREEN if r["percentage"] >= 78 else (YELLOW if r["percentage"] >= 60 else RED)
        date = r["date"][:10]
        domain = r["domain"][:24]
        print(f"  {date}  {domain:<26} {color}{r['correct']}/{r['total']} ({r['percentage']}%){RESET}")

    if data:
        avg = round(sum(r["percentage"] for r in data) / len(data))
        color = GREEN if avg >= 78 else (YELLOW if avg >= 60 else RED)
        total_q = sum(r["total"] for r in data)
        print(f"\n{BOLD}  Média geral: {color}{avg}%{RESET}   {DIM}({total_q} perguntas respondidas){RESET}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quiz dinâmico AD0-E724 — perguntas geradas pela Claude API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python3 quiz.py                    # 10 perguntas, todos os domínios\n"
            "  python3 quiz.py --domain 1         # só Arquitetura\n"
            "  python3 quiz.py --domain 2 --count 20\n"
            "  python3 quiz.py --stats            # ver histórico\n"
        ),
    )
    parser.add_argument(
        "--domain",
        type=int,
        choices=[0, 1, 2, 3],
        default=0,
        metavar="{0,1,2,3}",
        help="0=todos (padrão), 1=Arquitetura, 2=Customizações, 3=Cloud",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        metavar="N",
        help="Número de perguntas (padrão: 10)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar histórico de sessões anteriores",
    )
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(f"{RED}Erro: variável ANTHROPIC_API_KEY não definida.{RESET}")
        print(f"  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    if not STUDY_FILE.exists():
        print(f"{RED}Erro: ficheiro de estudo não encontrado: {STUDY_FILE}{RESET}")
        sys.exit(1)

    if not (2 <= args.count <= 50):
        print(f"{RED}Erro: --count deve ser entre 2 e 50.{RESET}")
        sys.exit(1)

    content = STUDY_FILE.read_text(encoding="utf-8")
    section = extract_domain(content, args.domain)
    domain_label = DOMAIN_LABELS[args.domain]

    print(f"{DIM}Gerando {args.count} perguntas · {domain_label}...{RESET}", end="", flush=True)

    client = anthropic.Anthropic(api_key=api_key)

    try:
        questions = generate_questions(section, args.count, client)
    except json.JSONDecodeError as e:
        print(f"\n{RED}Erro ao parsear resposta da API: {e}{RESET}")
        sys.exit(1)

    print(f" {GREEN}pronto!{RESET}")

    result = run_quiz(questions, domain_label)
    save_progress(result)


if __name__ == "__main__":
    main()
