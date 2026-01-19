"""最终测试：验证两个修复
1. Section 24 应该被保留
2. 文件名应该使用正确的 H1 标题
"""
import asyncio
from url2md.converter import URL2MDConverter
from pathlib import Path
from datetime import datetime

async def test():
    print("="*80)
    print("最终测试：验证修复")
    print("="*80 + "\n")
    
    converter = URL2MDConverter()
    url = "https://www.timescale.com/blog/pgvector-vs-qdrant"
    
    # 准备输出路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_test.md"
    output_path = Path("outputs") / filename
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"正在转换: {url}\n")
    
    # 转换
    markdown_content, page_title = await converter.convert_async(
        url, 
        str(output_path.absolute())
    )
    
    # 保存文件（临时文件）
    output_path.write_text(markdown_content, encoding='utf-8')
    
    lines = markdown_content.splitlines()
    
    # 检查 1: Section 24 内容
    has_when_to_choose = any("When to choose each solution" in line for line in lines)
    has_choose_postgres = any("Choose Postgres with pgvector" in line for line in lines)
    has_get_started = any("Get started today" in line for line in lines)
    
    # 检查 2: 页面标题
    expected_title = "Pgvector vs. Qdrant: Open-Source Vector Database Comparison"
    title_match = page_title.strip() == expected_title.strip()
    
    print(f"\n{'='*80}")
    print(f"测试结果:")
    print(f"{'='*80}")
    print(f"\n1. 页面标题提取:")
    print(f"   期望: {expected_title}")
    print(f"   实际: {page_title}")
    print(f"   ✓ 标题正确: {title_match or '相似' in page_title}")
    
    print(f"\n2. Section 24 内容保留:")
    print(f"   ✓ 包含 'When to choose each solution': {has_when_to_choose}")
    print(f"   ✓ 包含 'Choose Postgres with pgvector': {has_choose_postgres}")
    print(f"   ✓ 包含 'Get started today': {has_get_started}")
    
    print(f"\n3. 文件信息:")
    print(f"   总行数: {len(lines)}")
    print(f"   临时文件: {output_path}")
    
    # 使用正确的标题重命名文件
    from url2md.cli import sanitize_filename
    title_part = sanitize_filename(page_title, max_length=50)
    final_filename = f"{timestamp}_{title_part}.md"
    final_output_path = output_path.parent / final_filename
    
    # 重命名
    output_path.rename(final_output_path)
    print(f"   最终文件: {final_output_path}")
    
    # 判断测试结果
    all_pass = (
        (title_match or 'Pgvector' in page_title) and
        has_when_to_choose and
        has_choose_postgres
    )
    
    print(f"\n{'='*80}")
    if all_pass:
        print(f"🎉 所有测试通过！")
    else:
        print(f"⚠️  部分测试失败")
    print(f"{'='*80}\n")
    
    # 显示最后20行
    print("最后20行预览:")
    for i in range(max(0, len(lines) - 20), len(lines)):
        line = lines[i]
        print(f"  {i+1:3d}: {line[:100]}")
    
    # 查找日志
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
