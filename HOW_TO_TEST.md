# 测试运行指南

## ⚠️ 重要提醒

**必须使用 `uv run` 命令运行所有测试脚本！**

直接使用 `python` 命令可能会因为依赖环境问题而失败。

## 快速开始

### 1. 运行基本测试

```bash
# 测试 DataCamp 文章（包含侧边栏）
uv run python tests/test_datacamp.py

# 测试 TigerData 文章（包含footer）
uv run python tests/test_tigerdata.py
```

### 2. 查看输出

测试运行时会在控制台显示：

```
📋 日志文件: d:\mywork\url2md\log\clean_20260114_175230.log
📄 输出文件: d:\mywork\url2md\outputs\20260114_175230_Article_Title.md
```

### 3. 验证结果

#### 检查输出文件
```bash
# 查看生成的 Markdown 文件
code outputs/20260114_175230_*.md
```

#### 检查日志文件
```bash
# 查看处理日志（Windows PowerShell）
Get-Content log\clean_20260114_175230.log

# 或用编辑器打开
code log\clean_20260114_175230.log
```

## 日志文件说明

日志文件包含详细的分析过程：

### 关键信息解读

```log
--- Section 0: What is a Vector Database?
    Lines: 25, Non-empty: 20, Link lines: 3
    Link count: 5, Text length (no links): 856
    Link ratio: 0.15, Links/100chars: 0.58
    Avg chars per link: 171.2
    MD high links: False, HTML high links: False
    >>> IS_FOOTER: False
```

**字段说明**：

- `Lines`: Section总行数
- `Non-empty`: 非空行数
- `Link lines`: 包含链接的行数
- `Link count`: 链接总数
- `Text length (no links)`: **排除链接文本后**的纯内容字符数
- `Link ratio`: 链接行占比 (link_lines / non_empty_lines)
- `Links/100chars`: 每100字符的链接数量（基于不含链接的文本长度）
- `Avg chars per link`: 平均每个链接的上下文字符数
- `IS_FOOTER`: 是否被判定为footer/导航区域

### Footer判定规则

Section会被标记为footer如果满足以下**任一**条件：

1. `Links/100chars > 3` - 极高链接密度
2. `Link ratio > 0.7 AND Link count > 10` - 大部分行都是链接
3. `Link count > 12 AND Avg chars per link < 80` - 密集短链接列表
4. `MD high links AND HTML high links AND Text length < 400` - 双重验证短section
5. `Text length < 200 AND Links/100chars > 1.5` - 很短但链接密集
6. `Link count > 50` - 超多链接（典型footer）

## 常见问题

### Q: 为什么必须用 `uv run`？

**A**: `uv run` 会自动激活虚拟环境并使用正确的依赖。直接用 `python` 可能使用系统Python或缺少依赖。

### Q: 日志文件在哪里？

**A**: 
- 位置：`log/` 目录
- 命名：`clean_YYYYMMDD_HHMMSS.log`
- 每次运行都会创建新的日志文件

### Q: 如何判断转换是否成功？

**A**: 检查以下几点：

1. **控制台输出**：无错误信息
2. **输出文件**：
   - 文件存在于 `outputs/` 目录
   - 内容开头有H1标题和Source链接
   - 内容长度合理（不是太短或太长）
3. **日志文件**：
   - 有明确的 "Content range" 行
   - Footer sections被正确标记

### Q: 导航栏没有被过滤怎么办？

**A**: 

1. 打开日志文件，查找该区域对应的Section
2. 查看其链接密度指标
3. 如果指标未达到阈值，可以调整 `converter.py` 中的判定规则

### Q: 正文内容被误删了怎么办？

**A**: 

1. 查看日志中被删除部分的Section统计
2. 如果是因为包含大量链接（如推荐列表），考虑：
   - 放宽Footer判定阈值
   - 或在代码中添加特殊处理逻辑

## 测试用例说明

### DataCamp测试
- **URL**: `https://www.datacamp.com/blog/the-top-5-vector-databases`
- **特点**: 左侧有导航栏（第11-57行应该被删除）
- **验证**: 文章应该从"The 7 Best Vector Databases"标题开始

### TigerData测试
- **URL**: `https://www.tigerdata.com/blog/pgvector-vs-qdrant`
- **特点**: 
  - 文章有引言段落（第7-9行应保留）
  - 底部有"Related posts"（第240行后应删除）
- **验证**: 
  - 引言"Can you stick with PostgreSQL..."应该存在
  - 不应该有"Related posts"部分

## 性能优化建议

如果转换速度慢：

1. 检查网络连接（crawl4ai需要下载网页）
2. 某些网站响应较慢，属正常情况
3. 日志记录会略微影响性能，但便于调试

## 下一步

修改完代码后：

1. 运行测试验证
2. 查看日志确认逻辑正确
3. 对比输出文件检查效果
4. 提交代码前运行所有测试用例
