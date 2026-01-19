#!/usr/bin/env python
"""测试日志输出功能"""
import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test():
    print("="*80)
    print("测试 pgvector vs qdrant 页面的 footer 过滤")
    print("="*80)
    
    converter = URL2MDConverter()
    url = "https://www.timescale.com/blog/pgvector-vs-qdrant"
    
    print(f"\n正在抓取: {url}")
    
    # 准备输出路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_Pgvector_test.md"
    output_path = Path("outputs") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"输出路径已准备: {output_path.absolute()}")
    print(f"开始转换...\n")
    
    # 转换并传递输出路径
    markdown_content, page_title = await converter.convert_async(
        url, 
        str(output_path.absolute())
    )
    
    # 保存文件
    output_path.write_text(markdown_content, encoding='utf-8')
    
    print(f"\n{'='*80}")
    print(f"✓ 转换完成")
    print(f"✓ 文件已保存: {output_path.absolute()}")
    print(f"✓ 内容长度: {len(markdown_content)} 字符")
    print(f"✓ 总行数: {len(markdown_content.splitlines())}")
    
    # 检查是否包含 "When to choose each solution"
    has_when_to_choose = "When to choose each solution" in markdown_content
    print(f"✓ 包含 'When to choose' 部分: {has_when_to_choose}")
    print(f"{'='*80}\n")
    
    # 显示最后30行
    lines = markdown_content.splitlines()
    print("最后30行预览:")
    for i, line in enumerate(lines[-30:], len(lines) - 29):
        print(f"  {i:3d}: {line[:80]}")

if __name__ == "__main__":
    asyncio.run(test())
