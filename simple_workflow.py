#!/usr/bin/env python3
"""
医学文献调研与报告生成系统 - 简化测试版

使用 PubMed 直接检索，不依赖 Tavily API
"""

from literature_search import PubMedSearcher
from reading_report_generator import ReadingReportGenerator
import os


def simple_workflow(topic: str):
    """
    简化工作流

    1. PubMed 检索 → 找到高频作者 (潜在大佬)
    2. 检索高分文献
    3. 生成阅读报告
    """
    print(f"\n{'='*60}")
    print(f"医学文献调研 (简化版): {topic}")
    print(f"{'='*60}")

    searcher = PubMedSearcher()

    # Step 1: PubMed 检索
    print(f"\n[Step 1] PubMed 检索...")
    papers = searcher.search(topic, max_results=30)
    print(f"  检索到 {len(papers)} 篇")

    # Step 2: 提取高频作者
    print(f"\n[Step 2] 提取高频作者 (潜在大佬)...")
    from collections import Counter
    author_counts = Counter()
    for paper in papers:
        for author in paper.get('authors', []):
            author_counts[author] += 1

    top_authors = author_counts.most_common(10)
    print(f"  Top 10 作者:")
    for author, count in top_authors:
        print(f"    {author}: {count} 篇")

    # Step 3: 生成阅读报告
    print(f"\n[Step 3] 生成阅读报告...")
    generator = ReadingReportGenerator()
    report_file = generator.generate_report(topic, papers)
    print(f"  ✅ 报告已保存：{report_file}")

    print(f"\n{'='*60}")
    print(f"完成!")
    print(f"{'='*60}")

    return {
        'papers': papers,
        'top_authors': top_authors,
        'report_file': report_file,
    }


if __name__ == '__main__':
    result = simple_workflow("repetitive transcranial magnetic stimulation depression")
    print(f"\n输出位置:")
    print(f"  阅读报告：{result['report_file']}")
