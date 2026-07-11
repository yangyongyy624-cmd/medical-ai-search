# GitHub 发布指南

**项目**: AI Medical Expert Discovery System
**版本**: v1.0.0
**发布日期**: 2026-07-11

---

##  推送命令

### 1. 设置远程仓库

```bash
cd ~/medical-ai-search

# 替换 YOUR_USERNAME 为您的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/medical-ai-search.git
```

### 2. 推送到 GitHub

```bash
# 推送主分支
git branch -M main
git push -u origin main
```

### 3. 创建 Release

访问：https://github.com/YOUR_USERNAME/medical-ai-search/releases/new

**Tag version**: `v1.0.0`
**Release title**: `AI Medical Expert Discovery System v1.0.0`
**Description**:
```markdown
## 核心功能

- 医学细分领域专家发现
- Tavily 网络搜索 + PubMed 验证
- 开创性文献自动识别
- 中英文双语支持
- 机构信息自动提取
- Obsidian 集成

## 安装

```bash
git clone https://github.com/YOUR_USERNAME/medical-ai-search.git
cd medical-ai-search
pip install -r requirements.txt
```

## 使用示例

```python
from medical_subfield_expert_finder import MedicalSubfieldExpertFinder

finder = MedicalSubfieldExpertFinder()
result = finder.search("stem cell CAR-T cancer")
```

## 文档

- README.md - 项目说明
- RELEASE.md - 发布说明
- TEST_REPORT.md - 测试结果
- Obsidian_集成指南.md - Obsidian 集成

## 技术栈

- Python 3.10+
- Tavily API (网络搜索)
- PubMed API (文献检索)

## 许可证

MIT License
```

**Publish**: ✅ Publish release to the public

---

##  完整推送脚本

```bash
#!/bin/bash
# push_to_github.sh

echo "推送到 GitHub..."

# 进入项目目录
cd ~/medical-ai-search

# 检查远程仓库
if ! git remote get-url origin &>/dev/null; then
    echo "请设置 GitHub 用户名:"
    read -p "GitHub Username: " username
    git remote add origin https://github.com/$username/medical-ai-search.git
fi

# 推送
git push -u origin main

echo "✅ 推送完成!"
echo ""
echo "下一步:"
echo "1. 访问 https://github.com/$username/medical-ai-search"
echo "2. 创建 Release: https://github.com/$username/medical-ai-search/releases/new"
echo "3. Tag: v1.0.0"
```

---

##  发布后检查

### 1. 检查仓库页面

访问：https://github.com/YOUR_USERNAME/medical-ai-search

确认：
- [ ] README.md 正确显示
- [ ] 所有文件已上传
- [ ] 许可证正确

### 2. 测试克隆

```bash
# 在新目录测试
cd /tmp
git clone https://github.com/YOUR_USERNAME/medical-ai-search.git
cd medical-ai-search
pip install -r requirements.txt
python3 medical_subfield_expert_finder.py
```

### 3. 添加话题标签

在仓库页面设置：
- `medical-ai`
- `expert-discovery`
- `literature-search`
- `pubmed`
- `tavily`
- `obsidian`
- `research-tools`

---

##  宣传文案

### Twitter / X

```
🎉 发布了 AI Medical Expert Discovery System v1.0.0!

通过互联网搜索 + PubMed 验证，自动发现任意医学细分领域的专家和开创性文献。

核心功能:
✅ 任意医学细分领域专家发现
✅ 中英文双语支持
✅ 开创性文献自动识别
✅ Obsidian 集成

GitHub: https://github.com/YOUR_USERNAME/medical-ai-search

#MedicalAI #ResearchTools #PubMed
```

### 微信朋友圈

```
【开源项目发布】AI 医学专家发现系统 v1.0.0

输入任意医学细分领域（如"干细胞 CAR-T"、"干细胞抗衰老"），自动找到该领域的国际专家和开创性文献！

特色功能:
🔍 中英文互联网搜索
🏥 提取专家机构信息
⭐ 按年份识别开创性文献
📚 Obsidian 双向链接

GitHub: https://github.com/YOUR_USERNAME/medical-ai-search

欢迎 Star、Fork、PR！
```

### LinkedIn

```
Excited to announce the release of AI Medical Expert Discovery System v1.0.0!

This tool helps researchers discover experts and landmark papers in any medical subfield through:
- Web search + PubMed verification
- Automatic institution extraction
- Landmark paper identification
- Obsidian integration

GitHub: https://github.com/YOUR_USERNAME/medical-ai-search

#MedicalAI #ResearchTools #OpenSource
```

---

##  维护计划

### 短期 (1 周)

- [ ] 收集用户反馈
- [ ] 修复 bug
- [ ] 添加更多示例

### 中期 (1 月)

- [ ] Tavily API 正式集成
- [ ] Google Scholar 集成
- [ ] 批量处理支持

### 长期 (3 月)

- [ ] PyPI 发布
- [ ] Web 界面
- [ ] 专家数据库

---

##  常见问题

### Q: 推送失败怎么办？

A: 检查：
1. GitHub 用户名是否正确
2. 是否有 SSH key 或 token
3. 网络连接是否正常

### Q: 如何更新版本？

```bash
# 修改版本号
# medical_subfield_expert_finder.py: __version__ = "1.0.1"

# 提交
git add .
git commit -m "Release v1.0.1: Bug fixes"

# 推送
git push

# 创建新 Release
# https://github.com/YOUR_USERNAME/medical-ai-search/releases/new
# Tag: v1.0.1
```

### Q: 如何接受贡献？

A: 在 README.md 中添加：
```markdown
## 贡献

欢迎贡献！

1. Fork 本项目
2. 创建功能分支 (git checkout -b feature/AmazingFeature)
3. 提交更改 (git commit -m 'Add some AmazingFeature')
4. 推送到分支 (git push origin feature/AmazingFeature)
5. 开启 Pull Request
```

---

**准备人**: 宵宵
**准备日期**: 2026-07-11
**状态**: ✅ 准备就绪
