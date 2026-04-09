from config.settings import settings


def main():
    print(f"\n{'='*60}")
    print(f"  auto-multi-agent - IT 뉴스 자동 블로그 발행")
    print(f"  Supabase: {settings.supabase_url}")
    print(f"  테이블  : {settings.supabase_table}")
    print(f"  기사 수 : {settings.articles_per_run}개")
    print(f"{'='*60}\n")

    from orchestrator.workflow import run_pipeline
    final_state = run_pipeline()

    print(f"\n{'='*60}")
    print("  파이프라인 완료!")
    print(f"{'='*60}")
    print(f"  제목      : {final_state['title']}")
    print(f"  SEO 점수  : {final_state['seo_score']}점")
    print(f"  태그      : {final_state['tags']}")
    print(f"  dev.to    : {final_state['published_urls'].get('devto', '-')}")
    print(f"  Hashnode  : {final_state['published_urls'].get('hashnode', '-')}")
    print(f"  Naver     : {final_state['published_urls'].get('naver', '-')}")


if __name__ == "__main__":
    main()
