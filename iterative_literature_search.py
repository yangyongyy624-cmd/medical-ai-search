#!/usr/bin/env python3
"""
医学文献迭代检索系统 v3.1

实用迭代策略:
1. 第 1 次检索 - 主题检索 (精确检索词)
2. 第 2 次检索 - 扩展检索 (宽泛检索词 + 相关主题)
3. 第 3 次检索 - 经典作者/实验室检索
4. 第 4 次检索 - 高分期刊 + 早期文献检索

作者：宵宵
日期：2026-07-12
"""

import os
from typing import List, Dict
from datetime import datetime


class IterativeLiteratureSearch:
    """迭代文献检索系统 v3.1"""

    def __init__(self):
        from literature_search import PubMedSearcher
        self.searcher = PubMedSearcher()

        # 期刊影响因子数据
        self.journal_if = {
            'nejm': 158.5, 'lancet': 168.9, 'nature': 64.8,
            'science': 56.9, 'cell': 64.5, 'bmj': 93.1,
            'jama': 123.1, 'nature medicine': 82.9,
            'molecular psychiatry': 11.4, 'lancet psychiatry': 23.7,
            'jama psychiatry': 22.3, 'brain stimulation': 7.7,
            'american journal of psychiatry': 14.4,
        }

        # 检索词库 (按迭代轮次组织)
        self.search_queries = {
            'rTMS': {
                'iter1': [  # 第 1 次：精确检索
                    "repetitive transcranial magnetic stimulation depression",
                    "rTMS major depressive disorder",
                ],
                'iter2': [  # 第 2 次：扩展检索
                    "theta burst stimulation depression",
                    "iTBS depression",
                    "cTBS depression",
                    "noninvasive brain stimulation depression",
                ],
                'iter3': [  # 第 3 次：经典作者/实验室
                    "Stanford SNT depression",
                    "George MS transcranial magnetic",
                    "Lisanby SH brain stimulation",
                ],
                'iter4': [  # 第 4 次：高分期刊 + 经典
                    "transcranial magnetic stimulation treatment-resistant depression",
                    "accelerated TMS depression",
                ],
            },
            'esketamine': {
                'iter1': ["esketamine depression", "esketamine treatment-resistant depression"],
                'iter2': ["intranasal esketamine", "spravato depression"],
                'iter3': ["Zarate CA depression", "intravenous ketamine depression"],
                'iter4': ["ketamine suicidal ideation", "rapid acting antidepressant"],
            },
        }

        # 经典作者列表
        self.classic_authors = {
            'rTMS': ['George MS', 'Lisanby SH', 'Pascual-Leone A', 'Bikson M'],
            'esketamine': ['Zarate CA', 'Daly EJ', 'Singh JB', 'Sanacora G'],
        }

    def search_iterative(self, topic: str,
                        max_iterations: int = 4,
                        max_results: int = 50) -> List[Dict]:
        """
        迭代检索流程 (实用版)

        Args:
            topic: 研究领域
            max_iterations: 最大迭代次数
            max_results: 最大结果数

        Returns:
            文献列表（按迭代轮次标记）
        """
        print(f"\n{'='*60}")
        print(f"迭代检索：{topic}")
        print(f"最大迭代次数：{max_iterations}")
        print(f"{'='*60}")

        all_papers = []
        seen_pmids = set()
        topic_lower = topic.lower()

        # ========== 确定使用哪个检索词库 ==========
        query_set = None
        for key in self.search_queries.keys():
            if key in topic_lower:
                query_set = self.search_queries[key]
                break

        if not query_set:
            # 如果没有匹配，使用通用检索
            query_set = {
                'iter1': [topic],
                'iter2': [f"{topic} treatment"],
                'iter3': [f"{topic} clinical trial"],
                'iter4': [f"{topic} randomized trial"],
            }

        # ========== 第 1 次检索：主题检索 ==========
        if max_iterations >= 1:
            print(f"\n【第 1 次检索】主题检索 (精确)...")
            papers = self._search_queries(query_set['iter1'])
            new_count = self._add_papers(papers, all_papers, seen_pmids, iteration=1, source='主题检索')
            print(f"  新增：{new_count} 篇 | 累计：{len(all_papers)} 篇")

        # ========== 第 2 次检索：扩展检索 ==========
        if max_iterations >= 2:
            print(f"\n【第 2 次检索】扩展检索 (宽泛)...")
            papers = self._search_queries(query_set['iter2'])
            new_count = self._add_papers(papers, all_papers, seen_pmids, iteration=2, source='扩展检索')
            print(f"  新增：{new_count} 篇 | 累计：{len(all_papers)} 篇")

        # ========== 第 3 次检索：经典作者/实验室 ==========
        if max_iterations >= 3:
            print(f"\n【第 3 次检索】经典作者/实验室检索...")
            papers = self._search_queries(query_set['iter3'])
            new_count = self._add_papers(papers, all_papers, seen_pmids, iteration=3, source='经典作者')
            print(f"  新增：{new_count} 篇 | 累计：{len(all_papers)} 篇")

        # ========== 第 4 次检索：高分期刊 + 经典 ==========
        if max_iterations >= 4:
            print(f"\n【第 4 次检索】高分期刊 + 经典文献检索...")
            papers = self._search_queries(query_set['iter4'])
            new_count = self._add_papers(papers, all_papers, seen_pmids, iteration=4, source='经典文献')
            print(f"  新增：{new_count} 篇 | 累计：{len(all_papers)} 篇")

        # ========== 质量评估和排序 ==========
        print(f"\n【质量评估】按 IF+ 引用排序...")
        scored_papers = self._score_and_rank(all_papers)
        sorted_papers = sorted(scored_papers, key=lambda x: x.get('total_score', 0), reverse=True)

        # ========== 限制数量 ==========
        if max_results and len(sorted_papers) > max_results:
            sorted_papers = sorted_papers[:max_results]

        # ========== 生成报告 ==========
        print(f"\n【迭代检索报告】")
        report = self._generate_iterative_report(sorted_papers)
        self._print_iterative_report(report)

        return sorted_papers

    def _search_queries(self, queries: List[str]) -> List[Dict]:
        """执行多个检索词"""
        papers = []
        seen_pmids = set()

        for query in queries:
            search_papers = self.searcher.search(query, max_results=20)
            for paper in search_papers:
                pmid = paper.get('pmid')
                if pmid and pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    papers.append(paper)

        return papers

    def _add_papers(self, papers: List[Dict], all_papers: List[Dict],
                   seen_pmids: Set[str], iteration: int, source: str) -> int:
        """添加论文到列表"""
        new_count = 0
        for paper in papers:
            pmid = paper.get('pmid')
            if pmid and pmid not in seen_pmids:
                seen_pmids.add(pmid)
                paper['iteration'] = iteration
                paper['source'] = source
                all_papers.append(paper)
                new_count += 1
        return new_count

    def _score_and_rank(self, papers: List[Dict]) -> List[Dict]:
        """评分和排序"""
        scored = []
        current_year = datetime.now().year

        for paper in papers:
            score = 0
            journal = paper.get('journal', '').lower()
            year_str = paper.get('pubdate', '9999')[:4]

            # 1. IF 评分 (0-50 分)
            if_score = 0
            for j_name, if_value in self.journal_if.items():
                if j_name in journal:
                    if_score = min(if_value / 2, 50)
                    paper['if_value'] = if_value
                    break

            if not paper.get('if_value'):
                if any(tier in journal for tier in ['nature', 'science', 'cell', 'lancet', 'nejm', 'jama', 'bmj']):
                    if_score = 40
                    paper['if_value'] = 30
                elif 'psychiatry' in journal or 'brain' in journal:
                    if_score = 20
                    paper['if_value'] = 10
                else:
                    if_score = 10
                    paper['if_value'] = 5

            score += if_score

            # 2. 研究类型评分 (0-20 分)
            title = paper.get('title', '').lower()
            if 'meta-analysis' in title:
                score += 20
            elif 'randomized' in title and 'trial' in title:
                score += 18
            elif 'systematic review' in title:
                score += 15
            elif 'review' in title:
                score += 10
            else:
                score += 8

            # 3. 时效性评分 (0-10 分)
            try:
                year = int(year_str) if year_str else 9999
                years_old = current_year - year
                if years_old <= 1:
                    score += 10
                elif years_old <= 3:
                    score += 8
                elif years_old <= 5:
                    score += 6
                elif years_old <= 10:
                    score += 4  # 经典文献加分
                else:
                    score += 2
            except:
                pass

            # 4. 迭代轮次加分 (早期检索的加分)
            iteration = paper.get('iteration', 1)
            if iteration == 1:
                score += 5  # 第 1 次检索的通常是核心文献
            elif iteration >= 3:
                score += 8  # 第 3-4 次检索的可能是经典文献

            paper['total_score'] = score
            scored.append(paper)

        return scored

    def _generate_iterative_report(self, papers: List[Dict]) -> Dict:
        """生成迭代检索报告"""
        report = {
            'total_count': len(papers),
            'by_iteration': {1: 0, 2: 0, 3: 0, 4: 0},
            'by_source': {},
            'high_if_count': 0,
            'rct_count': 0,
            'meta_count': 0,
        }

        for paper in papers:
            iteration = paper.get('iteration', 1)
            source = paper.get('source', '未知')

            report['by_iteration'][iteration] = report['by_iteration'].get(iteration, 0) + 1
            report['by_source'][source] = report['by_source'].get(source, 0) + 1

            if paper.get('if_value', 0) >= 50:
                report['high_if_count'] += 1

            title = paper.get('title', '').lower()
            if 'randomized' in title and 'trial' in title:
                report['rct_count'] += 1
            elif 'meta-analysis' in title:
                report['meta_count'] += 1

        return report

    def _print_iterative_report(self, report: Dict):
        """打印迭代检索报告"""
        print(f"\n  文献总数：{report['total_count']} 篇")
        print(f"\n  按迭代轮次:")
        for i in range(1, 5):
            count = report['by_iteration'].get(i, 0)
            if count > 0:
                source_name = {1: '主题检索', 2: '扩展检索', 3: '经典作者', 4: '经典文献'}.get(i, f'第{i}次')
                print(f"    第{i}次 ({source_name}): {count} 篇")

        print(f"\n  按来源:")
        for source, count in report['by_source'].items():
            print(f"    {source}: {count} 篇")

        print(f"\n  高质量文献:")
        print(f"    IF≥50 (顶级期刊): {report['high_if_count']} 篇")
        print(f"    RCT: {report['rct_count']} 篇")
        print(f"    Meta 分析：{report['meta_count']} 篇")


# ==================== 使用示例 ====================

if __name__ == '__main__':
    searcher = IterativeLiteratureSearch()

    # 迭代检索
    papers = searcher.search_iterative(
        topic="rTMS depression",
        max_iterations=4,
        max_results=30
    )

    print(f"\n✅ 迭代检索完成!")
    print(f"   总文献数：{len(papers)} 篇")

    # 显示 Top 文献
    print(f"\n=== Top 10 文献 ===")
    for i, paper in enumerate(papers[:10], 1):
        print(f"{i}. (第{paper['iteration']}次检索，IF: {paper['if_value']:.1f}, 总分：{paper['total_score']:.1f})")
        title = paper.get('title', 'N/A')[:60]
        journal = paper.get('journal', 'N/A')[:30]
        year = paper.get('pubdate', 'N/A')[:4]
        print(f"   {title}...")
        print(f"   期刊：{journal} ({year})")
        print()
