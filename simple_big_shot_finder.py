#!/usr/bin/env python3
"""
行业大佬发现系统 - 第一性原理版

核心思想：
1. 直接搜身份，不绕弯子
2. 不设数量上限，有多少算多少
3. 每个大佬都有明确身份标签 + 来源链接

作者：宵宵
日期：2026-07-11
"""

from typing import List, Dict


class SimpleBigShotFinder:
    """行业大佬发现系统 - 简单版"""

    def __init__(self):
        pass

    def find_big_shots(self, subfield: str) -> List[Dict]:
        """
        找到行业内所有顶尖科学家

        Args:
            subfield: 细分领域（如"stem cell CAR-T"）

        Returns:
            大佬名单（不限制数量）
        """
        print(f"\n{'='*60}")
        print(f"行业大佬发现：{subfield}")
        print(f"{'='*60}")

        # 身份标签 + 搜索查询
        identity_queries = {
            '学会主席': [
                f"{subfield} society president",
                f"{subfield} 学会 主席",
                f"{subfield} 学会 主委",
            ],
            '前学会主席': [
                f"{subfield} past society president",
                f"{subfield} 前 主席",
            ],
            '指南第一作者': [
                f"{subfield} guideline first author",
                f"{subfield} 指南 第一作者",
            ],
            '指南通讯作者': [
                f"{subfield} guideline corresponding author",
                f"{subfield} 指南 通讯作者",
            ],
            '诺贝尔奖获得者': [
                f"{subfield} Nobel Prize",
                f"{subfield} 诺贝尔奖",
            ],
            '拉斯克奖获得者': [
                f"{subfield} Lasker Award",
                f"{subfield} 拉斯克奖",
            ],
            '大会主席': [
                f"{subfield} conference chair",
                f"{subfield} 大会 主席",
            ],
            '主委/主任委员': [
                f"{subfield} committee chair",
                f"{subfield} 主任委员",
            ],
        }

        # 收集所有结果
        all_big_shots = []

        for identity, queries in identity_queries.items():
            print(f"\n[搜索] {identity}...")
            for query in queries:
                results = self._tavily_search(query)
                for result in results[:5]:  # 每个查询取前 5 个结果
                    name = self._extract_name(result)
                    if name:
                        all_big_shots.append({
                            'name': name,
                            'identity': identity,
                            'source': result.get('url', ''),
                            'query': query
                        })

        # 去重 + 合并身份
        print(f"\n[处理] 去重 + 合并身份...")
        deduped = self._deduplicate_and_merge(all_big_shots)

        # 按身份数量排序（身份越多越重要）
        result = sorted(
            deduped,
            key=lambda x: len(x['identities']),
            reverse=True
        )

        print(f"\n[结果] 找到 {len(result)} 位行业大佬")
        self._print_results(result)

        return result

    def _tavily_search(self, query: str) -> List[Dict]:
        """Tavily 网络搜索"""
        # 实际调用 Tavily API
        # 这里用模拟数据
        return []

    def _extract_name(self, result: Dict) -> str:
        """从搜索结果提取人名"""
        # 简单实现
        title = result.get('title', '')
        content = result.get('content', '')

        # 英文人名模式
        import re
        pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)'
        matches = re.findall(pattern, title + ' ' + content)

        if matches:
            return matches[0]

        return ''

    def _deduplicate_and_merge(self, experts: List[Dict]) -> List[Dict]:
        """去重 + 合并身份"""
        deduped = {}

        for expert in experts:
            name = expert['name']
            if name not in deduped:
                deduped[name] = {
                    'name': name,
                    'identities': [expert['identity']],
                    'sources': [expert['source']],
                }
            else:
                # 合并身份
                if expert['identity'] not in deduped[name]['identities']:
                    deduped[name]['identities'].append(expert['identity'])
                deduped[name]['sources'].append(expert['source'])

        return list(deduped.values())

    def _print_results(self, big_shots: List[Dict]):
        """打印结果"""
        print("\n" + "="*60)
        print("行业顶尖科学家名单")
        print("="*60)

        for i, expert in enumerate(big_shots, 1):
            print(f"\n{i}. {expert['name']}")
            print(f"   身份：{' + '.join(expert['identities'])}")
            print(f"   来源：{len(expert['sources'])} 个")

            # 显示前 3 个来源
            for source in expert['sources'][:3]:
                print(f"   - {source}")


# ==================== 使用示例 ====================

if __name__ == '__main__':
    finder = SimpleBigShotFinder()

    # 示例：干细胞 CAR-T
    result = finder.find_big_shots("stem cell CAR-T cancer")

    # 保存结果
    import json
    with open('big_shots_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n结果已保存到 big_shots_result.json")
