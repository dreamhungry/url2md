"""测试 footer cascade 修复 - Section 24 应该被保留"""
import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test():
    print("="*80)
    print("测试: Footer Cascade 修复")
    print("URL: https://www.timescale.com/blog/pgvector-vs-qdrant")
    print("期望: 'When to choose each solution' 部分应该被保留")
    print("="*80 + "\n")
    
    converter = URL2MDConverter()
    url = "https://www.timescale.com/blog/pgvector-vs-qdrant"
    
    # 准备输出路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_Pgvector_cascade_test.md"
    output_path = Path("outputs") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"正在转换...\n")
    
    # 转换
    markdown_content, page_title = await converter.convert_async(
        url, 
        str(output_path.absolute())
    )
    
    # 保存文件
    output_path.write_text(markdown_content, encoding='utf-8')
    
    lines = markdown_content.splitlines()
    
    # 检查关键内容是否存在
    has_when_to_choose = any("When to choose each solution" in line for line in lines)
    has_choose_postgres = any("Choose Postgres with pgvector" in line for line in lines)
    has_consider_qdrant = any("Consider Qdrant" in line for line in lines)
    has_get_started = any("Get started today" in line for line in lines)
    has_get_involved = any("Get involved with the pgvectorscale community" in line for line in lines)
    
    print(f"\n{'='*80}")
    print(f"✓ 文件已保存: {output_path.absolute()}")
    print(f"✓ 总行数: {len(lines)}")
    print(f"\n内容检查:")
    print(f"  ✓ 包含 'When to choose each solution': {has_when_to_choose}")
    print(f"  ✓ 包含 'Choose Postgres with pgvector': {has_choose_postgres}")
    print(f"  ✓ 包含 'Consider Qdrant': {has_consider_qdrant}")
    print(f"  ✓ 包含 'Get started today': {has_get_started}")
    print(f"  ✓ 包含 'Get involved': {has_get_involved}")
    
    # 判断测试结果
    if has_when_to_choose and has_choose_postgres and has_consider_qdrant:
        print(f"\n🎉 测试通过! Section 24 已成功保留")
    else:
        print(f"\n⚠️  测试失败! Section 24 仍然被过滤")
    
    print(f"{'='*80}\n")
    
    # 显示最后40行
    print("最后40行预览:")
    for i in range(max(0, len(lines) - 40), len(lines)):
        line = lines[i]
        print(f"  {i+1:3d}: {line[:100]}")
    
    # 查找并显示日志文件路径
    print(f"\n{'='*80}")
    log_dir = Path("log")
    if log_dir.exists():
        log_files = sorted(log_dir.glob("clean_*.log"))
        if log_files:
            latest_log = log_files[-1]
            print(f"📋 日志文件: {latest_log.absolute()}")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test())
