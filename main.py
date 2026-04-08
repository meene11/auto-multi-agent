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
    parser.add_argument(
        "--phase",
        type=str,
        default="all",
        choices=["research", "write", "seo", "publish", "all"],
        help="실행할 phase (기본값: all — 전체 파이프라인)",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="특정 phase 단독 실행 시 입력값 (파일 경로 또는 텍스트)",
    )
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  auto-multi-agent")
    print(f"  대상 레포: {args.repo}")
    print(f"  실행 phase: {args.phase}")
    print(f"{'='*60}\n")

    # Research
    if args.phase in ("research", "all"):
        from agents.research_agent import run_research
        print("[Phase 1] Research Agent 실행 중...\n")
        research_result = run_research(args.repo)
        print("\n[Research 결과]")
        print(research_result)

        if args.phase == "research":
            return

    # Write
    if args.phase in ("write", "all"):
        from agents.writer_agent import run_writer
        print("\n[Phase 2] Writer Agent 실행 중...\n")
        input_data = args.input if args.phase == "write" else research_result
        draft = run_writer(input_data)
        print("\n[초안]")
        print(draft[:500] + "..." if len(draft) > 500 else draft)

        if args.phase == "write":
            return

    # SEO
    if args.phase in ("seo", "all"):
        from agents.seo_agent import run_seo
        print("\n[Phase 3] SEO Agent 실행 중...\n")
        input_data = args.input if args.phase == "seo" else draft
        seo_result = run_seo(input_data)
        print(f"\n[SEO 결과] 점수: {seo_result['seo_score']}점")
        print(f"제목: {seo_result['title']}")
        print(f"태그: {seo_result['tags']}")
        if seo_result["issues"]:
            print(f"개선 사항: {seo_result['issues']}")

        # SEO 점수 미달 시 재작성
        if seo_result["seo_score"] < settings.seo_score_threshold:
            print(f"\nSEO 점수 {seo_result['seo_score']}점 — 기준({settings.seo_score_threshold}점) 미달, 재작성 중...")
            from agents.writer_agent import run_writer
            draft = run_writer(research_result + "\n\n개선 필요 사항:\n" + "\n".join(seo_result["issues"]))
            seo_result = run_seo(draft)
            print(f"재작성 후 SEO 점수: {seo_result['seo_score']}점")

        if args.phase == "seo":
            return

    # Publish
    if args.phase in ("publish", "all"):
        from agents.publisher_agent import run_publisher
        print("\n[Phase 4] Publisher Agent 실행 중...\n")
        publish_result = run_publisher(
            title=seo_result["title"],
            content=seo_result["optimized_content"],
            tags=seo_result["tags"],
        )
        print("\n" + "="*60)
        print("발행 완료!")
        print("="*60)
        print(f"dev.to   : {publish_result['devto']}")
        print(f"Hashnode : {publish_result['hashnode']}")


if __name__ == "__main__":
    main()
