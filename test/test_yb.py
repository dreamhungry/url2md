import requests
from bs4 import BeautifulSoup
import urllib.parse
# pip install python-readability
import trafilatura

def text_density_based(soup):
    """
    基于文本密度和链接密度的算法
    """
    from bs4 import NavigableString
    
    def get_text_density(element):
        text_length = len(element.get_text(strip=True))
        html_length = len(str(element))
        return text_length / html_length if html_length > 0 else 0
    
    def get_link_density(element):
        links = element.find_all('a')
        link_text_length = sum(len(link.get_text(strip=True)) for link in links)
        total_text_length = len(element.get_text(strip=True))
        return link_text_length / total_text_length if total_text_length > 0 else 0
    
    candidates = []
    for element in soup.find_all(['article', 'div', 'section']):
        text_density = get_text_density(element)
        link_density = get_link_density(element)
        
        # 高文本密度和低链接密度的元素更有可能是主要内容
        if text_density > 0.5 and link_density < 0.2:
            candidates.append((element, text_density, link_density))
    
    if candidates:
        # 按文本密度降序排序
        candidates.sort(key=lambda x: (-x[1], x[2]))
        return candidates[0][0]
    
    return soup.body

def platform_specific_selectors(soup, url):
    domain = urllib.parse.urlparse(url).netloc
    
    # 针对不同平台使用特定选择器
    platform_selectors = {
        'medium.com': ['article', '.postArticle-content'],
        'wordpress.com': ['article', '.entry-content'],
        'blogger.com': ['.post-outer', '.entry-content'],
        'cnblogs.com': ['#mainContent', '.post'],
        'zhihu.com': ['.Post-RichTextContainer', '.RichText'],
        'jianshu.com': ['article', '.article'],
        'segmentfault.com': ['.article-content'],
        'csdn.net': ['article', '.blog-content-box'],
        'qq.com': ['.article', '.content-article'],
        'weixin.qq.com': ['#js_content'],
        'juejin.cn': ['.article-content'],
    }
    
    for domain_key, selectors in platform_selectors.items():
        if domain_key in domain:
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return element
    
    return None

def smart_content_extractor(url):
    """
    智能内容提取器，结合多种方法获取最佳结果
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # 首先尝试使用trafilatura
        downloaded = trafilatura.fetch_url(url)
        trafilatura_content = trafilatura.extract(downloaded, include_comments=False)
        if trafilatura_content and len(trafilatura_content) > 500:
            return trafilatura_content
    except:
        pass
    
    # 如果trafilatura失败，尝试其他方法
    response = requests.get(url, headers=headers)
    html = response.text
    
    # 尝试平台特定选择器
    soup = BeautifulSoup(html, 'html.parser')
    platform_content = platform_specific_selectors(soup, url)
    if platform_content:
        return str(platform_content)
    
    # 尝试readability
    # try:
    #     doc = Document(html)
    #     readability_content = doc.summary()
    #     if readability_content and len(readability_content) > 500:
    #         return readability_content
    # except:
    #     pass
    
    # 最后回退到文本密度算法
    return str(text_density_based(soup))

# 使用示例
if __name__ == "__main__":
    ret = smart_content_extractor("https://medium.com/predict/gpt-5-is-coming-in-july-2025-and-everything-will-change-643252fe6849")
    output_filename = 'yb_blog.md'
    print(ret)
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(ret)