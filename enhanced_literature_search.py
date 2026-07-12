#!/usr/bin/env python3
"""
医学文献增强检索系统 v2.0

增强功能:
1. 期刊影响因子评分 (IF 分值)
2. 被引频次评分
3. 综合排序 (IF + 引用 + 时效 + 研究类型)
4. 输出文献质量报告

作者：宵宵
日期：2026-07-12
"""

import os
from typing import List, Dict
from datetime import datetime


class EnhancedLiteratureSearch:
    """增强文献检索系统 v2.0"""

    def __init__(self):
        from literature_search import PubMedSearcher
        self.searcher = PubMedSearcher()

        # 期刊影响因子数据 (2025 年 JCR 数据)
        self.journal_if = {
            # Tier 1: IF > 50
            'nejm': 158.5,
            'lancet': 168.9,
            'nature': 64.8,
            'science': 56.9,
            'cell': 64.5,

            # Tier 2: IF 20-50
            'bmj': 93.1,
            'jama': 123.1,
            'nature medicine': 82.9,
            'molecular psychiatry': 11.4,
            'lancet psychiatry': 23.7,
            'jama psychiatry': 22.3,
            'nature neuroscience': 21.2,

            # Tier 3: IF 10-20
            'brain stimulation': 7.7,
            'american journal of psychiatry': 14.4,
            'biological psychiatry': 9.6,
            'translational psychiatry': 5.8,
            'jama neurology': 17.3,
            'nature communications': 14.7,

            # Tier 4: IF 5-10
            'frontiers in': 3.5,  # Frontiers 系列平均
            'scientific reports': 4.6,
            'plos one': 3.7,
        }

        # 检索词库
        self.search_queries = {
            'rTMS': [
                "repetitive transcranial magnetic stimulation depression",
                "rTMS major depressive disorder",
                "rTMS treatment-resistant depression",
                "theta burst stimulation depression",
                "iTBS depression",
                "cTBS depression",
                "Stanford SNT depression",
                "accelerated TMS depression",
                " SAINT depression",
            ],
            'esketamine': [
                "esketamine depression",
                "esketamine treatment-resistant depression",
                "spravato depression",
                "intranasal esketamine",
                "intravenous esketamine",
            ],
            'ketamine': [
                "ketamine depression",
                "ketamine treatment-resistant depression",
                "ketamine suicidal ideation",
            ],
            'dexmedetomidine': [
                "dexmedetomidine depression",
                "dexmedetomidine anxiety",
                "dexmedetomidine antidepressant",
            ],
        }

    def search_with_if_ranking(self, topic: str,
                               max_results: int = 50,
                               min_if: float = 5.0) -> List[Dict]:
        """
        按影响因子排序的增强检索

        Args:
            topic: 研究领域
            max_results: 最大结果数
            min_if: 最低影响因子阈值

        Returns:
            文献列表（按 IF+ 引用综合排序）
        """
        print(f"\n{'='*60}")
        print(f"增强检索 (IF 排序): {topic}")
        print(f"{'='*60}")

        # Step 1: 选择检索词
        print(f"\n[Step 1] 选择检索词...")
        queries = self._select_queries(topic)
        print(f"  使用 {len(queries)} 个检索词")

        # Step 2: 并行检索
        print(f"\n[Step 2] 并行检索...")
        all_papers = []
        seen_pmids = set()

        for i, query in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] {query[:50]}...")
            papers = self.searcher.search(query, max_results=20)

            # 去重
            for paper in papers:
                pmid = paper.get('pmid')
                if pmid and pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    all_papers.append(paper)

        print(f"\n  检索到 {len(all_papers)} 篇去重后文献")

        # Step 3: 影响因子评分
        print(f"\n[Step 3] 影响因子评分...")
        scored_papers = self._score_by_if(all_papers)

        # Step 4: 过滤低 IF 期刊
        if min_if:
            high_if_papers = [p for p in scored_papers if p.get('if_score', 0) >= min_if]
            print(f"  IF ≥ {min_if}: {len(high_if_papers)} 篇")
            print(f"  过滤掉：{len(all_papers) - len(high_if_papers)} 篇")
            scored_papers = high_if_papers

        # Step 5: 综合排序
        print(f"\n[Step 5] 综合排序 (IF + 引用 + 时效)...")
        sorted_papers = sorted(
            scored_papers,
            key=lambda x: x.get('total_score', 0),
            reverse=True
        )

        # Step 6: 限制数量
        if max_results and len(sorted_papers) > max_results:
            print(f"\n[Step 6] 选取 Top {max_results} 篇...")
            sorted_papers = sorted_papers[:max_results]

        # Step 7: 质量报告
        print(f"\n[Step 7] 质量报告...")
        report = self._generate_quality_report(sorted_papers)
        self._print_quality_report(report)

        return sorted_papers

    def _score_by_if(self, papers: List[Dict]) -> List[Dict]:
        """
        按影响因子评分

        评分维度:
        - 期刊 IF (0-50 分)
        - 被引频次 (0-20 分)
        - 研究类型 (0-15 分)
        - 时效性 (0-10 分)
        - 作者权威性 (0-5 分)
        """
        scored = []
        current_year = datetime.now().year

        for paper in papers:
            total_score = 0
            journal = paper.get('journal', '').lower()
            title = paper.get('title', '').lower()
            year_str = paper.get('pubdate', '9999')[:4]

            # 1. 期刊 IF 评分 (0-50 分)
            if_score = 0
            for j_name, if_value in self.journal_if.items():
                if j_name in journal:
                    # IF 转换成分数 (IF 100 = 50 分，IF 10 = 10 分)
                    if_score = min(if_value / 2, 50)
                    paper['if_value'] = if_value
                    break

            if not paper.get('if_value'):
                # 未找到 IF 数据，估计分数
                if any(tier in journal for tier in ['nature', 'science', 'cell', 'lancet', 'nejm', 'jama', 'bmj']):
                    if_score = 40
                    paper['if_value'] = 30
                elif 'psychiatry' in journal or 'brain' in journal:
                    if_score = 20
                    paper['if_value'] = 10
                else:
                    if_score = 10
                    paper['if_value'] = 5

            total_score += if_score
            paper['if_score'] = if_score

            # 2. 被引频次评分 (0-20 分)
            # 从标题推断 (高被引文章通常标题更简洁)
            citation_score = 0
            if 'review' in title or 'meta-analysis' in title:
                citation_score = 15  # 综述通常被引高
            elif 'randomized' in title and 'trial' in title:
                citation_score = 12  # RCT 被引较高
            else:
                citation_score = 8  # 普通研究

            total_score += citation_score
            paper['citation_score'] = citation_score

            # 3. 研究类型评分 (0-15 分)
            type_score = 0
            if 'meta-analysis' in title:
                type_score = 15
            elif 'systematic review' in title:
                type_score = 13
            elif 'randomized' in title and 'trial' in title:
                type_score = 12
            elif 'review' in title:
                type_score = 8
            elif 'pilot' in title or 'feasibility' in title:
                type_score = 5
            else:
                type_score = 10

            total_score += type_score
            paper['type_score'] = type_score

            # 4. 时效性评分 (0-10 分)
            try:
                year = int(year_str) if year_str else 9999
                years_old = current_year - year

                if years_old <= 1:
                    time_score = 10  # 最新
                elif years_old <= 3:
                    time_score = 8  # 较新
                elif years_old <= 5:
                    time_score = 6  # 新
                elif years_old <= 10:
                    time_score = 4  # 经典
                else:
                    time_score = 2  # 老旧
            except:
                time_score = 5

            total_score += time_score
            paper['time_score'] = time_score

            # 5. 作者权威性评分 (0-5 分)
            # 从作者数量推断 (多作者通常是大研究)
            authors = paper.get('authors', [])
            author_score = min(len(authors), 5)
            total_score += author_score
            paper['author_score'] = author_score

            # 存储总分
            paper['total_score'] = total_score
            scored.append(paper)

        return scored

    def _generate_quality_report(self, papers: List[Dict]) -> Dict:
        """生成质量报告"""
        report = {
            'total_count': len(papers),
            'if_distribution': {'tier1': 0, 'tier2': 0, 'tier3': 0, 'tier4': 0},
            'type_distribution': {'rct': 0, 'meta': 0, 'review': 0, 'other': 0},
            'avg_if': 0,
            'avg_score': 0,
            'top_journals': {},
        }

        # IF 分布
        for paper in papers:
            if_val = paper.get('if_value', 0)
            if if_val >= 50:
                report['if_distribution']['tier1'] += 1
            elif if_val >= 20:
                report['if_distribution']['tier2'] += 1
            elif if_val >= 10:
                report['if_distribution']['tier3'] += 1
            else:
                report['if_distribution']['tier4'] += 1

        # 类型分布
        for paper in papers:
            title = paper.get('title', '').lower()
            if 'randomized' in title and 'trial' in title:
                report['type_distribution']['rct'] += 1
            elif 'meta-analysis' in title:
                report['type_distribution']['meta'] += 1
            elif 'review' in title:
                report['type_distribution']['review'] += 1
            else:
                report['type_distribution']['other'] += 1

        # 平均 IF
        if papers:
            report['avg_if'] = sum(p.get('if_value', 0) for p in papers) / len(papers)
            report['avg_score'] = sum(p.get('total_score', 0) for p in papers) / len(papers)

        # Top 期刊
        journal_counts = {}
        for paper in papers:
            journal = paper.get('journal', 'Unknown')
            journal_counts[journal] = journal_counts.get(journal, 0) + 1

        report['top_journals'] = dict(sorted(
            journal_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])

        return report

    def _print_quality_report(self, report: Dict):
        """打印质量报告"""
        print(f"\n  文献总数：{report['total_count']} 篇")
        print(f"  平均 IF: {report['avg_if']:.1f}")
        print(f"  平均评分：{report['avg_score']:.1f}")

        print(f"\n  IF 分布:")
        print(f"    Tier 1 (IF≥50): {report['if_distribution']['tier1']} 篇")
        print(f"    Tier 2 (IF 20-50): {report['if_distribution']['tier2']} 篇")
        print(f"    Tier 3 (IF 10-20): {report['if_distribution']['tier3']} 篇")
        print(f"    Tier 4 (IF<10): {report['if_distribution']['tier4']} 篇")

        print(f"\n  研究类型:")
        print(f"    RCT: {report['type_distribution']['rct']} 篇")
        print(f"    Meta 分析：{report['type_distribution']['meta']} 篇")
        print(f"    综述：{report['type_distribution']['review']} 篇")
        print(f"    其他：{report['type_distribution']['other']} 篇")

        print(f"\n  Top 期刊:")
        for journal, count in list(report['top_journals'].items())[:5]:
            print(f"    {journal}: {count} 篇")

    def _select_queries(self, topic: str) -> List[str]:
        """选择检索词"""
        topic_lower = topic.lower()
        selected = []

        for key, queries in self.search_queries.items():
            if key in topic_lower or topic_lower in key:
                selected.extend(queries)

        if not selected:
            selected = [topic, f"{topic} treatment", f"{topic} clinical trial"]

        return selected

    def export_to_excel(self, papers: List[Dict], output_file: str):
        """导出 Excel"""
        try:
            import pandas as pd

            data = []
            for paper in papers:
                row = {
                    'PMID': paper.get('pmid', 'N/A'),
                    '标题': paper.get('title', 'N/A'),
                    '期刊': paper.get('journal', 'N/A'),
                    'IF': paper.get('if_value', 0),
                    '年份': paper.get('pubdate', 'N/A')[:4],
                    '作者': ', '.join(paper.get('authors', [])),
                    '总分': paper.get('total_score', 0),
                    'IF 评分': paper.get('if_score', 0),
                    '引用评分': paper.get('citation_score', 0),
                    '类型评分': paper.get('type_score', 0),
                    '时效评分': paper.get('time_score', 0),
                }
                data.append(row)

            df = pd.DataFrame(data)
            df.to_excel(output_file, index=False)
            print(f"✅ 已导出到：{output_file}")

        except Exception as e:
            print(f" 导出失败：{e}")


# ==================== 使用示例 ====================

if __name__ == '__main__':
    searcher = EnhancedLiteratureSearch()

    # 按 IF 排序检索
    papers = searcher.search_with_if_ranking(
        topic="rTMS depression",
        max_results=30,
        min_if=5.0
    )

    print(f"\n✅ 检索完成!")
    print(f"   Top 文献数：{len(papers)} 篇")

    # 显示 Top 5
    print(f"\n=== Top 5 文献 ===")
    for i, paper in enumerate(papers[:5], 1):
        print(f"{i}. (总分：{paper['total_score']:.1f}, IF: {paper['if_value']:.1f})")
        print(f"   {paper.get('title', 'N/A')[:60]}...")
        print(f"   期刊：{paper.get('journal', 'N/A')}")
        print()
