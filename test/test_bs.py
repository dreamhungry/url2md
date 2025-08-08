import requests
from bs4 import BeautifulSoup, Comment
import html2text
from goose3 import Goose

def clean_html_content(soup):
    """
    清除HTML中的脚本、样式、注释等非内容标签。
    """
    for script in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
        script.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    return soup

def find_article_body_heuristically(soup):
    """
    使用启发式算法查找文章主体。
    """
    # 1. 尝试使用通用选择器
    selectors = [
        'article',
        'main',
        'div[class*="article"]',
        'div[id*="article"]',
        'div[class*="post"]',
        'div[id*="post"]',
        'div[class*="content"]',
        'div[id*="content"]'
    ]
    for selector in selectors:
        element = soup.select_one(selector)
        if element and len(element.text.strip()) > 500: # 假设文章主体文本长度大于500字符
            return element

    # 2. 如果通用选择器失败，尝试计算文本密度
    best_candidate = None
    max_text_density = 0
    
    # 查找所有可能包含文章主体的区块
    potential_containers = soup.find_all(['div', 'section'])
    
    for container in potential_containers:
        # 排除可能包含干扰内容的元素
        if container.has_attr('class') and any(keyword in ' '.join(container['class']) for keyword in ['sidebar', 'ad', 'footer', 'comment']):
            continue
        
        text_content = container.get_text(strip=True)
        # 确保元素包含段落或标题，而不是一个空的div
        if len(text_content) > 300 and container.find(['p', 'h1', 'h2', 'h3']):
            # 简单的文本密度计算
            text_density = len(text_content) / len(str(container))
            if text_density > max_text_density:
                max_text_density = text_density
                best_candidate = container
                
    return best_candidate

def extract_article_with_goose3(url):
    """
    使用goose3库自动提取文章主体内容。
    """
    try:
        g = Goose()
        article = g.extract(url=url)
        
        # 提取标题和内容
        title = article.title
        content_html = article.cleaned_text
        print(f"xxxxxxxxxxxxxxxxx {article.infos}")
        if title and content_html:
            print(f"成功提取标题: {title}")
            return f"<h1>{title}</h1>\n\n{content_html}"
        else:
            print("goose3未能成功提取内容。")
            return None
            
    except Exception as e:
        print(f"使用goose3提取失败: {e}")
        return None

# 使用示例
# article_content = extract_article_with_goose3('https://zhuanlan.zhihu.com/p/697920119')
# if article_content:
#     # 转换HTML为Markdown...
#     print(article_content)
def download_and_convert_adaptive(url, output_filename='blog_post.md'):
    """
    结合自适应算法下载并转换博客。
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 尝试使用goose3，如果失败则使用启发式算法
        article_html = extract_article_with_goose3(url)
        if not article_html:
            print("goose3提取失败，正在尝试使用启发式算法...")
            article_body = find_article_body_heuristically(soup)
            if article_body:
                # 清理并转换
                clean_html_content(article_body)
                article_html = str(article_body)
            else:
                print("启发式算法也未能找到文章主体。")
                return

        # 转换HTML为Markdown
        if article_html:
            h = html2text.HTML2Text()
            h.ignore_links = False
            markdown_content = h.handle(article_html)
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            print(f"成功将文章保存到 {output_filename}")
            
    except Exception as e:
        print(f"处理失败: {e}")

# 使用示例
if __name__ == "__main__":
    download_and_convert_adaptive("https://python.langchain.com/docs/concepts/architecture/")