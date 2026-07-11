#!/usr/bin/env python3
"""
医学文献调研与报告生成系统 - 一键执行

功能:
1. 查阅文献 (找到行业大佬 + 检索高分文献)
2. 生成文献阅读报告 (自动总结 + 分类)
3. 生成讲课 PPT (基于调研结果)

输入：医学领域名称
输出：文献列表 + 阅读报告 + 讲课 PPT

作者：宵宵
日期：2026-07-12
"""

import sys
import os
from datetime import datetime


def main(topic: str, output_format: str = "all"):
    """
    一键执行完整工作流

    Args:
        topic: 研究领域
        output_format: 输出格式 (all/report/ppt)
    """
    print(f"\n{'='*60}")
    print(f"医学文献调研与报告生成系统 v1.0")
    print(f"研究主题：{topic}")
    print(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    # ========== 功能 1: 查阅文献 ==========
    print(f"\n【功能 1】查阅文献...")
    print(f"-"*60)

    try:
        from big_shot_literature_survey import BigShotLiteratureSurvey

        surveyor = BigShotLiteratureSurvey()
        result = surveyor.survey(topic, top_n=10)

        print(f"\n✅ 文献调研完成!")
        print(f"   找到大佬：{len(result)} 位")
        print(f"   高分文献：{sum(len(e.get('papers', [])) for e in result)} 篇")
        print(f"   Obsidian 笔记：已生成")

    except Exception as e:
        print(f" 文献调研失败：{e}")
        result = None

    # ========== 功能 2: 生成阅读报告 ==========
    if output_format in ["all", "report"] and result:
        print(f"\n【功能 2】生成文献阅读报告...")
        print(f"-"*60)

        try:
            from reading_report_generator import ReadingReportGenerator

            # 收集所有文献
            all_papers = []
            for expert in result:
                all_papers.extend(expert.get('papers', []))

            generator = ReadingReportGenerator()
            report_file = generator.generate_report(topic, all_papers)

            print(f"\n✅ 阅读报告生成完成!")
            print(f"   文件：{report_file}")

        except Exception as e:
            print(f"❌ 阅读报告生成失败：{e}")

    # ========== 功能 3: 生成讲课 PPT ==========
    if output_format in ["all", "ppt"] and result:
        print(f"\n【功能 3】生成讲课 PPT...")
        print(f"-"*60)

        try:
            from ppt_generator import PPTGenerator, PPTConfig

            # 收集所有文献
            all_papers = []
            for expert in result:
                all_papers.extend(expert.get('papers', []))

            generator = PPTGenerator()
            ppt_result = generator.generate(
                topic=topic,
                papers=all_papers,
                config=PPTConfig(
                    style='academic',
                    include_figures=False,
                    include_references=True
                )
            )

            print(f"\n✅ 讲课 PPT 生成完成!")
            print(f"   文件：{ppt_result.get('ppt_file', 'N/A')}")
            print(f"   幻灯片数：{ppt_result.get('slide_count', 'N/A')}")

        except Exception as e:
            print(f"❌ PPT 生成失败：{e}")

    # ========== 总结 ==========
    print(f"\n{'='*60}")
    print(f"执行完成!")
    print(f"{'='*60}")

    if result:
        print(f"\n输出文件:")
        print(f"  1. 文献调研笔记：~/Documents/Obsidian Vault/06-领域大佬文献调研/")
        print(f"  2. 阅读报告：~/Documents/Obsidian Vault/08-文献阅读报告/")
        print(f"  3. 讲课 PPT: ~/Documents/Obsidian Vault/09-讲课 PPT/")
    else:
        print(f"\n️ 部分功能执行失败，请检查错误信息")

    print(f"\n{'='*60}")


# ==================== 命令行入口 ====================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""
医学文献调研与报告生成系统

用法:
    python3 medical_literature_workflow.py <领域名称> [输出格式]

参数:
    领域名称：如 "rTMS depression", "stem cell CAR-T"
    输出格式：all (默认), report (仅报告), ppt (仅 PPT)

示例:
    python3 medical_literature_workflow.py "rTMS 治疗抑郁"
    python3 medical_literature_workflow.py "stem cell CAR-T" report
    python3 medical_literature_workflow.py "esketamine" ppt
""")
        sys.exit(1)

    topic = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "all"

    main(topic, output_format)
