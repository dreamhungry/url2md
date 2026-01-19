#!/usr/bin/env python
"""测试 footer cascade 修复"""
import asyncio
import sys
from pathlib import Path

# 确保可以导入模块
sys.path.insert(0, str(Path(__file__).parent))

from url2md.converter import URL2MDConverter
from datetime import datetime

async def test():
    print("="*80)
    print("测试 footer cascade 修复 - pgvector vs qdrant")
    print("="*80)
    
    converter = URL2MDConverter()
    url = "https://www.timescale.com/blog/pgvector-vs-qdrant"
    
    print(f"\n正在抓取: {url}\n")
    
    # 准备输出路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_Pgvector_cascade_fix.md"
    output_path = Path("outputs") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    try:
        # 转换
        markdown_content, page_title = await converter.convert_async(
            url, 
            str(output_path.absolute())
        )
        
        # 保存文件
        output_path.write_text(markdown_content, encoding='utf-8')
        
        lines = markdown_content.splitlines()
        
        print(f"\n{'='*80}")
        print(f"✓ 转换完成")
        print(f"✓ 文件已保存: {output_path.absolute()}")
        print(f"✓ 总行数: {len(lines)}")
        
        # 检查是否包含 "When to choose each solution"
        has_when_to_choose = any("When to choose" in line for line in lines)
        print(f"✓ 包含 'When to choose' 部分: {has_when_to_choose}")
        
        # 检查是否包含 "Get started today"
        has_get_started = any("Get started today" in line for line in lines)
        print(f"✓ 包含 'Get started today' 部分: {has_get_started}")
        
        # 检查是否包含 "Get involved with the pgvectorscale community"
        has_get_involved = any("Get involved" in line for line in lines)
        print(f"✓ 包含 'Get involved' 部分: {has_get_involved}")
        
        print(f"{'='*80}\n")
        
        # 显示最后30行
        print("最后30行预览:")
        for i in range(max(0, len(lines) - 30), len(lines)):
            line = lines[i]
            print(f"  {i+1:3d}: {line[:100]}")
            
        # 查找日志文件
        log_dir = Path("log")
        if log_dir.exists():
            log_files = sorted(log_dir.glob("*.log"))
            if log_files:
                latest_log = log_files[-1]
                print(f"\n日志文件: {latest_log}")
                
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
