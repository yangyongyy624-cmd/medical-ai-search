#!/usr/bin/env python3
"""
行业大佬文献调研 - 一键执行

功能:
1. 找到 Top 10 大佬
2. 检索每位大佬的高分文献
3. 自动生成 Obsidian 笔记

作者：宵宵
日期：2026-07-11
"""

import json
import os
from datetime import datetime
from typing import List, Dict


class BigShotLiteratureSurvey:
    """大佬文献调研系统"""

    def __init__(self, obsidian_vault: str = None):
        self.obsidian_vault = obsidian_vault or self._find_obsidian_vault()
        self.notes_folder = os.path.join(self.obsidian_vault, "06-领域大佬文献调研")
        os.makedirs(self.notes_folder, exist_ok=True)

        from simple_big_shot_finder import SimpleBigShotFinder
        from literature_search import PubMedSearcher

        self.big_shot_finder = SimpleBigShotFinder()
        self.pubmed_searcher = PubMedSearcher()

        # 高分期刊列表
        self.top_journals = [
            'nature', 'science', 'cell',
            'nejm', 'lancet', 'bmj',
            'jam', 'annals of internal medicine',
            'nature medicine', 'nature biotechnology',
            'cancer cell', 'immunity',
        ]

    def _find_obsidian_vault(self) -> str:
        """自动查找 Obsidian Vault"""
        common_paths = [
            os.path.expanduser("~/Documents/Obsidian Vault"),
            os.path.expanduser("~/Documents/Obsidian"),
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return os.getcwd()

    def survey(self, subfield: str, top_n: int = 10):
        """
        完整调研流程

        Args:
            subfield: 细分领域
            top_n: Top N 大佬（默认 10）
        """
        print(f"\n{'='*60}")
        print(f"行业大佬文献调研：{subfield}")
        print(f"{'='*60}")

        # Step 1: 找大佬
        print(f"\n[Step 1] 找到行业大佬...")
        big_shots = self.big_shot_finder.find_big_shots(subfield)
        big_shots = big_shots[:top_n]
        print(f"  选定 Top {len(big_shots)} 位")

        # Step 2: 检索高分文献
        print(f"\n[Step 2] 检索每位大佬的高分文献...")
        for expert in big_shots:
            papers = self._find_high_impact_papers(expert['name'], subfield)
            expert['papers'] = papers
            print(f"  ✅ {expert['name']}: {len(papers)} 篇高分文献")

        # Step 3: 生成 Obsidian 笔记
        print(f"\n[Step 3] 生成 Obsidian 笔记...")
        note_file = self._create_obsidian_note(subfield, big_shots)
        print(f"  ✅ 笔记已保存：{note_file}")

        # Step 4: 生成 JSON
        json_file = os.path.join(self.notes_folder, f"{subfield.replace(' ', '_')}_data.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(big_shots, f, indent=2, ensure_ascii=False)
        print(f"  ✅ 数据已保存：{json_file}")

        return big_shots

    def _find_high_impact_papers(self, name: str, subfield: str, max_papers: int = 5) -> List[Dict]:
        """找到某位大佬的高分文献"""
        papers = self.pubmed_searcher.search(name, max_results=20)

        # 过滤高分期刊
        high_impact = []
        for paper in papers:
            journal = paper.get('journal', '').lower()
            if any(j in journal for j in self.top_journals):
                high_impact.append(paper)

        # 按被引排序（如果有被引数据）
        high_impact.sort(key=lambda x: x.get('citation_count', 0), reverse=True)

        return high_impact[:max_papers]

    def _create_obsidian_note(self, subfield: str, big_shots: List[Dict]) -> str:
        """创建 Obsidian 笔记"""
        filename = os.path.join(
            self.notes_folder,
            f"{subfield.replace(' ', '_').replace('/', '_')}_大佬文献调研.md"
        )

        content = f"""---
created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
tags:
  - 领域大佬
  - {subfield.replace(' ', '_')}
  - 文献调研
aliases: []
---

# {subfield} - 行业顶尖科学家文献调研

> **调研日期**: {datetime.now().strftime('%Y-%m-%d')}
> **大佬数量**: {len(big_shots)} 位
> **筛选标准**: 学术影响力 + 文章数量 + 行业地位 + 实际贡献

---

## 📚 Top {len(big_shots)} 大佬名单

"""
        # 大佬列表
        for i, expert in enumerate(big_shots, 1):
            expert_filename = self._sanitize_filename(expert['name'])
            identities = ' + '.join(expert.get('identities', []))

            content += f"""
### {i}. [[{expert_filename}|{expert['name']}]]

**身份**: {identities}

**代表文献**（高分期刊）:

"""
            # 文献列表
            for j, paper in enumerate(expert.get('papers', []), 1):
                pmid = paper.get('pmid', 'unknown')
                title = paper.get('title', 'N/A')[:60]
                journal = paper.get('journal', 'N/A')
                year = paper.get('pubdate', 'N/A')[:4]

                content += f"""
{j}. [[PMID_{pmid}|{title}...]]
   - **期刊**: {journal}
   - **年份**: {year}
   - **PMID**: {pmid}

"""

        content += f"""
---

##  按期刊分类

### Nature/Science/Cell
"""
        # 按期刊分类
        nature_papers = self._collect_papers_by_journal(big_shots, ['nature', 'science', 'cell'])
        for paper in nature_papers[:10]:
            content += f"- [[PMID_{paper['pmid']}]] - {paper.get('author', 'Unknown')} - {paper.get('title', 'N/A')[:40]}...\n"

        content += f"""

### NEJM/Lancet/BMJ
"""
        nejm_papers = self._collect_papers_by_journal(big_shots, ['nejm', 'lancet', 'bmj'])
        for paper in nejm_papers[:10]:
            content += f"- [[PMID_{paper['pmid']}]] - {paper.get('author', 'Unknown')} - {paper.get('title', 'N/A')[:40]}...\n"

        content += f"""

---

## 🔗 快速导航

"""
        for expert in big_shots:
            content += f"[[{self._sanitize_filename(expert['name'])}|{expert['name']}]] "

        content += f"""

---

**自动生成**: 行业大佬文献调研系统 v1.0
**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        return filename

    def _collect_papers_by_journal(self, big_shots: List[Dict], journals: List[str]) -> List[Dict]:
        """按期刊收集文献"""
        papers = []
        for expert in big_shots:
            for paper in expert.get('papers', []):
                journal = paper.get('journal', '').lower()
                if any(j in journal for j in journals):
                    paper['author'] = expert['name']
                    papers.append(paper)
        return papers

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        import re
        filename = re.sub(r'[<>:"/\\|？*]', '_', filename)
        return filename.strip()[:50]


# ==================== 使用示例 ====================

if __name__ == '__main__':
    surveyor = BigShotLiteratureSurvey()

    # 调研某个领域
    result = surveyor.survey("stem cell CAR-T cancer", top_n=10)

    print(f"\n{'='*60}")
    print(f"调研完成!")
    print(f"{'='*60}")
    print(f"大佬数量：{len(result)} 位")
    print(f"高分文献：{sum(len(e.get('papers', [])) for e in result)} 篇")
    print(f"\n查看笔记:")
    print(f"  ~/Documents/Obsidian Vault/06-领域大佬文献调研/")
