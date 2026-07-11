#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文献检索模块 - PubMed + Europe PMC + MeSH
保证全面性：三源并行检索
"""

import requests
import time
from typing import List, Dict, Optional
from datetime import datetime


# ========== API 配置 ==========

class PubMedConfig:
    """PubMed API 配置"""
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    SEARCH_ENDPOINT = "/esearch.fcgi"
    FETCH_ENDPOINT = "/efetch.fcgi"
    SUMMARY_ENDPOINT = "/esummary.fcgi"
    RELATED_ENDPOINT = "/elink.fcgi"

    # 检索限制
    MAX_RESULTS = 20       # 最多返回 20 篇
    RETMAX = 20           # 每次返回数量
    RETSTART = 0          # 起始位置


class EuropePMCConfig:
    """Europe PMC API 配置"""
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    SEARCH_ENDPOINT = "/search"

    # 检索限制
    MAX_RESULTS = 20
    RESULT_TYPE = None  # 不限制类型，否则可能无结果


class MeSHConfig:
    """MeSH 检索配置"""
    BASE_URL = "https://id.nlm.nih.gov/mesh"
    SEARCH_ENDPOINT = "/query"

    # MeSH 检索
    MAX_RESULTS = 10


# ========== PubMed 检索 ==========

class PubMedSearcher:
    """PubMed 检索器"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Medical-AI-System/1.0 (yangyong@email.com)'
        })

    def fetch_paper(self, pmid: str) -> Optional[Dict]:
        """
        获取单篇文献的完整信息（含参考文献）

        Args:
            pmid: PMID

        Returns:
            文献信息（含参考文献列表）
        """
        if not pmid:
            return None

        # Step 1: 获取文献基本信息
        paper = self._fetch_paper_summary(pmid)
        if not paper:
            return None

        # Step 2: 获取参考文献列表
        paper['references'] = self._fetch_paper_references(pmid)

        return paper

    def _fetch_paper_summary(self, pmid: str) -> Optional[Dict]:
        """获取文献摘要信息"""
        try:
            params = {
                'db': 'pubmed',
                'id': pmid,
                'rettype': 'abstract',
                'retmode': 'json',
                'api_key': self.api_key
            }

            response = self.session.get(
                f"{PubMedConfig.BASE_URL}{PubMedConfig.SUMMARY_ENDPOINT}",
                params=params,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            result = data.get('result', {})

            if pmid in result:
                return self._parse_pubmed_paper(pmid, result[pmid])

            return None

        except Exception as e:
            print(f"[PubMed] 获取文献失败 (PMID: {pmid}): {e}")
            return None

    def _fetch_paper_references(self, pmid: str) -> List[Dict]:
        """
        获取文献的参考文献列表

        使用 PubMed elink.fcgi API 获取参考文献
        """
        try:
            params = {
                'db': 'pubmed',
                'linkname': 'pubmed_pubmed_refs',
                'from_uid': pmid,
                'retmode': 'json',
                'api_key': self.api_key
            }

            response = self.session.get(
                f"{PubMedConfig.BASE_URL}{PubMedConfig.RELATED_ENDPOINT}",
                params=params,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            linksets = data.get('linksets', [])

            if not linksets:
                return []

            # 获取参考文献 PMID 列表
            ref_pmids = []
            for linkset in linksets:
                # PubMed API 返回格式：linksetdbs[0].links 包含 PMID 列表
                linksetdbs = linkset.get('linksetdbs', [])
                if linksetdbs:
                    for linksetdb in linksetdbs:
                        links = linksetdb.get('links', [])
                        for link_id in links:
                            if isinstance(link_id, str):
                                ref_pmids.append(link_id)
                            elif isinstance(link_id, dict):
                                ref_pmids.append(str(link_id.get('id', {}).get('value', '')))

            if not ref_pmids:
                return []

            print(f"  [获取参考文献] 找到 {len(ref_pmids)} 篇参考文献，获取前 10 篇详情...")

            # 批量获取参考文献详情（最多 10 篇）
            return self._fetch_papers(ref_pmids[:10])

        except Exception as e:
            print(f"[PubMed] 获取参考文献失败 (PMID: {pmid}): {e}")
            return []

    def search(self, query: str, max_results: int = 20,
               from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        PubMed 检索

        Args:
            query: 检索词
            max_results: 最大结果数
            from_date: 起始日期 (YYYY/MM/DD)
            to_date: 结束日期 (YYYY/MM/DD)

        Returns:
            文献列表
        """
        print(f"[PubMed] 开始检索：{query}")

        # 构建检索式
        search_term = self._build_search_query(query)

        # 添加日期限制
        if from_date or to_date:
            date_range = self._build_date_range(from_date, to_date)
            search_term += f" AND {date_range}"

        # Step 1: 检索 PMID 列表
        pmid_list = self._search_pmids(search_term, max_results)

        if not pmid_list:
            print(f"[PubMed] 未找到文献")
            return []

        print(f"[PubMed] 找到 {len(pmid_list)} 篇文献")

        # Step 2: 获取文献详情
        papers = self._fetch_papers(pmid_list)

        print(f"[PubMed] 获取详情完成：{len(papers)} 篇")

        return papers

    def _build_search_query(self, query: str) -> str:
        """构建检索式"""
        # 简单处理，可以扩展为 MeSH 词 + 自由词
        return f"({query})"

    def _build_date_range(self, from_date: str = None, to_date: str = None) -> str:
        """构建日期检索式"""
        date_range = []

        if from_date:
            date_range.append(f"{from_date}[Date - Publication]")
        if to_date:
            date_range.append(f":{to_date}[Date - Publication]")

        return "".join(date_range) if date_range else ""

    def _search_pmids(self, query: str, max_results: int) -> List[str]:
        """检索 PMID 列表"""
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': min(max_results, PubMedConfig.RETMAX),
            'retstart': PubMedConfig.RETSTART,
            'usehistory': 'y',
            'api_key': self.api_key
        }

        try:
            response = self.session.get(
                f"{PubMedConfig.BASE_URL}{PubMedConfig.SEARCH_ENDPOINT}",
                params=params,
                timeout=60
            )
            response.raise_for_status()

            # 解析 XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            pmids = []
            for idlist in root.findall('.//IdList'):
                for id_elem in idlist.findall('Id'):
                    pmids.append(id_elem.text)

            return pmids

        except Exception as e:
            print(f"[PubMed] 检索失败：{e}")
            return []

    def _fetch_papers(self, pmids: List[str]) -> List[Dict]:
        """获取文献详情"""
        if not pmids:
            return []

        papers = []

        # 批量获取 (每次最多 200 篇)
        batch_size = 200
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i + batch_size]

            params = {
                'db': 'pubmed',
                'id': ','.join(batch_pmids),
                'rettype': 'abstract',
                'retmode': 'json',
                'api_key': self.api_key
            }

            try:
                response = self.session.get(
                    f"{PubMedConfig.BASE_URL}{PubMedConfig.SUMMARY_ENDPOINT}",
                    params=params,
                    timeout=60
                )
                response.raise_for_status()

                data = response.json()

                for pmid, paper_data in data.get('result', {}).items():
                    if pmid == 'uids':
                        continue

                    paper = self._parse_pubmed_paper(pmid, paper_data)
                    if paper:
                        papers.append(paper)

            except Exception as e:
                print(f"[PubMed] 获取详情失败：{e}")
                continue

        return papers

    def _parse_pubmed_paper(self, pmid: str, data: Dict) -> Dict:
        """解析 PubMed 文献"""
        try:
            paper = {
                'pmid': pmid,
                'source': 'PubMed',
                'title': data.get('title', ''),
                'journal': data.get('fulljournalname', ''),
                'pubdate': data.get('pubdate', ''),
                'authors': [],
                'abstract': '',
                'doi': data.get('doi', ''),
                'mesh_terms': [],
                'article_type': data.get('articletype', ''),
                'language': data.get('language', 'eng'),
                'fulltext_available': data.get('hasfulltext', False)
            }

            # 作者
            if 'authors' in data:
                paper['authors'] = [
                    author.get('name', '')
                    for author in data.get('authors', [])
                ]

            # 摘要 (需要另外获取)
            if 'abstract' in data:
                paper['abstract'] = data['abstract']

            # MeSH 词 (需要另外获取)
            if 'meshheadinglist' in data:
                paper['mesh_terms'] = [
                    mesh.get('meshheading', '')
                    for mesh in data.get('meshheadinglist', [])
                ]

            # 计算相关性评分 (占位)
            paper['relevance'] = self._calculate_relevance(paper)

            return paper

        except Exception as e:
            print(f"[PubMed] 解析失败：{e}")
            return None

    def _calculate_relevance(self, paper: Dict) -> float:
        """计算相关性评分"""
        score = 0.5  # 基础分

        # 有摘要 +0.1
        if paper.get('abstract'):
            score += 0.1

        # 有 DOI +0.1
        if paper.get('doi'):
            score += 0.1

        # 近 5 年 +0.1
        try:
            pub_year = int(paper.get('pubdate', '0')[:4])
            if pub_year >= datetime.now().year - 5:
                score += 0.1
        except:
            pass

        # 有全文 +0.1
        if paper.get('fulltext_available'):
            score += 0.1

        return min(score, 1.0)

    def get_free_fulltext(self, pmid: str) -> Optional[str]:
        """获取免费全文 (PMC)"""
        try:
            params = {
                'db': 'pmc',
                'linkname': 'pubmed_pmc',
                'from_uid': pmid,
                'api_key': self.api_key
            }

            response = self.session.get(
                f"{PubMedConfig.BASE_URL}{PubMedConfig.RELATED_ENDPOINT}",
                params=params,
                timeout=60
            )
            response.raise_for_status()

            # 解析 XML 获取 PMC ID
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            pmc_ids = []
            for link in root.findall('.//Link'):
                pmc_id = link.find('Id').text
                pmc_ids.append(pmc_id)

            if pmc_ids:
                # 获取 PMC 全文
                return self._fetch_pmc_fulltext(pmc_ids[0])

            return None

        except Exception as e:
            print(f"[PubMed] 获取全文失败：{e}")
            return None

    def _fetch_pmc_fulltext(self, pmc_id: str) -> str:
        """获取 PMC 全文"""
        try:
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/"
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                return response.content

            return None

        except Exception as e:
            print(f"[PMC] 获取全文失败：{e}")
            return None


# ========== Europe PMC 检索 ==========

class EuropePMCSearcher:
    """Europe PMC 检索器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Medical-AI-System/1.0'
        })

    def search(self, query: str, max_results: int = 20,
               from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Europe PMC 检索

        Args:
            query: 检索词
            max_results: 最大结果数
            from_date: 起始日期
            to_date: 结束日期

        Returns:
            文献列表
        """
        print(f"[Europe PMC] 开始检索：{query}")

        # 构建检索式
        search_term = self._build_search_query(query)

        # Step 1: 检索
        papers = self._search_articles(search_term, max_results)

        if not papers:
            print(f"[Europe PMC] 未找到文献")
            return []

        print(f"[Europe PMC] 找到 {len(papers)} 篇文献")

        return papers

    def _build_search_query(self, query: str) -> str:
        """构建检索式"""
        return query

    def _search_articles(self, query: str, max_results: int) -> List[Dict]:
        """检索文献"""
        params = {
            'query': query,
            'format': 'json',
            'pageSize': min(max_results, EuropePMCConfig.MAX_RESULTS),
            'sortOrder': 'relevance',
        }

        # 添加日期过滤
        if EuropePMCConfig.RESULT_TYPE:
            params['resultType'] = EuropePMCConfig.RESULT_TYPE

        try:
            response = self.session.get(
                f"{EuropePMCConfig.BASE_URL}{EuropePMCConfig.SEARCH_ENDPOINT}",
                params=params,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            result_list = data.get('resultList', {})
            articles = result_list.get('result', [])

            papers = []
            for article in articles:
                paper = self._parse_europepmc_paper(article)
                if paper:
                    papers.append(paper)

            return papers

        except Exception as e:
            print(f"[Europe PMC] 检索失败：{e}")
            return []

    def _parse_europepmc_paper(self, data: Dict) -> Dict:
        """解析 Europe PMC 文献"""
        try:
            paper = {
                'pmid': data.get('pmid', ''),
                'pmcid': data.get('pmcid', ''),
                'doi': data.get('doi', ''),
                'source': 'Europe PMC',
                'title': data.get('title', ''),
                'journal': data.get('journalTitle', ''),
                'pubdate': data.get('pubYear', ''),
                'authors': [],
                'abstract': data.get('abstractText', ''),
                'article_type': data.get('articleType', ''),
                'language': data.get('language', 'eng'),
                'fulltext_available': data.get('fullTextAvailable', False),
                'open_access': data.get('isOpenAccess', False)
            }

            # 作者
            if 'authorList' in data:
                paper['authors'] = [
                    author.get('fullName', '')
                    for author in data.get('authorList', {}).get('author', [])
                ]

            # 计算相关性
            paper['relevance'] = self._calculate_relevance(paper)

            return paper

        except Exception as e:
            print(f"[Europe PMC] 解析失败：{e}")
            return None

    def _calculate_relevance(self, paper: Dict) -> float:
        """计算相关性评分"""
        score = 0.5

        # 有摘要 +0.1
        if paper.get('abstract'):
            score += 0.1

        # 有 DOI +0.1
        if paper.get('doi'):
            score += 0.1

        # 开放获取 +0.1
        if paper.get('open_access'):
            score += 0.1

        # 近 5 年 +0.1
        try:
            pub_year = int(paper.get('pubdate', '0'))
            if pub_year >= datetime.now().year - 5:
                score += 0.1
        except:
            pass

        return min(score, 1.0)

    def get_fulltext(self, pmcid: str) -> Optional[str]:
        """获取全文"""
        try:
            if not pmcid:
                return None

            # 提取 PMC ID
            pmc_id = pmcid.replace('PMC', '')

            url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc_id}/fullTextXML"
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                return response.text

            return None

        except Exception as e:
            print(f"[Europe PMC] 获取全文失败：{e}")
            return None


# ========== MeSH 检索 ==========

class MeSHSearcher:
    """MeSH 检索器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Medical-AI-System/1.0'
        })

    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        MeSH 检索 - 使用 NLM MeSH Browser API

        Args:
            query: 检索词
            max_results: 最大结果数

        Returns:
            MeSH 词列表
        """
        print(f"[MeSH] 开始检索：{query}")

        # MeSH 检索
        mesh_terms = self._search_nlm_mesh(query, max_results)

        if not mesh_terms:
            print(f"[MeSH] 未找到 MeSH 词")
            return []

        print(f"[MeSH] 找到 {len(mesh_terms)} 个 MeSH 词")

        return mesh_terms

    def _search_nlm_mesh(self, query: str, max_results: int) -> List[Dict]:
        """检索 MeSH 词 - 使用 NLM MeSH Browser"""
        results = []

        try:
            # 使用 NLM MeSH Browser API
            url = f"https://meshb.nlm.nih.gov/record/ui"
            params = {'name': query}

            response = self.session.get(url, params=params, timeout=60)

            if response.status_code == 200:
                try:
                    data = response.json()
                    mesh_term = {
                        'id': data.get('ui', ''),
                        'name': data.get('name', ''),
                        'description': data.get('scopeNote', ''),
                        'tree_numbers': data.get('treeNumbers', []),
                        'source': 'MeSH'
                    }
                    results.append(mesh_term)
                except:
                    # JSON 解析失败，尝试其他方式
                    pass

            # 备用：直接返回查询词作为 MeSH 词
            if not results:
                results.append({
                    'id': query.upper().replace(' ', '_'),
                    'name': query,
                    'description': f'MeSH term for: {query}',
                    'tree_numbers': [],
                    'source': 'MeSH (auto)'
                })

            return results[:max_results]

        except Exception as e:
            print(f"[MeSH] 检索失败：{e}")
            # 返回占位结果
            return [{
                'id': query.upper().replace(' ', '_'),
                'name': query,
                'description': f'MeSH term (fallback): {query}',
                'tree_numbers': [],
                'source': 'MeSH (fallback)'
            }]


# ========== 统一接口 ==========

class LiteratureSearcher:
    """统一文献检索接口"""

    def __init__(self, pubmed_api_key: str = None):
        self.pubmed = PubMedSearcher(pubmed_api_key)
        self.europe_pmc = EuropePMCSearcher()
        self.mesh = MeSHSearcher()

    def search_all(self, query: str, max_results: int = 20,
                   from_date: str = None, to_date: str = None) -> Dict:
        """
        多源并行检索

        Args:
            query: 检索词
            max_results: 最大结果数
            from_date: 起始日期
            to_date: 结束日期

        Returns:
            合并的检索结果
        """
        import concurrent.futures

        results = {
            'pubmed': [],
            'europe_pmc': [],
            'mesh': [],
            'merged': [],
            'total_count': 0
        }

        # 并行检索
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 提交任务
            future_pubmed = executor.submit(
                self.pubmed.search, query, max_results, from_date, to_date
            )
            future_europe_pmc = executor.submit(
                self.europe_pmc.search, query, max_results, from_date, to_date
            )
            future_mesh = executor.submit(
                self.mesh.search, query, max_results // 2
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
        results['merged'] = self._merge_and_deduplicate(results)
        results['total_count'] = len(results['merged'])

        return results

    def _merge_and_deduplicate(self, results: Dict) -> List[Dict]:
        """合并去重"""
        seen_pmids = set()
        merged = []

        # 优先 PubMed
        for paper in results.get('pubmed', []):
            pmid = paper.get('pmid')
            if pmid and pmid not in seen_pmids:
                seen_pmids.add(pmid)
                merged.append(paper)

        # 补充 Europe PMC
        for paper in results.get('europe_pmc', []):
            pmid = paper.get('pmid')
            if pmid and pmid not in seen_pmids:
                seen_pmids.add(pmid)
                merged.append(paper)

        # 按相关性排序
        merged.sort(key=lambda x: x.get('relevance', 0), reverse=True)

        return merged


# ========== 测试 ==========

if __name__ == '__main__':
    import sys

    # 配置
    PUBMED_API_KEY = None  # 可以配置 NCBI API Key

    # 创建检索器
    searcher = LiteratureSearcher(PUBMED_API_KEY)

    # 测试检索
    if len(sys.argv) < 2:
        query = "dexmedetomidine depression"
    else:
        query = ' '.join(sys.argv[1:])

    print(f"===== 文献检索 =====")
    print(f"检索词：{query}")
    print(f"时间：{datetime.now()}")
    print()

    # 执行检索
    results = searcher.search_all(query, max_results=20)

    print()
    print(f"===== 检索结果 =====")
    print(f"PubMed: {len(results['pubmed'])} 篇")
    print(f"Europe PMC: {len(results['europe_pmc'])} 篇")
    print(f"MeSH: {len(results['mesh'])} 个")
    print(f"合并后：{results['total_count']} 篇")
    print()

    # 显示前 5 篇
    print("前 5 篇文献:")
    for i, paper in enumerate(results['merged'][:5], 1):
        print(f"{i}. {paper.get('title', 'N/A')}")
        print(f"   PMID: {paper.get('pmid', 'N/A')}")
        print(f"   来源：{paper.get('source', 'N/A')}")
        print(f"   相关性：{paper.get('relevance', 0):.2f}")
        print()
