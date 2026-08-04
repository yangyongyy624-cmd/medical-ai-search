# 文献检索 A2A 调度器规范

> 创建于 2026-08-04 | 验证通过 | 铁律级别

## 核心原则

**全面 > 速度** — 用户要的是全面、准确、内容丰富，不是快。

## 为什么必须用 A2A？

| 方式 | 覆盖 API | 文献量 | 高被引覆盖 |
|------|---------|--------|-----------|
| **A2A 调度器（5 路并行）** | OpenAlex + Semantic Scholar + CrossRef + Europe PMC + PubMed | 200+ 篇 | 93% |
| 自己调 PubMed MCP（1 路） | 仅 PubMed | 10-50 篇 | 大量遗漏 |

**自己调 PubMed → 丢 Semantic Scholar 正向追踪的 142 篇引用文献**
**自己调 OpenAlex → 丢 PubMed 独有的临床文献**
**选捷径 = 丢文献 = 不合格**

## A2A 调度器 5 路并行架构

| 路数 | Agent | API | 数据方向 |
|------|-------|-----|---------|
| 1 | openclaw-dandan | OpenAlex | 反向追踪（该文献引用了谁） |
| 2 | openclaw-tongtong | Europe PMC | 相关文献 |
| 3 | openclaw-cloud-xiaoxiao | CrossRef | 反向追踪（DOI 独有） |
| 4 | openclaw-xiaoxiao | Europe PMC | 相关文献 |
| 5 | 本地 pubmed-search.sh | PubMed MCP | 临床文献核心库 |

## 唯一正确方式

```bash
~/.a2a/bin/a2a-dispatcher search "关键词"
```

## 绝对禁止（NO EXCEPTIONS）

1. 禁止直接调用任何 MCP 工具做文献检索（pubmed_search_articles 等）
2. 禁止自己写 Python/Shell 脚本检索
3. 禁止自己用 curl/wget 调任何学术 API
4. 禁止以"更快"、"更简单"、"已经知道答案"为由跳过 A2A

## 标准流程

1. 从用户问题提取关键词 → 调 A2A 检索（中英文各一次）
2. 等 A2A 结果（30-60 秒）
3. 关键词覆盖不全 → 换关键词再调一次 A2A
4. 基于全部结果整理回复（标注 PMID、DOI、被引次数）

## 技术背景

- **cc-connect v1.3.2**：不支持 system_prompt 字段，规则被静默忽略
- **cc-connect v1.4.1**：支持 system_prompt，规则正确传递
- **验证结果**：Claude 严格执行 A2A 调度器，无违规调用

## 触发条件

检索、查文献、搜索论文、找文章、综述、文献报告、高分文献、核心期刊

## Skill 位置

`~/.claude/skills/literature-a2a-search/SKILL.md`

## 相关记忆

- `[[pubmed-literature-search-workflow]]` — PubMed 直接 MCP 工作流（已废弃）
- `[[feedback_literature_search]]` — 文献检索方法论
