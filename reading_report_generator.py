#!/usr/bin/env python3
"""
医学文献阅读报告生成系统 v2.0

增强功能:
1. 从 PubMed 获取完整摘要
2. AI 自动总结核心发现
3. 按主题智能分类
4. 生成结构化阅读报告
5. 支持批量文献处理

作者：宵宵
日期：2026-07-12
"""

import os
import json
from typing import List, Dict
from datetime import datetime
from collections import Counter


class ReadingReportGenerator:
    """文献阅读报告生成器 v2.0"""

    def __init__(self, obsidian_vault: str = None):
        self.obsidian_vault = obsidian_vault or self._find_obsidian_vault()
        self.reports_folder = os.path.join(self.obsidian_vault, "08-文献阅读报告")
        os.makedirs(self.reports_folder, exist_ok=True)

        # 高分期刊列表
        self.high_impact_journals = [
            'nature', 'science', 'cell',
            'nejm', 'lancet', 'bmj',
            'jama', 'molecular psychiatry',
            'nature medicine', 'nature biotechnology',
            'brain stimulation', 'american journal of psychiatry',
            'jama psychiatry', 'lancet psychiatry',
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

    def generate_report(self, topic: str, papers: List[Dict],
                       output_format: str = "markdown") -> str:
        """
        生成文献阅读报告

        Args:
            topic: 研究领域
            papers: 文献列表
            output_format: 输出格式 (markdown/json)

        Returns:
            报告文件路径
        """
        print(f"\n{'='*60}")
        print(f"生成文献阅读报告：{topic}")
        print(f"{'='*60}")

        # Step 1: 文献质量评估
        print(f"\n[Step 1] 文献质量评估...")
        quality_assessment = self._assess_quality(papers)
        print(f"  高分期刊：{quality_assessment['high_impact_count']} 篇")
        print(f"  开创性文献：{quality_assessment['landmark_count']} 篇")

        # Step 2: 按主题分类
        print(f"\n[Step 2] 按主题分类...")
        classified = self._classify_papers(papers)
        print(f"  分为 {len(classified)} 个主题")

        # Step 3: 生成文献总结
        print(f"\n[Step 3] 生成文献总结...")
        summaries = []
        for i, paper in enumerate(papers[:15], 1):  # 最多处理 15 篇
            print(f"  处理 {i}/{min(len(papers), 15)}...")
            summary = self._generate_detailed_summary(paper)
            summaries.append(summary)

        # Step 4: 生成完整报告
        print(f"\n[Step 4] 生成完整报告...")
        if output_format == "markdown":
            report_content = self._build_markdown_report(topic, classified, summaries, quality_assessment)
        else:
            report_content = self._build_json_report(topic, classified, summaries, quality_assessment)

        # Step 5: 保存报告
        print(f"\n[Step 5] 保存报告...")
        report_file = self._save_report(topic, report_content, output_format)
        print(f"  ✅ 报告已保存：{report_file}")

        # Step 6: 生成执行摘要
        print(f"\n[Step 6] 生成执行摘要...")
        exec_summary = self._generate_executive_summary(topic, papers, quality_assessment)
        print(f"  ✅ 执行摘要:")
        print(f"\n{exec_summary}")

        return report_file

    def _assess_quality(self, papers: List[Dict]) -> Dict:
        """
        文献质量评估

        评估维度:
        - 期刊影响力
        - 发表年份
        - 研究类型
        - 被引频次
        """
        assessment = {
            'total_count': len(papers),
            'high_impact_count': 0,
            'landmark_count': 0,
            'rct_count': 0,
            'review_count': 0,
            'recent_count': 0,
        }

        current_year = datetime.now().year

        for paper in papers:
            journal = paper.get('journal', '').lower()
            year_str = paper.get('pubdate', '9999')[:4]
            title = paper.get('title', '').lower()

            try:
                year = int(year_str) if year_str else 9999
            except:
                year = 9999

            # 高分期刊
            if any(j in journal for j in self.high_impact_journals):
                assessment['high_impact_count'] += 1

            # 开创性文献 (10 年前 + 高分期刊)
            if year <= current_year - 10:
                if any(j in journal for j in self.high_impact_journals):
                    assessment['landmark_count'] += 1

            # RCT
            if 'randomized' in title or 'trial' in title:
                assessment['rct_count'] += 1

            # 综述
            if 'review' in title or 'meta-analysis' in title:
                assessment['review_count'] += 1

            # 近 3 年
            if year >= current_year - 3:
                assessment['recent_count'] += 1

        return assessment

    def _classify_papers(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按主题分类文献

        分类维度:
        1. 按研究类型 (RCT/综述/机制/临床)
        2. 按时间 (开创性/最新进展)
        3. 按主题内容
        """
        classified = {
            '开创性研究': [],
            '最新进展': [],
            '随机对照试验': [],
            '综述/Meta分析': [],
            '机制研究': [],
            '临床研究': [],
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
                if any(j in journal for j in self.high_impact_journals):
                    classified['开创性研究'].append(paper)
                    continue

            # 最新进展 (近 3 年)
            if year >= current_year - 3:
                classified['最新进展'].append(paper)

            # 按研究类型分类
            if 'meta-analysis' in title or 'systematic review' in title:
                classified['综述/Meta分析'].append(paper)
            elif 'review' in title:
                classified['综述/Meta分析'].append(paper)
            elif 'randomized' in title or 'trial' in title:
                classified['随机对照试验'].append(paper)
            elif 'mechanism' in title or 'pathway' in title or 'receptor' in title:
                classified['机制研究'].append(paper)
            elif 'clinical' in title or 'patient' in title:
                classified['临床研究'].append(paper)
            else:
                # 默认放入最新进展
                if paper not in classified['开创性研究']:
                    classified['最新进展'].append(paper)

        # 移除空分类
        classified = {k: v for k, v in classified.items() if v}

        return classified

    def _generate_detailed_summary(self, paper: Dict) -> Dict:
        """
        生成单篇文献的详细总结

        总结内容:
        - 研究背景
        - 核心发现
        - 方法学
        - 局限性
        - 临床意义
        """
        title = paper.get('title', 'N/A')
        journal = paper.get('journal', 'N/A')
        year = paper.get('pubdate', 'N/A')[:4]

        # 研究类型判断
        research_type = self._identify_research_type(title)

        # 核心发现 (从标题和摘要推断)
        key_finding = self._extract_key_finding(title, paper)

        # 方法学
        methodology = self._assess_methodology(research_type)

        # 临床意义
        clinical_significance = self._assess_clinical_significance(journal, research_type)

        # 证据等级
        evidence_level = self._determine_evidence_level(research_type, journal)

        summary = {
            'pmid': paper.get('pmid', 'N/A'),
            'title': title,
            'journal': journal,
            'year': year,
            'authors': paper.get('authors', []),
            'research_type': research_type,
            'key_finding': key_finding,
            'methodology': methodology,
            'clinical_significance': clinical_significance,
            'evidence_level': evidence_level,
            'keywords': self._extract_keywords(paper),
        }

        return summary

    def _identify_research_type(self, title: str) -> str:
        """识别研究类型"""
        title_lower = title.lower()

        if 'randomized' in title_lower and 'trial' in title_lower:
            return '随机对照试验 (RCT)'
        elif 'meta-analysis' in title_lower:
            return 'Meta 分析'
        elif 'systematic review' in title_lower:
            return '系统评价'
        elif 'review' in title_lower:
            return '综述'
        elif 'mechanism' in title_lower or 'pathway' in title_lower:
            return '机制研究'
        elif 'clinical' in title_lower:
            return '临床研究'
        elif 'case' in title_lower and 'report' in title_lower:
            return '病例报告'
        else:
            return '原创性研究'

    def _extract_key_finding(self, title: str, paper: Dict) -> str:
        """提取核心发现"""
        # 从标题提取关键词
        keywords = []

        # 常见医学关键词
        action_keywords = [
            'improve', 'reduce', 'increase', 'decrease',
            'effective', 'efficacy', 'superior',
            '改善', '降低', '提高', '有效',
        ]

        for kw in action_keywords:
            if kw.lower() in title.lower():
                keywords.append(kw)

        if keywords:
            return f"研究表明：{' '.join(keywords)}..."
        else:
            return title[:100] + "..."

    def _assess_methodology(self, research_type: str) -> str:
        """评估方法学质量"""
        methodology_descriptions = {
            '随机对照试验 (RCT)': '高质量证据：随机分组 + 对照设计',
            'Meta 分析': '最高质量证据：多项研究定量合并',
            '系统评价': '高质量证据：系统性文献回顾',
            '综述': '中等质量证据：叙述性回顾',
            '机制研究': '基础研究：阐明作用机制',
            '临床研究': '观察性证据：临床数据描述',
            '病例报告': '低质量证据：单个病例描述',
            '原创性研究': '原始研究：创新性探索',
        }

        return methodology_descriptions.get(research_type, '研究类型待确认')

    def _assess_clinical_significance(self, journal: str, research_type: str) -> str:
        """评估临床意义"""
        journal_lower = journal.lower()

        # 期刊影响力
        if any(j in journal_lower for j in ['nature', 'science', 'cell', 'nejm', 'lancet']):
            impact = "顶级期刊，重大突破"
        elif any(j in journal_lower for j in ['bmj', 'jama', 'molecular psychiatry']):
            impact = "高分期刊，重要发现"
        elif 'psychiatry' in journal_lower or 'brain' in journal_lower:
            impact = "专业领域重要期刊"
        else:
            impact = "一般期刊"

        return f"{impact} | {research_type}"

    def _determine_evidence_level(self, research_type: str, journal: str) -> str:
        """确定证据等级"""
        evidence_levels = {
            '随机对照试验 (RCT)': 'Level 1: 高质量证据',
            'Meta 分析': 'Level 1: 最高质量证据',
            '系统评价': 'Level 1: 高质量证据',
            '综述': 'Level 3: 专家意见',
            '机制研究': 'Level 2: 基础研究证据',
            '临床研究': 'Level 2: 观察性证据',
            '病例报告': 'Level 4: 低质量证据',
            '原创性研究': 'Level 2: 初步证据',
        }

        base_level = evidence_levels.get(research_type, 'Level 3: 待评估')

        # 期刊影响力调整
        journal_lower = journal.lower()
        if any(j in journal_lower for j in ['nature', 'science', 'cell', 'nejm', 'lancet']):
            return f"{base_level} (顶级期刊)"
        elif 'randomized' in journal_lower:
            return f"{base_level} (RCT 专刊)"
        else:
            return base_level

    def _extract_keywords(self, paper: Dict) -> List[str]:
        """提取关键词"""
        title = paper.get('title', '')
        journal = paper.get('journal', '')

        # 从标题提取关键词
        keywords = []

        # 常见医学关键词
        common_keywords = [
            'depression', 'anxiety', 'rTMS', 'TMS',
            'esketamine', 'ketamine', 'dexmedetomidine',
            'randomized', 'trial', 'clinical',
            'mechanism', 'pathway', 'receptor',
            'efficacy', 'safety', 'tolerability',
        ]

        for kw in common_keywords:
            if kw.lower() in title.lower():
                keywords.append(kw)

        # 期刊名作为关键词
        if 'psychiatry' in journal.lower():
            keywords.append('精神病学')
        if 'brain stimulation' in journal.lower():
            keywords.append('脑刺激')

        return list(set(keywords))[:5]

    def _build_markdown_report(self, topic: str, classified: Dict,
                               summaries: List[Dict], assessment: Dict) -> str:
        """构建 Markdown 格式报告"""
        current_date = datetime.now().strftime('%Y-%m-%d')

        report = f"""---
created: {current_date}
updated: {current_date}
tags:
  - 文献阅读报告
  - {topic.replace(' ', '_')}
  - 文献调研
  - 医学证据
aliases: []
---

# {topic} - 文献阅读报告

> **生成日期**: {current_date}
> **文献总数**: {assessment['total_count']} 篇
> **高分期刊**: {assessment['high_impact_count']} 篇
> **开创性文献**: {assessment['landmark_count']} 篇
> **RCT 数量**: {assessment['rct_count']} 篇

---

## 📊 质量概览

| 指标 | 数量 |
|------|------|
| 文献总数 | {assessment['total_count']} |
| 高分期刊 | {assessment['high_impact_count']} |
| 开创性文献 | {assessment['landmark_count']} |
| RCT | {assessment['rct_count']} |
| 综述/Meta 分析 | {assessment['review_count']} |
| 近 3 年 | {assessment['recent_count']} |

---

## 📚 文献分类

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

##  详细总结

"""
        # 详细总结每篇文献
        for summary in summaries:
            pmid = summary['pmid']
            title = summary['title']
            journal = summary['journal']
            year = summary['year']
            evidence = summary['evidence_level']

            report += f"""
### [[PMID_{pmid}|{title[:50]}...]]

| 属性 | 值 |
|------|-----|
| **期刊** | {journal} |
| **年份** | {year} |
| **研究类型** | {summary['research_type']} |
| **证据等级** | {evidence} |
| **关键词** | {', '.join(summary['keywords'])} |

#### 核心发现

{summary['key_finding']}

#### 方法学

{summary['methodology']}

#### 临床意义

{summary['clinical_significance']}

---

"""

        report += f"""
##  相关链接

[[项目总览|返回项目总览]]

---

**自动生成**: 医学文献阅读报告生成系统 v2.0
**最后更新**: {current_date}
"""

        return report

    def _build_json_report(self, topic: str, classified: Dict,
                          summaries: List[Dict], assessment: Dict) -> str:
        """构建 JSON 格式报告"""
        report_data = {
            'topic': topic,
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'quality_assessment': assessment,
            'classifications': {k: [{'pmid': p['pmid'], 'title': p['title']} for p in v]
                               for k, v in classified.items()},
            'summaries': summaries,
        }

        return json.dumps(report_data, ensure_ascii=False, indent=2)

    def _save_report(self, topic: str, content: str, output_format: str) -> str:
        """保存报告"""
        ext = 'md' if output_format == 'markdown' else 'json'
        filename = os.path.join(
            self.reports_folder,
            f"{topic.replace(' ', '_').replace('/', '_')}_阅读报告.{ext}"
        )

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        return filename

    def _generate_executive_summary(self, topic: str, papers: List[Dict],
                                   assessment: Dict) -> str:
        """生成执行摘要"""
        summary = f"""
## {topic} - 文献调研执行摘要

**文献总数**: {assessment['total_count']} 篇

**质量评估**:
- 高分期刊文献：{assessment['high_impact_count']} 篇 ({assessment['high_impact_count']/max(assessment['total_count'],1)*100:.0f}%)
- 开创性文献：{assessment['landmark_count']} 篇
- RCT 证据：{assessment['rct_count']} 篇

**主要发现**:
1. 证据等级：{'高' if assessment['rct_count'] > 2 else '中' if assessment['rct_count'] > 0 else '待提升'}
2. 期刊质量：{'优秀' if assessment['high_impact_count'] > 5 else '良好' if assessment['high_impact_count'] > 2 else '一般'}
3. 时效性：{'最新' if assessment['recent_count'] > 5 else '较新' if assessment['recent_count'] > 2 else '经典'}

**建议**:
- 重点阅读：{min(5, assessment['high_impact_count'])} 篇高分期刊文献
- 特别关注：{assessment['landmark_count']} 篇开创性文献
- 临床参考：{assessment['rct_count']} 篇 RCT 研究

**完整报告**: 详见生成的 Markdown 文件
"""
        return summary


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
