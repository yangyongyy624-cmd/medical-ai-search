# AI Medical Expert Discovery System

**AI 医学领域专家发现系统** - 找到行业内真正的大佬，而不只是发文章最多的人

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version: 2.0](https://img.shields.io/badge/version-2.0-green.svg)](https://github.com/YOUR_USERNAME/medical-ai-search/releases)

---

##  核心理念

> **传统检索**: 找到"发文章最多的人"  
> **我们的方法**: 找到"定义行业的人"

---

##  核心功能

### 1. 行业大佬发现 (第一性原理版)

直接搜索身份标签，不绕弯子：

```python
from simple_big_shot_finder import SimpleBigShotFinder

finder = SimpleBigShotFinder()

# 找到所有行业大佬 (不设上限)
big_shots = finder.find_big_shots("stem cell CAR-T")

# 输出:
# 1. Carl H. June - 学会主席 + 奖项获得者 + 指南作者
# 2. Michel Sadelain - 指南作者 + 开创性研究者
# 3. ...
```

**搜索的身份标签**:
- ✅ 学会主席/主委 (`society president`)
- ✅ 指南第一/通讯作者 (`guideline author`)
- ✅ 奖项获得者 (`Nobel Prize`, `Lasker Award`)
- ✅ 大会主席 (`conference chair`)

---

### 2. 大佬文献调研一键执行

找到大佬后，自动检索他们的高分文献：

```python
from big_shot_literature_survey import BigShotLiteratureSurvey

surveyor = BigShotLiteratureSurvey()

# 一键执行: 找大佬 + 检索高分文献 + 生成 Obsidian 笔记
result = surveyor.survey("rTMS depression", top_n=10)

# 输出:
# ✅ 10 位大佬
# ✅ 每位大佬的 3-5 篇高分文献
# ✅ Obsidian 笔记 (双向链接)
```

**高分期刊过滤**:
- Nature/Science/Cell
- NEJM/Lancet/BMJ
- Brain Stimulation
- American Journal of Psychiatry
- JAMA Psychiatry

---

### 3. Obsidian 双向链接笔记

自动生成结构化的 Obsidian 笔记：

```markdown
# rTMS/Stanford SNT - 行业顶尖科学家文献调研

##  大佬名单

### 1. [[Cole_EJ|Cole EJ]]
身份：Stanford SNT 开创者
代表文献:
- [[PMID_32252538|Stanford Accelerated Intelligent...]]
  期刊：Am J Psychiatry, 2020 ⭐ 开创性文献

##  快速导航
[[Cole_EJ]] [[Williams_NR]] [[Blumberger_DM]] ...
```

---

##  快速开始

### 安装

```bash
git clone https://github.com/YOUR_USERNAME/medical-ai-search.git
cd medical-ai-search
pip install -r requirements.txt
```

### 使用

#### 方式 1: 找行业大佬

```bash
python3 simple_big_shot_finder.py
```

#### 方式 2: 一键文献调研

```bash
python3 big_shot_literature_survey.py
```

#### 方式 3: Python 调用

```python
from big_shot_literature_survey import BigShotLiteratureSurvey

surveyor = BigShotLiteratureSurvey()
result = surveyor.survey("stem cell CAR-T", top_n=10)
```

---

##  实战测试

### 测试领域：rTMS/Stanford SNT

**测试结果**:

| 指标 | 结果 |
|------|------|
| 找到大佬数 | 8 位 |
| 高分文献数 | 13 篇 |
| 开创性文献 | ✅ PMID 32252538 (Cole 2020) |
| Obsidian 笔记 | ✅ 自动生成 |

**核心发现**:
```
1. Cole EJ - Stanford SNT 开创者 ✅
   - PMID 32252538 (2020 SNT 开创性研究)
   - PMID 34711062 (2022 双盲 RCT)

2. Williams NR - Stanford SNT 开创者 ✅
   - PMID 38161297 (2024 长期疗效)

3. Blumberger DM - rTMS 高产出 ✅
   - PMID 42415252 (2026 网络定位)
```

---

##  与传统方法对比

| 特性 | 传统检索 | 本系统 |
|------|----------|--------|
| 搜索方式 | 关键词 | 身份标签 |
| 数量限制 | Top 10 | 不设上限 |
| 筛选标准 | 文章数 | 学会主席/指南作者/奖项 |
| 文献质量 | 不分高低 | 只看顶级期刊 |
| 输出格式 | 列表 | Obsidian 双向链接 |

---

##  项目结构

```
medical-ai-search/
├── simple_big_shot_finder.py       # 大佬发现系统
├── big_shot_literature_survey.py   # 文献调研系统
├── literature_search.py             # PubMed 检索
├── search_optimizer.py              # 检索优化
├── medical_ai.py                    # 完整工作流
├── requirements.txt                 # 依赖
├── README.md                        # 本文档
├── RELEASE.md                       # 发布说明
├── TEST_REPORT.md                   # 测试报告
└── examples/                        # 使用示例
```

---

##  使用场景

### 场景 1: 新领域调研

```python
surveyor = BigShotLiteratureSurvey()
result = surveyor.survey("stem cell diabetes")

# 输出:
# - 领域大佬名单 (10 位)
# - 每位大佬的高分文献
# - Obsidian 笔记 (双向链接)
```

### 场景 2: 学术会议邀请

```python
finder = SimpleBigShotFinder()
big_shots = finder.find_big_shots("cancer immunotherapy")

# 找到 keynote speaker 候选人
keynote_candidates = [
    e for e in big_shots 
    if 'conference chair' in e['identities']
]
```

### 场景 3: 合作者筛选

```python
# 找有实际资源的大佬
result = surveyor.survey("CAR-T solid tumor")
industry_leaders = [
    e for e in result 
    if 'society president' in e['identities']
]
```

---

##  依赖

```txt
requests>=2.31.0
PyYAML>=6.0
tavily-python>=0.3.0  # 可选，用于网络搜索
```

---

##  许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

##  引用

如果您使用了这个工具，请引用：

```
宵宵。AI Medical Expert Discovery System v2.0. 2026-07-11.
GitHub: https://github.com/YOUR_USERNAME/medical-ai-search
```

---

##  联系方式

- GitHub Issues: 提出问题
- Email: your.email@example.com

---

##  更新日志

### v2.0 (2026-07-11)

**新增**:
- 大佬发现系统 (第一性原理版)
- 文献调研一键执行
- Obsidian 双向链接笔记
- 高分期刊过滤
- rTMS/Stanford SNT 实战测试

### v1.0 (2026-07-11)

**新增**:
- 医学细分领域专家发现
- 中英文双语支持
- 机构信息自动提取

---

**最后更新**: 2026-07-11
