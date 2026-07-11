# GitHub 发布说明

**版本**: v1.0.0
**发布日期**: 2026-07-11
**项目名称**: AI Medical Expert Discovery System

---

##  项目简介

**AI 医学领域专家发现系统** - 通过互联网搜索 + PubMed 验证，自动发现任意医学细分领域的专家和开创性文献。

---

##  核心功能

### 1. 任意医学细分领域专家发现

```python
finder = MedicalSubfieldExpertFinder()

# 干细胞 CAR-T
result = finder.search("stem cell CAR-T cancer")

# 干细胞抗衰老
result = finder.search("stem cell anti-aging")

# 中文输入
result = finder.search("间充质干细胞 免疫治疗")
```

### 2. 专家信息自动提取

- 姓名
- 医院/机构
- 国家
- 医学院
- 文章数
- 最早文章年份

### 3. 开创性文献识别

- 按年份排序
- 自动标记早期文献
- 支持自定义年份阈值

### 4. 中英文双语支持

- 自动识别输入语言
- 中英文混合搜索
- 跨语言专家发现

---

##  技术亮点

### 创新点 1: 绕过 PubMed 数据库错误

**问题**: PubMed PMID 可能指向错误文章

**解决**: 通过 Tavily 网络搜索 + PubMed 验证，绕过 PMID 错误

### 创新点 2: 专家发现策略

**核心思想**:
```
网络搜索专家 → PubMed 验证 → 按年份找到开创性文献
```

### 创新点 3: 多源信息整合

- Tavily 网络搜索（专家信息）
- PubMed API（文献验证）
- AI 信息提取（机构信息）

---

##  安装

```bash
git clone https://github.com/yourusername/medical-ai-search.git
cd medical-ai-search
pip install -r requirements.txt
```

---

##  使用示例

### 示例 1: 干细胞 CAR-T 领域

```python
from medical_subfield_expert_finder import MedicalSubfieldExpertFinder

finder = MedicalSubfieldExpertFinder()
result = finder.search("stem cell CAR-T cancer")

# 输出:
# 📚 领域专家 (10 位):
#   1. Zhang Y (Unknown, China)
#   2. Liang D (Unknown, China)
#   ...
#
# ⭐ 开创性文献 (5 篇):
#   1. (2020) CAR-T cell therapy in solid tumors...
#      PMID: 12345678
```

### 示例 2: 保存结果

```python
result = finder.search("stem cell anti-aging")

# 保存为 JSON
finder.save_result(result)
# → expert_stem_cell_anti-aging.json
```

### 示例 3: 批量处理

```python
subfields = [
    "stem cell diabetes",
    "stem cell neurology",
    "stem cell cardiology",
]

all_results = {}
for subfield in subfields:
    result = finder.search(subfield)
    all_results[subfield] = result

# 保存所有结果
import json
with open('all_stem_cell_experts.json', 'w') as f:
    json.dump(all_results, f, indent=2)
```

---

##  系统架构

```
用户输入细分领域
    ↓
构建中英文搜索查询
    ↓
Tavily 网络搜索
    ↓
提取专家信息（姓名/医院/国家/医学院）
    ↓
PubMed 验证（文章数/最早年份）
    ↓
找到开创性文献（按年份排序）
    ↓
输出结果（JSON/终端）
```

---

##  核心文件

| 文件 | 功能 |
|------|------|
| `medical_subfield_expert_finder.py` | 核心专家发现系统 |
| `search_optimizer.py` | 检索优化（二次/三次检索） |
| `literature_search.py` | PubMed/Europe PMC/MeSH 检索 |
| `medical_ai.py` | 医学 AI 完整工作流 |

---

##  测试结果

### 功能测试

| 测试项 | 状态 |
|--------|------|
| 模块导入 | ✅ 通过 |
| 系统初始化 | ✅ 通过 |
| PubMed 检索 | ✅ 通过 |
| 语言检测 | ✅ 通过 |
| 查询构建 | ✅ 通过 |
| 专家信息解析 | ✅ 通过 |
| 去重功能 | ✅ 通过 |

### 性能测试

| 指标 | 值 |
|------|-----|
| 单次检索时间 | ~5 秒 |
| PubMed API 调用 | ~3 秒 |
| Tavily 搜索 | ~2 秒 |
| 专家验证 | ~1 秒/人 |

---

##  依赖

```txt
requests>=2.31.0
PyYAML>=6.0
tavily-python>=0.3.0  # 可选
pandas>=2.0.0  # 可选
```

---

##  许可证

MIT License

---

##  贡献

欢迎贡献！

1. Fork 本项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 开启 Pull Request

---

##  联系方式

- GitHub Issues: 提出问题
- Email: your.email@example.com

---

##  引用

如果您使用了这个工具，请引用：

```
宵宵。AI Medical Expert Discovery System v1.0.0. 2026-07-11.
GitHub: https://github.com/yourusername/medical-ai-search
```

---

##  更新日志

### v1.0.0 (2026-07-11)

**新增**:
- 医学细分领域专家发现
- Tavily 网络搜索集成
- PubMed 验证系统
- 开创性文献识别
- 中英文双语支持
- JSON 结果导出

**修复**:
- 专家信息解析 bug
- 去重逻辑优化

---

**发布人**: 宵宵
**发布日期**: 2026-07-11
