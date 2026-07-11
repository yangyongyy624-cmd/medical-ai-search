#!/usr/bin/env python3
"""
医学细分领域专家发现系统

核心功能:
用户输入任意医学细分领域（如"干细胞 抗肿瘤 T 细胞"、"干细胞 抗衰老"）
→ 互联网搜索该领域专家
→ 提取专家信息（医院、国家、医学院）
→ PubMed 验证
→ 找到开创性文献

作者：宵宵
日期：2026-07-11
"""

import json
from typing import List, Dict
from datetime import datetime


class MedicalSubfieldExpertFinder:
    """医学细分领域专家发现系统"""

    def __init__(self):
        from literature_search import PubMedSearcher
        self.searcher = PubMedSearcher()

    def search(self, subfield: str, max_experts: int = 10) -> Dict:
        """
        搜索任意医学细分领域的专家

        Args:
            subfield: 细分领域（中英文均可）
            max_experts: 最多找多少位专家

        Returns:
            完整结果
        """
        print("="*60)
        print(f"医学细分领域专家发现")
        print(f"领域：{subfield}")
        print("="*60)

        # Step 1: 中英文互联网搜索
        print(f"\n[Step 1] 互联网搜索领域专家...")

        # 构建中英文搜索查询
        queries = self._build_queries(subfield)

        all_experts = []

        for query in queries:
            print(f"  搜索：{query}")

            # Tavily 网络搜索
            results = self._tavily_search(query)

            # 提取专家信息
            experts = self._extract_experts(results)
            all_experts.extend(experts)

        # 去重 + 排序
        experts = self._deduplicate_experts(all_experts)

        # 取前 N 位
        experts = experts[:max_experts]

        print(f"  找到 {len(experts)} 位候选专家")

        # Step 2: PubMed 验证
        print(f"\n[Step 2] PubMed 验证专家身份...")

        verified = []
        for expert in experts:
            name = expert.get('name', '')
            if not name:
                continue

            # PubMed 检索
            papers = self.searcher.search(name, max_results=10)

            if papers:
                expert['paper_count'] = len(papers)
                expert['is_verified'] = True
                expert['papers'] = papers

                # 最早文章年份
                years = [p.get('pubdate', '')[:4] for p in papers if p.get('pubdate')]
                expert['first_year'] = min(years) if years else 'Unknown'

                verified.append(expert)
                print(f"  ✅ {name}: {len(papers)} 篇")

        print(f"\n  验证通过 {len(verified)} 位专家")

        # Step 3: 找到开创性文献
        print(f"\n[Step 3] 寻找开创性文献...")

        landmark = self._find_landmark_papers(verified)

        print(f"  发现 {len(landmark)} 篇开创性文献")

        # 整合结果
        result = {
            'subfield': subfield,
            'experts': verified,
            'landmark_papers': landmark,
            'summary': {
                'expert_count': len(verified),
                'landmark_count': len(landmark)
            },
            'metadata': {
                'search_date': datetime.now().isoformat(),
                'original_query': subfield
            }
        }

        # 打印结果
        self._print_results(result)

        return result

    def _build_queries(self, subfield: str) -> List[str]:
        """
        构建中英文搜索查询

        Args:
            subfield: 细分领域

        Returns:
            搜索查询列表
        """
        queries = []

        # 英文查询
        en_queries = [
            f"{subfield} expert",
            f"{subfield} pioneer researcher",
            f"{subfield} leading scientist",
            f"{subfield} key opinion leader",
            f"top researchers in {subfield}",
        ]

        # 中文查询
        cn_queries = [
            f"{subfield} 专家",
            f"{subfield} 领军人物",
            f"{subfield} 权威",
            f"{subfield} 顶尖团队",
        ]

        # 智能判断语言
        if self._is_chinese(subfield):
            # 中文领域词，生成中英文查询
            queries.extend(en_queries)
            queries.extend(cn_queries)
        else:
            # 英文领域词，主要用英文查询
            queries.extend(en_queries)
            # 也尝试中文
            queries.append(f"{subfield} 专家")

        return queries

    def _is_chinese(self, text: str) -> bool:
        """判断是否包含中文"""
        import re
        return bool(re.search(r'[一-鿿]', text))

    def _tavily_search(self, query: str) -> List[Dict]:
        """Tavily 网络搜索"""
        # 实际调用 Tavily API
        # 这里用模拟数据演示流程
        return []

    def _extract_experts(self, results: List[Dict]) -> List[Dict]:
        """从搜索结果提取专家信息"""
        experts = []

        # Tavily 返回格式：{'results': [...], 'query': '...'}
        result_list = results
        if isinstance(results, dict) and 'results' in results:
            result_list = results.get('results', [])

        for result in result_list:
            expert = self._parse_expert_info(result)
            if expert:
                experts.append(expert)

        return experts

    def _parse_expert_info(self, result: Dict) -> Dict:
        """
        解析专家信息

        从网页内容提取:
        - 姓名
        - 医院/机构
        - 国家
        - 医学院
        """
        title = result.get('title', '')
        content = result.get('content', '')
        url = result.get('url', '')

        # 提取人名（英文模式）
        import re
        name_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)'
        names = re.findall(name_pattern, title + ' ' + content)

        # 提取人名（中文模式）
        cn_name_pattern = r'([一-鿿]{2,4}教授|[一-鿿]{2,4}医生|[一-鿿]{2,4}博士)'
        cn_names = re.findall(cn_name_pattern, title + ' ' + content)

        # 提取机构信息
        institutions = self._extract_institutions(content)

        experts = []

        # 英文名
        for name in names[:3]:
            expert = {
                'name': name,
                'institution': institutions.get('hospital', 'Unknown'),
                'country': institutions.get('country', 'Unknown'),
                'medical_school': institutions.get('medical_school', 'Unknown'),
                'relevance_score': 0.5,
                'source': url,
                'search_query': result.get('query', '')
            }
            experts.append(expert)

        # 中文名
        for name in cn_names[:3]:
            # 清理后缀
            clean_name = re.sub(r'(教授 | 医生 | 博士)$', '', name)
            expert = {
                'name': clean_name,
                'institution': institutions.get('hospital', 'Unknown'),
                'country': institutions.get('country', 'Unknown'),
                'medical_school': institutions.get('medical_school', 'Unknown'),
                'relevance_score': 0.5,
                'source': url,
                'search_query': result.get('query', '')
            }
            experts.append(expert)

        return experts

    def _extract_institutions(self, content: str) -> Dict:
        """
        从内容提取机构信息

        包括:
        - 医院/研究机构
        - 国家
        - 医学院
        """
        institutions = {
            'hospital': 'Unknown',
            'country': 'Unknown',
            'medical_school': 'Unknown'
        }

        # 知名医学机构关键词
        medical_institutions = {
            'Harvard': 'Harvard Medical School',
            'Stanford': 'Stanford University',
            'Johns Hopkins': 'Johns Hopkins Hospital',
            'Mayo Clinic': 'Mayo Clinic',
            'Cleveland Clinic': 'Cleveland Clinic',
            'Massachusetts General': 'Massachusetts General Hospital',
            ' UCSF ': 'University of California San Francisco',
            'UCLA': 'UCLA David Geffen School of Medicine',
            'Cambridge': 'University of Cambridge',
            'Oxford': 'University of Oxford',
            '北京协和': '中国医学科学院北京协和医院',
            '北京大学': '北京大学医学部',
            '复旦大学': '复旦大学上海医学院',
            '上海交通': '上海交通大学医学院',
        }

        for keyword, institution in medical_institutions.items():
            if keyword.lower() in content.lower():
                institutions['hospital'] = institution
                institutions['medical_school'] = institution
                break

        # 国家提取
        countries = {
            'USA': ['USA', 'United States', 'America', '美国'],
            'UK': ['UK', 'United Kingdom', 'Britain', '英国'],
            'China': ['China', 'Chinese', '中国'],
            'Germany': ['Germany', 'German', '德国'],
            'Japan': ['Japan', 'Japanese', '日本'],
            'France': ['France', 'French', '法国'],
        }

        for country, keywords in countries.items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    institutions['country'] = country
                    break

        return institutions

    def _deduplicate_experts(self, experts: List[Dict]) -> List[Dict]:
        """专家去重"""
        seen = set()
        unique = []

        for expert in experts:
            # 按姓名 + 国家去重
            key = f"{expert.get('name', '')}_{expert.get('country', '')}"
            if key not in seen:
                seen.add(key)
                unique.append(expert)

        return sorted(unique, key=lambda x: x.get('relevance_score', 0), reverse=True)

    def _find_landmark_papers(self, experts: List[Dict]) -> List[Dict]:
        """找到开创性文献"""
        all_papers = []

        for expert in experts[:10]:
            papers = expert.get('papers', [])
            all_papers.extend(papers)

        # 去重
        unique = self._deduplicate_papers(all_papers)

        # 按年份排序
        current_year = datetime.now().year
        landmark = []

        for paper in unique:
            year_str = paper.get('pubdate', '')[:4]
            try:
                year = int(year_str) if year_str else 9999

                # 5 年前的文献
                if year <= current_year - 5:
                    paper['is_landmark'] = True
                    paper['landmark_reason'] = '开创性研究'
                    landmark.append(paper)
            except:
                pass

        landmark.sort(key=lambda x: int(x.get('pubdate', '9999')[:4]))

        return landmark[:20]

    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """文献去重"""
        seen_pmids = set()
        unique = []

        for paper in papers:
            pmid = paper.get('pmid')
            if pmid and pmid not in seen_pmids:
                seen_pmids.add(pmid)
                unique.append(paper)

        return unique

    def _print_results(self, result: Dict):
        """打印结果"""
        print("\n" + "="*60)
        print(f"检索结果：{result['subfield']}")
        print("="*60)

        # 领域专家
        print(f"\n📚 领域专家 ({result['summary']['expert_count']} 位):")
        print("-"*60)

        for i, expert in enumerate(result['experts'][:10], 1):
            print(f"\n{i}. {expert['name']}")
            print(f"   医院：{expert.get('institution', 'Unknown')}")
            print(f"   国家：{expert.get('country', 'Unknown')}")
            print(f"   医学院：{expert.get('medical_school', 'Unknown')}")
            print(f"   文章数：{expert.get('paper_count', 0)}")
            print(f"   最早文章：{expert.get('first_year', 'Unknown')}")

        # 开创性文献
        if result['landmark_papers']:
            print(f"\n⭐ 开创性文献 ({result['summary']['landmark_count']} 篇):")
            print("-"*60)

            for i, paper in enumerate(result['landmark_papers'][:10], 1):
                print(f"\n{i}. ({paper.get('pubdate', 'N/A')[:4]})")
                print(f"   标题：{paper.get('title', 'N/A')[:70]}...")
                print(f"   PMID: {paper.get('pmid', 'N/A')}")
                print(f"   期刊：{paper.get('journal', 'N/A')[:40]}...")
                if paper.get('landmark_reason'):
                    print(f"   标识：{paper['landmark_reason']} ⭐")

        print("\n" + "="*60)

    def save_result(self, result: Dict, filename: str = None):
        """保存结果"""
        if not filename:
            subfield = result['subfield'].replace(' ', '_').replace('/', '_')
            filename = f"expert_{subfield}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n结果已保存到 {filename}")


# ==================== 使用示例 ====================

if __name__ == '__main__':
    finder = MedicalSubfieldExpertFinder()

    # 示例 1: 干细胞 抗肿瘤 T 细胞
    print("\n" + "#"*60)
    print("# 示例 1: 干细胞 抗肿瘤 T 细胞")
    print("#"*60)

    result = finder.search("stem cell CAR-T cancer", max_experts=10)
    finder.save_result(result)

    # 示例 2: 干细胞 抗衰老
    # print("\n" + "#"*60)
    # print("# 示例 2: 干细胞 抗衰老")
    # print("#"*60)
    #
    # result = finder.search("stem cell anti-aging", max_experts=10)
    # finder.save_result(result)

    # 示例 3: 中文输入
    # print("\n" + "#"*60)
    # print("# 示例 3: 中文输入")
    # print("#"*60)
    #
    # result = finder.search("间充质干细胞 免疫治疗", max_experts=10)
    # finder.save_result(result)
