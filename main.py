import argparse
from agents.research_agent import run_research
from config.settings import settings


def main():
    parser = argparse.ArgumentParser(description="auto-multi-agent: 블로그 자동 발행 멀티에이전트")
    parser.add_argument(
        "--repo",
        type=str,
        default=settings.target_repo_url,
        help="분석할 GitHub 레포지토리 URL",
    )
    parser.add_argument(
        "--phase",
        type=str,
        default="research",
        choices=["research"],
        help="실행할 phase (현재: research)",
    )
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  auto-multi-agent")
    print(f"  대상 레포: {args.repo}")
    print(f"{'='*60}\n")

    if args.phase == "research":
        print("[Phase 1] Research Agent 실행 중...\n")
        result = run_research(args.repo)
        print("\n" + "="*60)
        print("리서치 결과:")
        print("="*60)
        print(result)


if __name__ == "__main__":
    main()
