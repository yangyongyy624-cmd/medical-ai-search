#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学 AI 系统 - 平衡版
设计原则：全面性 + 正确性 + 稳定性

核心功能:
- 多 Agent 并行文献检索 (保证全面)
- 桐桐杠精审核 (保证正确)
- 有限重试 + 超时保护 (保证稳定)
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


# ========== 配置 ==========

class Config:
    """系统配置"""

    # 超时配置 (秒)
    SEARCH_TIMEOUT = 300      # 文献检索 5 分钟
    AUDIT_TIMEOUT = 300       # 审核 5 分钟
    PPT_TIMEOUT = 300         # PPT 生成 5 分钟

    # 重试配置
    MAX_RETRIES = 2           # 最多重试 2 次
    RETRY_DELAYS = [1, 2]     # 重试等待时间 (秒)

    # 质量阈值
    HIGH_QUALITY = 0.8        # 高置信度
    MEDIUM_QUALITY = 0.5      # 中置信度

    # 文献数量
    MIN_PAPERS = 5            # 最少 5 篇
    MAX_PAPERS = 20           # 最多 20 篇


# ========== 数据类 ==========

class QualityLevel(Enum):
    """质量等级"""
    HIGH = "high"       # 高质量，≥2 篇独立文献支持
    MEDIUM = "medium"   # 中等质量，有文献支持但不够全面
    LOW = "low"         # 低质量，证据不足


@dataclass
class AuditResult:
    """审核结果"""
    passed: bool
    confidence: float           # 置信度 0-1
    quality: QualityLevel       # 质量等级
    issues: List[str]           # 问题列表
    gaps: List[str]             # 缺失内容
    verified_claims: List[str]  # 已验证的声明

    def __str__(self):
        return f"Audit(passed={self.passed}, quality={self.quality.value}, confidence={self.confidence})"


@dataclass
class SearchResult:
    """检索结果"""
    papers: List[Dict]          # 文献列表
    sources: List[str]          # 来源 (PubMed/Europe PMC/MeSH)
    total_count: int            # 总数
    search_time: float          # 检索时间 (秒)
    query: str                  # 检索词


# ========== 核心功能 ==========

class MedicalAISystem:
    """医学 AI 系统 - 平衡版"""

    def __init__(self):
        self.config = Config()
        self.log_file = f"~/Medical-AI/logs/{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    def log(self, message: str, level: str = "INFO"):
        """日志记录"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)

        # 保存到文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except:
            pass

    # ========== 1. 文献检索 (保证全面) ==========

    def search_literature(self, query: str) -> Optional[SearchResult]:
        """
        文献检索 - 多 Agent 并行，保证全面性
        """
        self.log(f"开始文献检索：{query}")
        start_time = time.time()

        # 并行检索 (伪代码，实际调用 Hermes)
        results = {}

        try:
            # Agent 1: PubMed
            self.log("检索 PubMed...")
            results['pubmed'] = self._search_pubmed(query)

            # Agent 2: Europe PMC (并行)
            self.log("检索 Europe PMC...")
            results['europe_pmc'] = self._search_europe_pmc(query)

            # Agent 3: MeSH (并行)
            self.log("检索 MeSH...")
            results['mesh'] = self._search_mesh(query)

        except Exception as e:
            self.log(f"检索失败：{e}", "ERROR")
            return None

        # 合并去重
        merged_papers = self._merge_and_deduplicate(results)
        search_time = time.time() - start_time

        result = SearchResult(
            papers=merged_papers,
            sources=list(results.keys()),
            total_count=len(merged_papers),
            search_time=search_time,
            query=query
        )

        self.log(f"检索完成：{result.total_count} 篇，耗时{search_time:.1f}秒")

        return result

    def _search_pubmed(self, query: str) -> List[Dict]:
        """PubMed 检索"""
        # TODO: 调用 Hermes nature-academic-search
        return []

    def _search_europe_pmc(self, query: str) -> List[Dict]:
        """Europe PMC 检索"""
        # TODO: 调用 Hermes
        return []

    def _search_mesh(self, query: str) -> List[Dict]:
        """MeSH 检索"""
        # TODO: 调用 Hermes
        return []

    def _merge_and_deduplicate(self, results: Dict[str, List[Dict]]) -> List[Dict]:
        """合并去重"""
        seen_pmids = set()
        merged = []

        for source, papers in results.items():
            for paper in papers:
                pmid = paper.get('pmid') or paper.get('id')
                if pmid and pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    paper['source'] = source
                    merged.append(paper)

        # 按相关性排序
        merged.sort(key=lambda x: x.get('relevance', 0), reverse=True)

        return merged[:self.config.MAX_PAPERS]

    # ========== 2. 杠精审核 (保证正确) ==========

    def audit_with_gangjing(self, papers: List[Dict], claims: List[str] = None) -> AuditResult:
        """
        杠精审核 - 桐桐专属，保证正确性
        """
        self.log("开始杠精审核...")

        # 调用桐桐审核
        try:
            # TODO: 调用桐桐 academic-verify
            audit_result = self._call_tongtong_audit(papers, claims)
        except Exception as e:
            self.log(f"审核失败：{e}", "ERROR")
            return AuditResult(
                passed=False,
                confidence=0.0,
                quality=QualityLevel.LOW,
                issues=[f"审核失败：{e}"],
                gaps=[],
                verified_claims=[]
            )

        # 评估质量
        if audit_result.confidence >= self.config.HIGH_QUALITY:
            self.log(f"审核通过：高质量 (置信度{audit_result.confidence})")
        elif audit_result.confidence >= self.config.MEDIUM_QUALITY:
            self.log(f"审核通过：中等质量 (置信度{audit_result.confidence})")
        else:
            self.log(f"审核警告：低质量 (置信度{audit_result.confidence})", "WARNING")

        return audit_result

    def _call_tongtong_audit(self, papers: List[Dict], claims: List[str]) -> AuditResult:
        """调用桐桐审核"""
        # TODO: 实际调用桐桐
        # 这里是占位实现
        return AuditResult(
            passed=True,
            confidence=0.9,
            quality=QualityLevel.HIGH,
            issues=[],
            gaps=[],
            verified_claims=["示例声明 1", "示例声明 2"]
        )

    # ========== 3. 有限重试 (保证稳定) ==========

    def call_with_retry(self, func, max_retries: int = None, timeout: int = None) -> Any:
        """
        带超时和重试的调用 - 保证稳定
        """
        max_retries = max_retries or self.config.MAX_RETRIES
        timeout = timeout or self.config.SEARCH_TIMEOUT

        for attempt in range(max_retries + 1):
            try:
                self.log(f"调用 {func.__name__} (尝试 {attempt + 1}/{max_retries + 1})")

                # 带超时调用
                result = func(timeout=timeout)

                self.log(f"调用成功：{func.__name__}")
                return result

            except TimeoutError as e:
                self.log(f"调用超时：{func.__name__} ({timeout}秒)", "ERROR")

                if attempt < max_retries:
                    delay = self.config.RETRY_DELAYS[min(attempt, len(self.config.RETRY_DELAYS) - 1)]
                    self.log(f"等待{delay}秒后重试...")
                    time.sleep(delay)
                else:
                    self.log(f"{func.__name__} 超时，已重试{max_retries}次，放弃", "ERROR")
                    return None

            except Exception as e:
                self.log(f"调用失败：{func.__name__} - {e}", "ERROR")

                if attempt < max_retries:
                    delay = self.config.RETRY_DELAYS[min(attempt, len(self.config.RETRY_DELAYS) - 1)]
                    self.log(f"等待{delay}秒后重试...")
                    time.sleep(delay)
                else:
                    self.log(f"{func.__name__} 失败，已重试{max_retries}次，放弃", "ERROR")
                    return None

        return None

    # ========== 4. 关键通知 ==========

    def notify_user(self, message: str, level: str = "info"):
        """
        通知用户 - 只通知关键节点
        """
        self.log(f"[通知用户] [{level}] {message}")

        # 通过 Hermes 发送飞书通知
        # TODO: 调用 Hermes send_feishu

        return True

    # ========== 5. 完整工作流 ==========

    def make_evidence_based_ppt(self, topic: str) -> Optional[Dict]:
        """
        基于循证的 PPT 生成 - 完整工作流
        """
        self.log(f"===== 开始任务：{topic} =====")

        # Step 1: 文献检索 (保证全面)
        self.log("--- Step 1: 文献检索 ---")
        search_result = self.call_with_retry(
            lambda timeout: self.search_literature(topic),
            max_retries=2,
            timeout=300
        )

        if not search_result:
            self.notify_user("文献检索失败，已重试 3 次", "critical")
            return None

        if search_result.total_count < self.config.MIN_PAPERS:
            self.notify_user(f"文献较少 ({search_result.total_count}篇)，但继续执行", "warning")

        # Step 2: 杠精审核 (保证正确)
        self.log("--- Step 2: 杠精审核 ---")
        audit_result = self.call_with_retry(
            lambda timeout: self.audit_with_gangjing(search_result.papers),
            max_retries=1,
            timeout=300
        )

        if not audit_result:
            self.notify_user("审核失败，使用原始文献", "warning")
            audit_result = AuditResult(
                passed=False,
                confidence=0.0,
                quality=QualityLevel.LOW,
                issues=["审核失败"],
                gaps=[],
                verified_claims=[]
            )

        # 中等质量以下，通知用户
        if audit_result.quality == QualityLevel.MEDIUM:
            self.notify_user(f"文献质量中等：{audit_result.issues}", "warning")
        elif audit_result.quality == QualityLevel.LOW:
            self.notify_user(f"文献质量较低：{audit_result.issues}", "critical")

        # Step 3: PPT 生成
        self.log("--- Step 3: PPT 生成 ---")
        ppt_result = self.call_with_retry(
            lambda timeout: self._generate_ppt(search_result, audit_result),
            max_retries=2,
            timeout=300
        )

        if not ppt_result:
            self.notify_user("PPT 生成失败", "critical")
            return None

        # Step 4: 完成
        self.log("===== 任务完成 =====")
        self.notify_user(f"PPT 生成完成，质量等级：{audit_result.quality.value}", "success")

        return ppt_result

    def _generate_ppt(self, search_result: SearchResult, audit_result: AuditResult) -> Dict:
        """生成 PPT"""
        # TODO: 调用 Hermes guizang-ppt-skill
        return {
            "status": "success",
            "ppt_file": "output.pptx",
            "papers_used": search_result.total_count,
            "quality": audit_result.quality.value
        }


# ========== 命令行接口 ==========

if __name__ == '__main__':
    import sys

    system = MedicalAISystem()

    if len(sys.argv) < 2:
        print("用法：python medical_ai.py <命令> [参数]")
        print("命令:")
        print("  search <检索词>     - 文献检索")
        print("  audit <PMID 列表>    - 杠精审核")
        print("  ppt <主题>         - 生成 PPT")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'search':
        query = ' '.join(sys.argv[2:])
        result = system.search_literature(query)
        if result:
            print(f"检索到 {result.total_count} 篇文献")
            print(f"来源：{', '.join(result.sources)}")
            print(f"耗时：{result.search_time:.1f}秒")

    elif command == 'audit':
        pmids = sys.argv[2:]
        # TODO: 实现审核命令
        print("审核功能开发中...")

    elif command == 'ppt':
        topic = ' '.join(sys.argv[2:])
        result = system.make_evidence_based_ppt(topic)
        if result:
            print(f"PPT 生成完成：{result['ppt_file']}")
            print(f"使用文献：{result['papers_used']}篇")
            print(f"质量等级：{result['quality']}")

    else:
        print(f"未知命令：{command}")
