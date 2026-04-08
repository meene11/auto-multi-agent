import argparse
from config.settings import settings


def main():
    parser = argparse.ArgumentParser(description="auto-multi-agent: 블로그 자동 발행 멀티에이전트")
    parser.add_argument(
        "--repo",
        type=str,
        default=settings.target_repo_url,
        help="분석할 GitHub 레포지토리 URL",
    )
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  auto-multi-agent")
    print(f"  대상 레포: {args.repo}")
    print(f"{'='*60}\n")

    from orchestrator.workflow import run_pipeline
    final_state = run_pipeline(args.repo)

    print(f"\n{'='*60}")
    print("  파이프라인 완료!")
    print(f"{'='*60}")
    print(f"  제목      : {final_state['title']}")
    print(f"  SEO 점수  : {final_state['seo_score']}점")
    print(f"  태그      : {final_state['tags']}")
    print(f"  dev.to    : {final_state['published_urls'].get('devto', '-')}")
    print(f"  Hashnode  : {final_state['published_urls'].get('hashnode', '-')}")


if __name__ == "__main__":
    main()
