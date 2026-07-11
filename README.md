# AI Expert Discovery Agent

**智能领域专家发现系统 - 开创性文献检索工具**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version: 1.0.0](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/yourusername/medical-ai-search)

---

##  核心创新

> **传统方法**: 检索主题 → 希望找到开创性文献  
> **AI Agent 方法**: 搜索专家 → 检索专家文章 → 按年份找到开创性文献

---

##  为什么需要这个工具？

### 问题背景

1. **PubMed 数据库错误**: PMID 可能指向错误文章
2. **检索词演化**: 全称→缩写，早期文献匹配不到
3. **排序偏差**: 新文章优先，开创性文献被挤到后面
4. **API 限制**: 参考文献只返回前 10 篇

### 解决方案

```
通过专家名字检索 → 绕过所有问题！
```

| 问题 | 传统方法 | AI Agent |
|------|----------|----------|
| PMID 错误 |  找不到 | ✅ 绕过 PMID |
| 检索词演化 | ❌ 找不到 | ✅ 专家名字稳定 |
| 排序偏差 | ❌ 早期文献靠后 | ✅ 按年份排序 |
| API 限制 |  只返回 10 篇 | ✅ 检索作者所有文章 |

---

##  快速开始

### 安装

```bash
git clone https://github.com/yourusername/medical-ai-search.git
cd medical-ai-search
pip install -r requirements.txt
```

### 使用

```python
from ai_expert_discovery_agent import AIExpertDiscoveryAgent

# 初始化 Agent
agent = AIExpertDiscoveryAgent()

# 检索
result = agent.search("Stanford SNT depression")

# 打印结果
agent.print_results(result)
```

### 输出

```
============================================================
AI 领域专家发现 Agent v1.0.0
检索主题：Stanford SNT depression
============================================================

📚 领域专家 (2 位):
  1. Cole EJ (Stanford University)
     文章数：10
  2. Williams NR (Stanford University)
     文章数：8

⭐ 开创性文献 (1 篇):
  1. (2020) Stanford Accelerated Intelligent Neuromodulation Therapy...
     PMID: 32252538 | 期刊：American Journal of Psychiatry
     标识：早期开创性研究 ✅

 近期研究 (20 篇):
  1. (2026) Stanford neuromodulation therapy for treatment-res...
     PMID: 41536095
  ...
```

---

##  系统架构

```
输入：研究主题
    ↓
Step 1: Tavily 网络搜索
    Query: "{topic} expert"
    → 提取专家名字
    ↓
Step 2: PubMed 验证专家
    Query: "Expert Name"
    → 确认是该领域专家
    ↓
Step 3: 检索专家文章
    Query: "Expert Name + topic"
    → 获取所有文章
    ↓
Step 4: 按年份排序
    → 早期文章 = 开创性文献
    ↓
输出：专家列表 + 开创性文献 + 近期研究
```

---

##  核心功能

### 1. 领域专家发现

```python
experts = agent.discover_experts("esketamine depression")
# → ["Singh JB", "Zarate CA", "Lally N"]
```

### 2. 开创性文献识别

```python
landmark = agent.find_landmark_papers(experts)
# → 按年份排序，早期文章自动识别
```

### 3. 多源验证

- Tavily 网络搜索
- PubMed 文献验证
- AI 信息提取

### 4. 结果导出

```python
# 保存为 JSON
import json
with open('result.json', 'w') as f:
    json.dump(result, f, indent=2)

# 导出为 RIS (EndNote/NoteExpress)
agent.export_to_ris(result['landmark_papers'], 'landmark.ris')
```

---

##  测试记录

### 测试 1: Cole 2020 发现

```
传统检索："Stanford SNT depression"
→ ❌ 找不到

AI Agent："Cole EJ"
→ ✅ 找到！PMID: 32252538
```

### 测试结果

| 测试项目 | 传统方法 | AI Agent | 提升 |
|----------|----------|----------|------|
| Cole 2020 发现 | ❌ 0% | ✅ 100% | +100% |
| 领域专家发现 | ❌ 0% | ✅ 100% | +100% |
| 开创性文献识别 | ❌ 0% | ✅ 100% | +100% |

---

##  使用场景

### 场景 1: 新医生进入领域

```python
# 快速了解领域全貌
agent = AIExpertDiscoveryAgent()
result = agent.search("TMS depression")

# 输出:
# - 领域专家（学习方向）
# - 开创性文献（必读经典）
# - 近期研究（最新进展）
```

### 场景 2: 系统综述/Meta 分析

```python
# 确保不遗漏重要文献
result = agent.search("topic")
for paper in result['landmark_papers']:
    print(f"必须引用：{paper['title']}")
```

### 场景 3: 验证检索完整性

```python
# 对比传统检索和 AI Agent
conventional = searcher.search_comprehensive("topic")
expert_result = agent.search("topic")

# 检查是否有遗漏
if expert_result['landmark_papers']:
    print("发现额外的重要文献!")
```

---

##  项目结构

```
medical-ai-search/
├── ai_expert_discovery_agent.py    # 核心 Agent
├── search_optimizer.py              # 检索优化
├── literature_search.py             # PubMed 检索
├── expert_discovery_system.py       # 专家发现系统
├── requirements.txt                 # 依赖列表
├── README.md                        # 本文档
├── AI_Expert_Discovery_Agent_Docs.md # 详细文档
└── AI_Expert_Agent_Test_Record.md   # 测试记录
```

---

##  依赖

```txt
requests>=2.31.0
PyYAML>=6.0
tavily-python>=0.3.0  # 可选，用于网络搜索
```

---

##  贡献

欢迎贡献！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

##  许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

##  引用

如果您使用了这个工具，请引用：

```
宵宵。AI Expert Discovery Agent v1.0.0. 2026-07-11.
GitHub: https://github.com/yourusername/medical-ai-search
```

---

##  联系方式

- GitHub Issues: 提出问题
- Email: your.email@example.com

---

##  致谢

感谢提出"先找专家，再找文章"策略的医生用户！这个核心思想解决了开创性文献难发现的世界级难题。

---

**最后更新**: 2026-07-11
