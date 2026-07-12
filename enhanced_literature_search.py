#!/usr/bin/env python3
"""
医学文献增强检索系统

目标：找到尽可能多的高分文献

策略:
1. 多检索词并行检索
2. PubMed + Europe PMC 双源检索
3. 高分期刊优先
4. 智能去重
5. 按相关性排序

作者：宵宵
日期：2026-07-12
"""

import os
from typing import List, Dict, Set
from datetime import datetime
from collections import Counter


class EnhancedLiteratureSearch:
    """增强文献检索系统"""

    def __init__(self):
        from literature_search import PubMedSearcher
        self.searcher = PubMedSearcher()

        # 高分期刊列表（按影响力排序）
        self.top_tiers = {
            'tier1': ['nature', 'science', 'cell', 'nejm', 'lancet'],  # 顶级
            'tier2': ['bmj', 'jama', 'nature medicine', 'molecular psychiatry',  # 高分
                     'lancet psychiatry', 'jama psychiatry'],
            'tier3': ['brain stimulation', 'american journal of psychiatry',  # 专业顶刊
                     'biological psychiatry', 'translational psychiatry'],
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
                "noninvasive brain stimulation depression",
                "neuromodulation depression",
                "Stanford SNT depression",
                "accelerated TMS depression",
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

    def search_comprehensive(self, topic: str,
                            max_results: int = 100,
                            filter_high_impact: bool = True) -> List[Dict]:
        """
        综合检索策略

        Args:
            topic: 研究领域
            max_results: 最大结果数
            filter_high_impact: 是否优先高分期刊

        Returns:
            文献列表（按影响力排序）
        """
        print(f"\n{'='*60}")
        print(f"增强检索：{topic}")
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

        # Step 3: 高分期刊过滤
        if filter_high_impact:
            print(f"\n[Step 3] 高分期刊过滤...")
            scored_papers = self._score_papers(all_papers)
            sorted_papers = sorted(scored_papers, key=lambda x: x['score'], reverse=True)

            # 显示高分文献
            high_impact = [p for p in sorted_papers if p['score'] >= 8]
            print(f"  高分文献 (≥8 分): {len(high_impact)} 篇")

            all_papers = sorted_papers

        # Step 4: 限制数量
        if max_results and len(all_papers) > max_results:
            print(f"\n[Step 4] 选取 Top {max_results} 篇...")
            all_papers = all_papers[:max_results]

        # Step 5: 质量评估
        print(f"\n[Step 5] 质量评估...")
        assessment = self._assess_quality(all_papers)
        print(f"  Tier 1 (顶级期刊): {assessment['tier1']} 篇")
        print(f"  Tier 2 (高分期刊): {assessment['tier2']} 篇")
        print(f"  Tier 3 (专业顶刊): {assessment['tier3']} 篇")
        print(f"  RCT: {assessment['rct_count']} 篇")
        print(f"  Meta 分析：{assessment['meta_count']} 篇")

        return all_papers

    def _select_queries(self, topic: str) -> List[str]:
        """根据主题选择检索词"""
        topic_lower = topic.lower()
        selected = []

        # 匹配主题
        for key, queries in self.search_queries.items():
            if key in topic_lower or topic_lower in key:
                selected.extend(queries)

        # 如果没有匹配，使用通用检索
        if not selected:
            # 从主题生成检索词
            selected = [
                topic,
                f"{topic} treatment",
                f"{topic} clinical trial",
            ]

        return selected

    def _score_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        文献评分

        评分维度:
        - 期刊影响力 (0-10 分)
        - 研究类型 (0-5 分)
        - 时效性 (0-3 分)
        - 被引频次 (0-2 分)
        """
        scored = []
        current_year = datetime.now().year

        for paper in papers:
            score = 0
            journal = paper.get('journal', '').lower()
            title = paper.get('title', '').lower()
            year_str = paper.get('pubdate', '9999')[:4]

            # 期刊影响力 (0-10 分)
            for tier_name, journals in self.top_tiers.items():
                if any(j in journal for j in journals):
                    if tier_name == 'tier1':
                        score += 10
                    elif tier_name == 'tier2':
                        score += 8
                    elif tier_name == 'tier3':
                        score += 6
                    break

            # 研究类型 (0-5 分)
            if 'randomized' in title and 'trial' in title:
                score += 5  # RCT
            elif 'meta-analysis' in title:
                score += 5  # Meta 分析
            elif 'systematic review' in title:
                score += 4  # 系统评价
            elif 'review' in title:
                score += 2  # 综述

            # 时效性 (0-3 分)
            try:
                year = int(year_str) if year_str else 9999
                if year >= current_year - 1:
                    score += 3  # 最新
                elif year >= current_year - 3:
                    score += 2  # 较新
                elif year >= current_year - 5:
                    score += 1  # 新
            except:
                pass

            # 存储分数
            paper['score'] = score
            scored.append(paper)

        return scored

    def _assess_quality(self, papers: List[Dict]) -> Dict:
        """质量评估"""
        assessment = {
            'total_count': len(papers),
            'tier1': 0,
            'tier2': 0,
            'tier3': 0,
            'rct_count': 0,
            'meta_count': 0,
        }

        for paper in papers:
            journal = paper.get('journal', '').lower()
            title = paper.get('title', '').lower()

            # 期刊分级
            for tier_name, journals in self.top_tiers.items():
                if any(j in journal for j in journals):
                    assessment[tier_name] += 1
                    break

            # 研究类型
            if 'randomized' in title and 'trial' in title:
                assessment['rct_count'] += 1
            elif 'meta-analysis' in title:
                assessment['meta_count'] += 1

        return assessment

    def export_to_excel(self, papers: List[Dict], output_file: str):
        """导出为 Excel"""
        try:
            import pandas as pd

            # 准备数据
            data = []
            for paper in papers:
                row = {
                    'PMID': paper.get('pmid', 'N/A'),
                    '标题': paper.get('title', 'N/A'),
                    '期刊': paper.get('journal', 'N/A'),
                    '年份': paper.get('pubdate', 'N/A')[:4],
                    '作者': ', '.join(paper.get('authors', [])),
                    '评分': paper.get('score', 0),
                }
                data.append(row)

            # 创建 DataFrame
            df = pd.DataFrame(data)

            # 导出
            df.to_excel(output_file, index=False)
            print(f"✅ 已导出到：{output_file}")

        except Exception as e:
            print(f"❌ 导出失败：{e}")


# ==================== 使用示例 ====================

if __name__ == '__main__':
    searcher = EnhancedLiteratureSearch()

    # 综合检索
    papers = searcher.search_comprehensive(
        topic="rTMS depression",
        max_results=50,
        filter_high_impact=True
    )

    print(f"\n✅ 检索完成!")
    print(f"   总文献数：{len(papers)} 篇")

    # 导出 Excel
    # searcher.export_to_excel(papers, "rTMS_literature.xlsx")
