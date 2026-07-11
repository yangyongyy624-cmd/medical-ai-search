#!/usr/bin/env python3
"""
艾司氯胺酮快速抗抑郁文献检索示例

使用方法:
    python examples/esketamine_example.py
"""

from search_optimizer import OptimizedLiteratureSearcher


def main():
    # 创建检索器
    searcher = OptimizedLiteratureSearcher()

    print("=" * 60)
    print("艾司氯胺酮快速抗抑郁文献检索")
    print("=" * 60)
    print()

    # 执行检索 (支持中文)
    result = searcher.search_comprehensive(
        "esketamine rapid antidepressant",
        use_translation=True,
        use_mesh=True,
        use_synonyms=True,
        citation_iterations=2,  # 二次检索
        max_results=30
    )

    print()
    print(f"检索完成：{result['total_count']} 篇")
    print()

    # 显示前 10 篇
    print("前 10 篇文献:")
    print()
    for i, paper in enumerate(result['merged'][:10], 1):
        title = paper.get('title', 'N/A')[:60]
        pmid = paper.get('pmid', 'N/A')
        year = paper.get('pubdate', 'N/A')[:4] if paper.get('pubdate') else 'N/A'

        # 标记经典文献
        tags = []
        if paper.get('is_classic'):
            tags.append('⭐经典')
        if paper.get('iteration', 0) > 0:
            tags.append(f"第{paper['iteration']}次检索")

        tag_str = ' | '.join(tags) if tags else ''

        print(f"{i}. {title}...")
        print(f"   PMID: {pmid} | 年份：{year} {tag_str}")
        print()


if __name__ == '__main__':
    main()
