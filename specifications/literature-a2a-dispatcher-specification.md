# 文献检索 A2A 调度器规范

> 创建于 2026-08-04 | 更新于 2026-08-05 | 最终版 | 铁律级别

## 核心原则

**全面 > 速度** — 用户要的是全面、准确、内容丰富，不是快。

## 最终架构：7路主链 + 1路云端辅助（非阻塞）

| 路数 | Agent | 身份 | 任务分工 | 阻塞性 |
|:---:|:---:|:---:|:---|:---:|
| **0** | **本地磁盘** | 脚本 | **Obsidian 知识库基线** | 阻塞 |
| **1** | **蛋蛋** (Dandan) | 独立实例 | **反向追踪** (OpenAlex/CrossRef) | 阻塞 |
| **2** | **桐桐** (Tongtong) | 独立实例 | **正向追踪** (Semantic Scholar/EPMC) | 阻塞 |
| **3** | **宵宵** (Xiaoxiao) | 本地主实例 | **临床核心** (PubMed MCP) | 阻塞 |
| **4** | **Tiny** | 宵宵分身 | **全文验证** (fetch_articles) | 阻塞 |
| **5** | **Smile** | 宵宵分身 | **指南检索** (Web Search) | 阻塞 |
| **6** | **Codex** | 独立实例 | **矛盾标红** (对比验证) | 阻塞 |
| **7** | **Hermes** | 独立实例 | **备份兜底** (失败重试) | 阻塞 |
| **8** | **肖肖** (Cloud) | 云端实例 | **境外补充** (跨墙抓取) | 🟡 非阻塞(后台, 超时自动丢弃) |

## 三层强约束

### 1. 工具层约束（最强制）
```toml
disallowed_tools = [
    "mcp__pubmed__pubmed_search_articles",
    "mcp__pubmed__pubmed_europepmc_search",
]
```
禁搜索，保留辅助（fetch_articles / fetch_fulltext / find_related / lookup_mesh / convert_ids）

### 2. 提示词层约束
cc-connect `system_prompt` 铁律：A2A 唯一入口 + 多轮迭代 + 全文验证 + 标红

### 3. 流程层约束
a2a-dispatcher 派发 7 路主链 + 1 路云端辅助。Claude Code 仅作为指挥官（理解需求→调度→整合），不碰任何 API 调用。

## 唯一正确方式
```bash
~/.a2a/bin/a2a-dispatcher search "关键词"
```

## 版本历史
- v1.3 (2026-08-05): 三层强约束，完整验证通过
- v1.4 (2026-08-05): 引入 Tiny/Smile 分身，注册到 A2A
- v1.5 (2026-08-05): 云端肖肖非阻塞辅助架构定稿
- v1.6 (2026-08-05): 修正本地为宵宵、云端为肖肖的命名规范

## 相关仓库
- Skill: `~/.claude/skills/literature-a2a-search/SKILL.md`
- Obsidian: `~/Documents/Obsidian Vault/00-方法论/文献检索 A2A 调度器规范.md`
- GitHub: `yangyongyy624-cmd/medical-ai-search → specifications/literature-a2a-dispatcher-specification.md`

## 实测验证记录

### v1.6 实测 (2026-08-05) - 不宁腿综合征 RLS

| 检查项 | 结果 | 说明 |
|--------|------|------|
| A2A 调用 | ✅ 2 次 | 中英文双关键词 |
| Fetch全文 | ✅ 2 次 | fetch_articles |
| 直接PubMed搜索 | ⚠️ 1 次 | 部分违规 |
| 标红 | ✅ 4 条 | 多巴胺激动剂、铁补充阈值、阿片类、非药物证据 |
| 文献量 | ✅ 52 篇 | 去重后 |
| 报告质量 | ✅ | AASM 2025 指南、治疗范式转变 |
