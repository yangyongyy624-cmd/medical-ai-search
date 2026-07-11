#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检索优化模块 - 让检索更全面
功能:
- 中文→英文自动翻译
- MeSH 词自动扩展
- 同义词扩展
- 布尔逻辑优化
"""

from typing import List, Dict, Set, Tuple


# ========== 医学词典 (中文→英文) ==========

MEDICAL_TRANSLATION = {
    # 药物名
    "右美托咪定": "dexmedetomidine",
    "艾司氯胺酮": "esketamine",
    "氯胺酮": "ketamine",
    "丙泊酚": "propofol",
    "咪达唑仑": "midazolam",
    "芬太尼": "fentanyl",
    "舒芬太尼": "sufentanil",
    "瑞芬太尼": "remifentanil",

    # 疾病/症状
    "抑郁": "depression",
    "抗抑郁": "antidepressant",
    "焦虑": "anxiety",
    "抗焦虑": "anxiolytic",
    "失眠": "insomnia",
    "睡眠": "sleep",
    "疼痛": "pain",
    "镇痛": "analgesia",
    "麻醉": "anesthesia",
    "镇静": "sedation",
    "谵妄": "delirium",
    "术后": "postoperative",
    "难治性": "refractory",
    "难治性抑郁": "treatment-resistant depression",

    # 研究类型
    "随机对照试验": "randomized controlled trial",
    "meta 分析": "meta-analysis",
    "系统评价": "systematic review",
    "综述": "review",
    "病例报告": "case report",
    "队列研究": "cohort study",
    "横断面研究": "cross-sectional study",
}

# 同义词扩展
SYNONYMS = {
    "dexmedetomidine": ["dexmedetomidine hydrochloride", "precedex", "dexdor"],
    "esketamine": ["s-ketamine", "esketamine hydrochloride", "spravato"],
    "ketamine": ["ketamine hydrochloride", "ketalar"],
    "depression": ["depressive disorder", "major depression", "MDD", "major depressive disorder"],
    "anxiety": ["anxiety disorder", "anxious", "generalized anxiety"],
    "insomnia": ["sleep disorder", "sleep disturbance", "sleep problems"],
    "sleep": ["sleep quality", "sleep architecture", "sleep stages"],
    "pain": ["pain management", "pain control", "analgesia"],
    "sedation": ["sedative", "conscious sedation", "deep sedation"],
    "delirium": ["icu delirium", "postoperative delirium", "acute confusion"],
    "anesthesia": ["anesthetic", "general anesthesia", "local anesthesia"],
    "postoperative": ["post-operative", "after surgery", "surgical"],
    "treatment-resistant": ["refractory", "drug-resistant", "intractable"],
}

# MeSH 术语映射
MESH_TERMS = {
    "dexmedetomidine": "D063110",
    "esketamine": "D007676",
    "ketamine": "D007676",
    "depression": "D003866",
    "depressive disorder": "D003866",
    "anxiety": "D001008",
    "anxiety disorders": "D001008",
    "sleep initiation and maintenance disorders": "D007022",
    "insomnia": "D007022",
    "pain": "D010146",
    "pain management": "D010146",
    "analgesia": "D000703",
    "anesthesia": "D000775",
    "sedation": "D012628",
    "conscious sedation": "D000776",
    "delirium": "D003696",
    "postoperative complications": "D011145",
}

# 经典/开创性文献 PMID 列表 (手动维护，防止漏检)
# 注意：PMID 32345093 在 PubMed 检索中可能指向错误文章，Cole et al. 2020 应通过标题检索
CLASSIC_PAPERS = {
    # 斯坦福 SNT/SAINT 核心文献
    # 注意：Cole et al. 2020 的 PMID 32345093 在 PubMed 检索中有问题，需要单独处理
    "SNT_2024_Williams_RCT": "41536095",  # Williams NR et al. World Psychiatry 2024 - RCT 验证
    "SNT_2024_Williams_durability": "40209894",  # Williams MD et al. Brain Stimul 2024 - 长期随访
    "SNT_2023_lee_predictor": "39468255",  # Lee SH et al. NPJ Ment Health Res 2023 - 预测因子
    "SNT_2024_Chen_bipolar": "39154984",  # Chen L et al. J Affect Disord 2024 - 双相抑郁
    "SNT_2024_Wang_connectivity": "38971869",  # Wang Y et al. NPJ Ment Health Res 2024 - 功能连接
    "SNT_2024_Zhang_pilot": "38447774",  # Zhang X et al. Brain Stimul 2024 - 双相抑郁试点

    # 艾司氯胺酮核心文献 (宁玉萍团队等)
    "ESK_Zhou_YAACAP_2023": "37414272",  # Zhou Y et al. JAACAP 2023 - 青少年 RCT
    "ESK_Amerio_eClinMed_2026": "41440469",  # Amerio et al. eClinicalMedicine 2026 - 综述
}

# Cole et al. 2020 单独通过标题检索 (PMID 不可靠)
COLE_2020_QUERY = "Stanford Accelerated Intelligent Neuromodulation Therapy for Treatment-Resistant Depression"


class SearchOptimizer:
    """检索优化器"""

    def __init__(self):
        self.translations = MEDICAL_TRANSLATION
        self.synonyms = SYNONYMS
        self.mesh_terms = MESH_TERMS

    def translate_query(self, query_zh: str) -> str:
        """
        中文→英文翻译

        Args:
            query_zh: 中文检索词

        Returns:
            英文检索词
        """
        query_en = query_zh

        # 优先匹配长词
        sorted_terms = sorted(self.translations.keys(), key=len, reverse=True)

        for zh_term in sorted_terms:
            if zh_term in query_en:
                query_en = query_en.replace(zh_term, self.translations[zh_term])

        return query_en

    def expand_with_synonyms(self, query: str) -> List[str]:
        """
        同义词扩展

        Args:
            query: 检索词

        Returns:
            扩展后的检索词列表
        """
        expanded_queries = [query]

        # 对每个词进行同义词扩展
        words = query.lower().split()
        for word in words:
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    # 生成新的检索式
                    new_query = query.lower().replace(word, synonym)
                    if new_query not in expanded_queries:
                        expanded_queries.append(new_query)

        return expanded_queries

    def build_mesh_query(self, query: str) -> Tuple[str, List[str]]:
        """
        构建 MeSH 检索式

        Args:
            query: 检索词

        Returns:
            (主检索式，MeSH 词列表)
        """
        mesh_ids = []
        mesh_queries = []

        words = query.lower().split()
        for word in words:
            if word in self.mesh_terms:
                mesh_id = self.mesh_terms[word]
                mesh_ids.append(mesh_id)
                mesh_queries.append(f'"{word}"[Mesh Terms]')

        if mesh_queries:
            # MeSH 检索式
            mesh_query = " OR ".join(mesh_queries)
            # 组合自由词 + MeSH
            combined_query = f"({query}) OR ({mesh_query})"
            return combined_query, mesh_ids
        else:
            return query, []

    def build_advanced_query(self, query: str) -> Dict[str, str]:
        """
        构建高级检索式

        Args:
            query: 检索词

        Returns:
            不同策略的检索式
        """
        strategies = {}

        # 策略 1: 基础检索
        strategies['basic'] = query

        # 策略 2: MeSH 扩展
        mesh_query, mesh_ids = self.build_mesh_query(query)
        strategies['mesh'] = mesh_query

        # 策略 3: 同义词扩展
        expanded = self.expand_with_synonyms(query)
        if len(expanded) > 1:
            strategies['synonyms'] = f"({' OR '.join(expanded)})"

        # 策略 4: 字段限定 (标题/摘要)
        strategies['title_abstract'] = f"({query}[Title/Abstract])"

        # 策略 5: 综合策略 (最全面)
        comprehensive = self._build_comprehensive_query(query, mesh_query, expanded)
        strategies['comprehensive'] = comprehensive

        return strategies

    def _build_comprehensive_query(self, query: str, mesh_query: str, expanded: List[str]) -> str:
        """构建综合检索式"""
        parts = []

        # 自由词
        parts.append(f"({query})")

        # MeSH 词
        if mesh_query != query:
            parts.append(f"({mesh_query})")

        # 同义词
        if len(expanded) > 1:
            parts.append(f"({' OR '.join(expanded)})")

        return " OR ".join(parts)


# ========== 优化后的检索器 ==========

class OptimizedLiteratureSearcher:
    """优化的文献检索器"""

    def __init__(self, pubmed_api_key: str = None):
        from literature_search import LiteratureSearcher
        self.base_searcher = LiteratureSearcher(pubmed_api_key)
        self.optimizer = SearchOptimizer()

    def _build_pubmed_query(self, query: str, use_mesh: bool, use_synonyms: bool) -> str:
        """构建 PubMed 检索式 (支持 MeSH)"""
        parts = [f"({query})"]

        # MeSH 扩展
        if use_mesh:
            mesh_query, _ = self.optimizer.build_mesh_query(query)
            if mesh_query != query:
                parts.append(f"({mesh_query})")

        # 同义词扩展
        if use_synonyms:
            expanded = self.optimizer.expand_with_synonyms(query)
            if len(expanded) > 1:
                parts.append(f"({' OR '.join(expanded)})")

        return " OR ".join(parts)

    def _build_simple_query(self, query: str, use_synonyms: bool) -> str:
        """构建简单检索式 (Europe PMC 用)"""
        if use_synonyms:
            expanded = self.optimizer.expand_with_synonyms(query)
            if len(expanded) > 1:
                return f"({' OR '.join(expanded)})"
        return query

    def _search_with_queries(self, pubmed_query: str, europe_pmc_query: str,
                            max_results: int = 30) -> Dict:
        """使用不同检索式执行检索"""
        import concurrent.futures
        from literature_search import PubMedSearcher, EuropePMCSearcher, MeSHSearcher

        results = {
            'pubmed': [],
            'europe_pmc': [],
            'mesh': [],
            'merged': [],
            'total_count': 0
        }

        pubmed_searcher = PubMedSearcher()
        europe_pmc_searcher = EuropePMCSearcher()
        mesh_searcher = MeSHSearcher()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # PubMed (复杂检索式)
            future_pubmed = executor.submit(
                lambda: pubmed_searcher.search(pubmed_query, max_results)
            )

            # Europe PMC (简单检索式)
            future_europe_pmc = executor.submit(
                lambda: europe_pmc_searcher.search(europe_pmc_query, max_results)
            )

            # MeSH
            future_mesh = executor.submit(
                lambda: mesh_searcher.search(pubmed_query.split()[0] if pubmed_query.split() else "", 10)
            )

            # 等待结果
            try:
                results['pubmed'] = future_pubmed.result(timeout=300)
            except Exception as e:
                print(f"[PubMed] 检索超时/失败：{e}")
                results['pubmed'] = []

            try:
                results['europe_pmc'] = future_europe_pmc.result(timeout=300)
            except Exception as e:
                print(f"[Europe PMC] 检索超时/失败：{e}")
                results['europe_pmc'] = []

            try:
                results['mesh'] = future_mesh.result(timeout=300)
            except Exception as e:
                print(f"[MeSH] 检索超时/失败：{e}")
                results['mesh'] = []

        # 合并去重
        results['merged'] = self.base_searcher._merge_and_deduplicate(results)
        results['total_count'] = len(results['merged'])

        return results

    def search_comprehensive(self, query: str,
                            use_translation: bool = True,
                            use_mesh: bool = True,
                            use_synonyms: bool = True,
                            max_results: int = 30,
                            include_classics: bool = True,
                            citation_iterations: int = 2) -> Dict:
        """
        全面检索

        Args:
            query: 检索词 (支持中文)
            use_translation: 是否使用中文翻译
            use_mesh: 是否使用 MeSH 扩展
            use_synonyms: 是否使用同义词扩展
            max_results: 最大结果数
            include_classics: 是否包含经典文献 (默认 True)
            citation_iterations: 二次/三次/四次检索迭代次数 (默认 2 次)

        Returns:
            检索结果
        """
        print(f"===== 全面检索 =====")
        print(f"原始检索词：{query}")

        # Step 1: 中文翻译
        if use_translation and self._is_chinese(query):
            print(f"[优化] 检测到中文，自动翻译...")
            query_en = self.optimizer.translate_query(query)
            print(f"[优化] 翻译结果：{query_en}")
        else:
            query_en = query

        # Step 2: 构建检索式 (针对不同来源)
        print(f"[优化] 构建检索式...")

        # PubMed 使用复杂检索式 (支持 MeSH)
        pubmed_query = self._build_pubmed_query(query_en, use_mesh, use_synonyms)

        # Europe PMC 使用简单检索式 (不支持 MeSH)
        europe_pmc_query = self._build_simple_query(query_en, use_synonyms)

        print(f"[优化] PubMed 检索式：{pubmed_query[:80]}...")
        print(f"[优化] Europe PMC 检索式：{europe_pmc_query[:80]}...")

        # Step 3: 执行检索 (使用不同检索式)
        print(f"[优化] 执行检索...")
        results = self._search_with_queries(
            pubmed_query=pubmed_query,
            europe_pmc_query=europe_pmc_query,
            max_results=max_results
        )

        # Step 4: 添加经典文献 (防止漏检)
        if include_classics:
            print(f"[优化] 添加经典文献...")
            classic_papers = self._fetch_classic_papers()
            existing_pmids = {p.get('pmid') for p in results['merged']}

            added_count = 0
            for paper in classic_papers:
                if paper.get('pmid') not in existing_pmids:
                    paper['is_classic'] = True
                    paper['relevance'] = 1.0  # 经典文献最高相关性
                    results['merged'].append(paper)
                    added_count += 1

            if added_count > 0:
                print(f"[优化] 添加 {added_count} 篇经典文献")

            # 重新排序 (经典文献优先)
            results['merged'].sort(
                key=lambda x: (x.get('is_classic', False), x.get('relevance', 0)),
                reverse=True
            )

        # Step 4b: 二次/三次/四次检索 (基于参考文献分析，可迭代)
        if include_classics and citation_iterations > 0:
            print(f"[优化] 迭代检索：开始第 1 轮参考文献分析...")

            all_papers = results['merged'][:]
            seen_pmids = {p.get('pmid') for p in all_papers}
            total_new = 0

            for iteration in range(1, citation_iterations + 1):
                # 基于参考文献分析检索
                citation_papers = self._search_by_citation_analysis(all_papers, top_n=15)

                # 去重
                new_count = 0
                for paper in citation_papers:
                    if paper.get('pmid') not in seen_pmids:
                        paper['iteration'] = iteration
                        paper['relevance'] = max(0.9, 0.95 - iteration * 0.02)
                        all_papers.append(paper)
                        seen_pmids.add(paper.get('pmid'))
                        new_count += 1

                total_new += new_count
                print(f"[优化] 第{iteration}次检索：新增 {new_count} 篇")

                # 如果没有新文献，停止迭代
                if new_count == 0:
                    print(f"[优化] 无新文献，停止迭代")
                    break

                # 更新 results
                results['merged'] = all_papers
                results['total_count'] = len(all_papers)

            if total_new > 0:
                print(f"[优化] 迭代检索共添加 {total_new} 篇高引用文献")

        # Step 5: 结果增强
        print(f"[优化] 结果增强...")
        results = self._enhance_results(results, query_en)

        print(f"[优化] 检索完成：{results['total_count']} 篇")

        return results

    def _extract_references(self, papers: List[Dict]) -> Dict:
        """
        从已检索文献中提取参考文献，统计引用频次

        Returns:
            {
                "pmid1": {"count": 5, "title": "...", "papers": ["pmid_a", "pmid_b"]},
                "pmid2": {"count": 3, "title": "...", "papers": ["pmid_a"]},
            }
        """
        ref_counts = {}

        for paper in papers:
            # 从 PubMed 获取参考文献
            try:
                from literature_search import PubMedSearcher
                searcher = PubMedSearcher()

                # 获取单篇文献的完整信息（含参考文献）
                full_paper = searcher.fetch_paper(paper.get('pmid'))
                if full_paper and full_paper.get('references'):
                    for ref in full_paper['references']:
                        ref_pmid = ref.get('pmid')
                        if ref_pmid:
                            if ref_pmid not in ref_counts:
                                ref_counts[ref_pmid] = {
                                    'count': 0,
                                    'title': ref.get('title', ''),
                                    'papers': []
                                }
                            ref_counts[ref_pmid]['count'] += 1
                            ref_counts[ref_pmid]['papers'].append(paper.get('pmid'))
            except Exception as e:
                # 忽略单篇文献的参考文献获取失败
                pass

        # 按引用频次排序
        sorted_refs = sorted(
            ref_counts.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        return sorted_refs

    def _search_by_citation_analysis(self, papers: List[Dict], top_n: int = 10, min_citations: int = 2) -> List[Dict]:
        """
        基于参考文献分析的二次检索

        Args:
            papers: 第一次检索结果
            top_n: 分析前 N 个参考文献
            min_citations: 最小被引用次数阈值

        Returns:
            二次检索结果
        """
        from literature_search import PubMedSearcher

        # 提取参考文献
        references = self._extract_references(papers)

        if not references:
            print("  [二次检索] 无参考文献数据")
            return []

        print(f"  [二次检索] 分析 {len(references)} 个参考文献，被引用≥{min_citations}次...")

        # 检索高引用文献
        searcher = PubMedSearcher()
        classic_papers = []

        for ref_pmid, ref_info in references[:top_n]:
            if ref_info['count'] >= min_citations:  # 至少被 min_citations 篇文献引用
                try:
                    papers = searcher.search(ref_pmid, max_results=1)
                    if papers:
                        paper = papers[0]
                        paper['citation_count'] = ref_info['count']
                        paper['cited_by'] = ref_info['papers']
                        classic_papers.append(paper)
                        print(f"    [高引用] {paper.get('title', 'N/A')[:50]}... (被引用{ref_info['count']}次)")
                except Exception as e:
                    pass

        return classic_papers

    def _fetch_classic_papers(self) -> List[Dict]:
        """获取经典文献列表（手动维护的）"""
        from literature_search import PubMedSearcher

        searcher = PubMedSearcher()
        classic_papers = []

        # 通过 PMID 获取经典文献
        for name, pmid in CLASSIC_PAPERS.items():
            try:
                papers = searcher.search(pmid, max_results=1)
                if papers:
                    paper = papers[0]
                    paper['classic_name'] = name
                    classic_papers.append(paper)
                    print(f"  [经典文献] {paper.get('title', 'N/A')[:50]}... PMID: {pmid}")
            except Exception as e:
                print(f"  [经典文献获取失败] {pmid}: {e}")

        # Cole et al. 2020 单独通过标题检索 (PMID 不可靠)
        try:
            papers = searcher.search(COLE_2020_QUERY, max_results=2)
            for paper in papers:
                title = paper.get('title', '')
                if 'Stanford' in title and 'Accelerated' in title:
                    paper['classic_name'] = 'SNT_2020_Cole'
                    paper['is_classic'] = True
                    classic_papers.insert(0, paper)
                    print(f"  [经典文献] Cole et al. 2020 Am J Psychiatry...")
                    break
        except Exception as e:
            print(f"  [Cole 2020 获取失败]: {e}")

        return classic_papers

    def _is_chinese(self, text: str) -> bool:
        """检测是否包含中文"""
        import re
        chinese_pattern = re.compile(r'[一-鿿]')
        return bool(chinese_pattern.search(text))

    def _enhance_results(self, results: Dict, query: str) -> Dict:
        """增强检索结果"""
        # 添加相关性重评分
        for paper in results.get('merged', []):
            paper['enhanced_relevance'] = self._rescore_paper(paper, query)

        # 按增强后的相关性排序
        results['merged'].sort(
            key=lambda x: x.get('enhanced_relevance', 0),
            reverse=True
        )

        return results

    def _rescore_paper(self, paper: Dict, query: str) -> float:
        """重评分文献相关性"""
        score = paper.get('relevance', 0.5)

        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()

        # 标题匹配加分
        query_words = query.lower().split()
        for word in query_words:
            if len(word) > 3:  # 忽略短词
                if word in title:
                    score += 0.2
                if word in abstract:
                    score += 0.1

        # 近年文献加分
        try:
            pub_year = int(paper.get('pubdate', '0')[:4])
            if pub_year >= 2020:
                score += 0.1
            if pub_year >= 2024:
                score += 0.1
        except:
            pass

        # RCT/Meta 分析加分
        if 'randomized' in title or 'meta-analysis' in title:
            score += 0.1

        return min(score, 1.0)


# ========== 测试 ==========

if __name__ == '__main__':
    import sys
    from datetime import datetime

    # 创建检索器
    searcher = OptimizedLiteratureSearcher()

    # 测试检索
    if len(sys.argv) < 2:
        query = "右美托咪定 抗抑郁"
    else:
        query = ' '.join(sys.argv[1:])

    print(f"检索词：{query}")
    print(f"时间：{datetime.now()}")
    print()

    # 执行全面检索
    results = searcher.search_comprehensive(query, max_results=30)

    print()
    print(f"===== 检索结果 =====")
    print(f"PubMed: {len(results.get('pubmed', []))} 篇")
    print(f"Europe PMC: {len(results.get('europe_pmc', []))} 篇")
    print(f"MeSH: {len(results.get('mesh', []))} 个")
    print(f"合并后：{results['total_count']} 篇")
    print()

    # 显示前 10 篇
    print("前 10 篇文献:")
    for i, paper in enumerate(results['merged'][:10], 1):
        title = paper.get('title', 'N/A')[:80]
        pmid = paper.get('pmid', 'N/A')
        score = paper.get('enhanced_relevance', 0)
        print(f"{i}. {title}...")
        print(f"   PMID: {pmid} | 相关性：{score:.2f}")
