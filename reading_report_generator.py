#!/usr/bin/env python3
"""
医学文献阅读报告生成系统

功能：
1. 自动总结文献核心发现
2. 按主题分类文献
3. 生成结构化阅读报告
4. 输出到 Obsidian

作者：宵宵
日期：2026-07-12
"""

import os
from typing import List, Dict
from datetime import datetime


class ReadingReportGenerator:
    """文献阅读报告生成器"""

    def __init__(self, obsidian_vault: str = None):
        self.obsidian_vault = obsidian_vault or self._find_obsidian_vault()
        self.reports_folder = os.path.join(self.obsidian_vault, "08-文献阅读报告")
        os.makedirs(self.reports_folder, exist_ok=True)

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

    def generate_report(self, topic: str, papers: List[Dict]) -> str:
        """
        生成文献阅读报告

        Args:
            topic: 研究领域
            papers: 文献列表

        Returns:
            报告文件路径
        """
        print(f"\n{'='*60}")
        print(f"生成文献阅读报告：{topic}")
        print(f"{'='*60}")

        # Step 1: 按主题分类
        print(f"\n[Step 1] 按主题分类文献...")
        classified = self._classify_papers(papers)
        print(f"  分为 {len(classified)} 个主题")

        # Step 2: 生成每篇文献的总结
        print(f"\n[Step 2] 生成文献总结...")
        summarized = self._summarize_papers(papers)

        # Step 3: 生成完整报告
        print(f"\n[Step 3] 生成完整报告...")
        report_content = self._build_report(topic, classified, summarized)

        # Step 4: 保存到 Obsidian
        print(f"\n[Step 4] 保存到 Obsidian...")
        report_file = self._save_report(topic, report_content)
        print(f"  ✅ 报告已保存：{report_file}")

        return report_file

    def _classify_papers(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按主题分类文献

        分类维度:
        - 开创性研究 (年份早 + 高被引)
        - 最新进展 (近 3 年)
        - 临床研究
        - 机制研究
        - 综述/Meta分析
        """
        classified = {
            '开创性研究': [],
            '最新进展': [],
            '临床研究': [],
            '机制研究': [],
            '综述/Meta分析': [],
        }

        current_year = datetime.now().year

        for paper in papers:
            title = paper.get('title', '').lower()
            journal = paper.get('journal', '').lower()
            year_str = paper.get('pubdate', '9999')[:4]

            try:
                year = int(year_str) if year_str else 9999
            except:
                year = 9999

            # 开创性研究 (10 年前 + 高分期刊)
            if year <= current_year - 10:
                if any(j in journal for j in ['nature', 'science', 'cell', 'nejm', 'lancet']):
                    classified['开创性研究'].append(paper)
                    continue

            # 最新进展 (近 3 年)
            if year >= current_year - 3:
                classified['最新进展'].append(paper)
                continue

            # 按类型分类
            if 'review' in title or 'meta-analysis' in title:
                classified['综述/Meta分析'].append(paper)
            elif 'clinical' in title or 'trial' in title or 'randomized' in title:
                classified['临床研究'].append(paper)
            elif 'mechanism' in title or 'pathway' in title or 'receptor' in title:
                classified['机制研究'].append(paper)
            else:
                # 默认放入最新进展
                classified['最新进展'].append(paper)

        # 移除空分类
        classified = {k: v for k, v in classified.items() if v}

        return classified

    def _summarize_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        生成每篇文献的总结

        总结内容:
        - 研究背景
        - 核心发现
        - 方法学
        - 局限性
        - 临床意义
        """
        summarized = []

        for paper in papers:
            summary = {
                'pmid': paper.get('pmid', 'N/A'),
                'title': paper.get('title', 'N/A'),
                'journal': paper.get('journal', 'N/A'),
                'year': paper.get('pubdate', 'N/A')[:4],
                'authors': paper.get('authors', []),
                'summary': self._generate_paper_summary(paper),
                'keywords': self._extract_keywords(paper),
                'citation_count': paper.get('citation_count', 0),
            }
            summarized.append(summary)

        return summarized

    def _generate_paper_summary(self, paper: Dict) -> str:
        """
        生成单篇文献总结

        策略:
        1. 从标题提取研究类型
        2. 从期刊推断影响力
        3. 从年份推断是新进展还是经典研究
        """
        title = paper.get('title', 'N/A')
        journal = paper.get('journal', 'N/A')
        year = paper.get('pubdate', 'N/A')[:4]

        # 研究类型判断
        research_type = self._identify_research_type(title)

        # 核心发现 (从标题推断)
        key_finding = self._extract_key_finding(title)

        # 临床意义
        clinical_significance = self._assess_clinical_significance(journal, research_type)

        summary = f"""
**研究类型**: {research_type}

**核心发现**: {key_finding}

**临床意义**: {clinical_significance}
"""
        return summary

    def _identify_research_type(self, title: str) -> str:
        """识别研究类型"""
        title_lower = title.lower()

        if 'randomized' in title_lower or 'trial' in title_lower:
            return '随机对照试验 (RCT)'
        elif 'meta-analysis' in title_lower or 'systematic review' in title_lower:
            return 'Meta 分析/系统评价'
        elif 'review' in title_lower:
            return '综述'
        elif 'mechanism' in title_lower or 'pathway' in title_lower:
            return '机制研究'
        elif 'clinical' in title_lower:
            return '临床研究'
        elif 'case' in title_lower:
            return '病例报告'
        else:
            return '原创性研究'

    def _extract_key_finding(self, title: str) -> str:
        """从标题提取核心发现"""
        # 简化实现：返回标题本身
        # 实际应该调用 AI 总结
        return title[:100] + "..."

    def _assess_clinical_significance(self, journal: str, research_type: str) -> str:
        """评估临床意义"""
        journal_lower = journal.lower()

        # 高分期刊
        high_impact = ['nature', 'science', 'cell', 'nejm', 'lancet', 'bmj']
        if any(j in journal_lower for j in high_impact):
            impact = "高影响力"
        elif 'psychiatry' in journal_lower or 'brain' in journal_lower:
            impact = "专业领域重要"
        else:
            impact = "一般"

        # 研究类型权重
        type_weight = {
            '随机对照试验 (RCT)': '高',
            'Meta 分析/系统评价': '高',
            '综述': '中',
            '机制研究': '中',
            '临床研究': '中',
            '病例报告': '低',
            '原创性研究': '中',
        }

        evidence_level = type_weight.get(research_type, '中')

        return f"证据等级：{evidence_level} | 期刊影响力：{impact}"

    def _extract_keywords(self, paper: Dict) -> List[str]:
        """提取关键词"""
        title = paper.get('title', '')

        # 从标题提取关键词 (简化实现)
        keywords = []

        # 常见医学关键词
        common_keywords = [
            'depression', 'anxiety', 'rTMS', 'TMS',
            'esketamine', 'ketamine', 'dexmedetomidine',
            'randomized', 'trial', 'clinical',
            'mechanism', 'pathway', 'receptor',
        ]

        for kw in common_keywords:
            if kw.lower() in title.lower():
                keywords.append(kw)

        return keywords[:5]

    def _build_report(self, topic: str, classified: Dict, summarized: List) -> str:
        """构建完整报告"""
        current_date = datetime.now().strftime('%Y-%m-%d')

        report = f"""---
created: {current_date}
updated: {current_date}
tags:
  - 文献阅读报告
  - {topic.replace(' ', '_')}
  - 文献调研
aliases: []
---

# {topic} - 文献阅读报告

> **生成日期**: {current_date}
> **文献总数**: {len(summarized)} 篇
> **分类数量**: {len(classified)} 个主题

---

## 📚 文献概览

"""
        # 按分类展示
        for category, papers in classified.items():
            report += f"""
### {category} ({len(papers)} 篇)

"""
            for i, paper in enumerate(papers[:5], 1):  # 每个分类最多显示 5 篇
                pmid = paper.get('pmid', 'N/A')
                title = paper.get('title', 'N/A')[:60]
                journal = paper.get('journal', 'N/A')
                year = paper.get('pubdate', 'N/A')[:4]

                report += f"""
{i}. [[PMID_{pmid}|{title}...]]
   - **期刊**: {journal}
   - **年份**: {year}

"""

        report += """
---

## 📋 详细总结

"""
        # 详细总结每篇文献
        for summary in summarized:
            pmid = summary['pmid']
            title = summary['title']
            journal = summary['journal']
            year = summary['year']

            report += f"""
### [[PMID_{pmid}|{title[:50]}...]]

- **期刊**: {journal}
- **年份**: {year}
- **关键词**: {', '.join(summary['keywords'])}

{summary['summary']}

---

"""

        report += f"""
##  相关链接

[[项目总览|返回项目总览]]

---

**自动生成**: 医学文献阅读报告生成系统 v1.0
**最后更新**: {current_date}
"""

        return report

    def _save_report(self, topic: str, content: str) -> str:
        """保存报告"""
        filename = os.path.join(
            self.reports_folder,
            f"{topic.replace(' ', '_').replace('/', '_')}_阅读报告.md"
        )

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        return filename


# ==================== 使用示例 ====================

if __name__ == '__main__':
    # 示例数据
    sample_papers = [
        {
            'pmid': '32252538',
            'title': 'Stanford Accelerated Intelligent Neuromodulation Therapy for Treatment-Resistant Depression',
            'journal': 'American Journal of Psychiatry',
            'pubdate': '2020',
            'authors': ['Cole EJ', 'Williams NR'],
        },
        {
            'pmid': '34711062',
            'title': 'Stanford Neuromodulation Therapy (SNT): A Double-Blind Randomized Controlled Trial',
            'journal': 'American Journal of Psychiatry',
            'pubdate': '2022',
            'authors': ['Cole EJ'],
        },
    ]

    generator = ReadingReportGenerator()
    report_file = generator.generate_report("rTMS depression", sample_papers)

    print(f"\n✅ 报告生成完成!")
    print(f"   文件：{report_file}")
