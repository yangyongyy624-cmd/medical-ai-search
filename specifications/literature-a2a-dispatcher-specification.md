# 文献检索 A2A 调度器规范

> 创建于 2026-08-04 | 更新于 2026-08-05 | 验证通过 | 铁律级别

## 核心原则

**全面 > 速度** — 用户要的是全面、准确、内容丰富，不是快。

## 为什么必须用 A2A？

| 方式 | 覆盖 API | 文献量 | 高被引覆盖 |
|------|---------|--------|-----------|
| **A2A 调度器（5 路并行 + 迭代）** | OpenAlex + Semantic Scholar + CrossRef + Europe PMC + PubMed | 200+ 篇 | 93% |
| 自己调 PubMed MCP（1 路） | 仅 PubMed | 10-50 篇 | 大量遗漏 |

**自己调 PubMed → 丢 Semantic Scholar 正向追踪的 142 篇引用文献**
**自己调 OpenAlex → 丢 PubMed 独有的临床文献**
**选捷径 = 丢文献 = 不合格**

## A2A 调度器 5 路并行架构

| 路数 | Agent | API | 数据方向 |
|------|-------|-----|---------|
| 1 | openclaw-dandan | OpenAlex | 反向追踪（该文献引用了谁） |
| 2 | openclaw-tongtong | **Semantic Scholar** | **正向追踪（哪些文章引用了该文献，142 篇/篇）** |
| 3 | openclaw-cloud-xiaoxiao | CrossRef | 反向追踪（DOI 独有） |
| 4 | openclaw-xiaoxiao | Europe PMC | 相关文献 |
| 5 | 本地 pubmed-search.sh | **PubMed MCP（maxResults=50）** | 临床文献核心库 |

## 多轮迭代流程

```
1. 从用户问题提取关键词 → 调 A2A 检索（中英文各一次）
2. 等 A2A 结果（30-60 秒）
3. 从结果中提取高被引文献的 PMID/DOI
4. 用这些 PMID/DOI 的参考文献做第 2 轮 A2A 检索
5. 重复 3-4 步，最多 4 轮
6. 每轮合并去重
7. 基于全部结果整理回复（标注 PMID、DOI、被引次数）
8. 对于 PMC 开放获取的文献，读取全文进行交叉验证
9. 发现矛盾的观点 → 标红 🔴 并说明理由
```

## 报告规范

- **只加不删**：所有检索到的文献都保留，不做删减
- **内容完整**：全文读取越多越好，不做摘要截断
- **标红质疑**：不同观点、不确定结论、矛盾数据必须标红 🔴
- **第一性原理**：追溯原始文献，不依赖二次引用

## 唯一正确方式

```bash
~/.a2a/bin/a2a-dispatcher search "关键词"
```

## 绝对禁止（NO EXCEPTIONS）

1. 禁止直接调用任何 MCP 工具做文献检索（pubmed_search_articles 等）
2. 禁止自己写 Python/Shell 脚本检索
3. 禁止自己用 curl/wget 调任何学术 API
4. 禁止以"更快"、"更简单"、"已经知道答案"为由跳过 A2A

## 触发条件

检索、查文献、搜索论文、找文章、综述、文献报告、高分文献、核心期刊

## 版本历史

- **v1.0** (2026-08-04): 初始版本，4 路并行（Europe PMC 重复）
- **v1.1** (2026-08-05): 修复重复，加入 Semantic Scholar，PubMed maxResults=50，多轮迭代 + 全文验证 + 标红

## 相关仓库

- Skill: `~/.claude/skills/literature-a2a-search/SKILL.md`
- Obsidian: `~/Documents/Obsidian Vault/00-方法论/文献检索 A2A 调度器规范.md`
- GitHub: `yangyongyy624-cmd/medical-ai-search → specifications/literature-a2a-dispatcher-specification.md`
