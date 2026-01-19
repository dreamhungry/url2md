"""Core functionality for converting web pages to Markdown"""

from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import html2text
from typing import Optional
import asyncio
import re
from pathlib import Path
from datetime import datetime


class URL2MDConverter:
    """Convert web page content to Markdown format"""
    
    def __init__(self):
        # Configure html2text
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # Don't wrap lines
        self.h2t.single_line_break = False
        
        # Setup logging
        self.log_dir = Path("log")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = None
        self.log_path = None  # Track current log file path
    
    def _log(self, message: str):
        """Write log message to file"""
        if self.log_file:
            self.log_file.write(message + "\n")
            self.log_file.flush()
    
    def _calculate_text_length_without_links(self, text: str) -> tuple[int, int]:
        """Calculate text length excluding link text, and count links
        
        Args:
            text: Markdown text
            
        Returns:
            Tuple of (text_length_without_links, link_count)
        """
        # Find all markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\([^\)]+\)'
        links = re.findall(link_pattern, text)
        link_count = len(links)
        
        # Calculate total link text length
        link_text_length = sum(len(link_text) for link_text in links)
        
        # Total text length minus link text length
        total_length = len(text.strip())
        text_without_links_length = total_length - link_text_length
        
        return max(1, text_without_links_length), link_count
    
    def _extract_title_from_markdown(self, markdown: str) -> str:
        """Extract page title from markdown content (prefer H1 heading)
        
        Args:
            markdown: Markdown content
            
        Returns:
            Extracted title or 'Untitled'
        """
        lines = markdown.split('\n')
        for line in lines[:50]:  # Check first 50 lines
            stripped = line.strip()
            # Look for H1 heading (# Title, not ## or ###)
            if stripped.startswith('# ') and not stripped.startswith('## '):
                title = stripped[2:].strip()
                # Remove any markdown formatting
                title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', title)  # Remove links
                title = re.sub(r'[*_~`]', '', title)  # Remove formatting
                return title if title else 'Untitled'
        return 'Untitled'
    
    async def fetch_url(self, url: str) -> tuple[str, str]:
        """Fetch content from URL using crawl4ai
        
        Args:
            url: The URL to fetch
            
        Returns:
            Tuple of (HTML content, markdown content from crawl4ai)
            
        Raises:
            Exception: If the fetch fails
        """
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(
                url=url,
                # Wait for page to load completely
                wait_for="body",
                # Use JavaScript to wait for dynamic content
                js_code="await new Promise(resolve => setTimeout(resolve, 2000));",
                # Extract markdown directly
                bypass_cache=True
            )
            
            if not result.success:
                error_msg = getattr(result, 'error_message', 'Unknown error')
                raise Exception(f"Failed to crawl URL: {error_msg}")
            
            # Return both HTML and extracted markdown
            return result.html, result.markdown if hasattr(result, 'markdown') else ""
    
    def extract_main_content(self, html: str, url: str) -> str:
        """Extract main article content from HTML using DOM structure
        
        Args:
            html: Raw HTML content
            url: Original URL (for reference)
            
        Returns:
            Extracted main content as HTML
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Strategy 1: Find the article/main container first
        main_content = None
        
        # Priority selectors for main content
        content_selectors = [
            'article',
            '[role="main"]',
            'main',
            '.post-content',
            '.article-content',
            '.article-body',
            '.blog-content',
            '.entry-content',
            '.post-body',
            '.markdown-body',
            '[class*="blog-post"]',
            '[class*="article-container"]',
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                # Make a copy to work with
                main_content = BeautifulSoup(str(main_content), 'lxml')
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup
        
        # Strategy 2: Remove elements by their semantic role and position
        # Remove from the COPY, not the original
        
        # 1. Remove script, style, iframe (always unwanted)
        for tag in ['script', 'style', 'iframe']:
            for element in main_content.find_all(tag):
                element.decompose()
        
        # 2. Remove semantic navigation/header/footer elements
        for tag in ['nav', 'header', 'footer', 'aside']:
            for element in main_content.find_all(tag):
                element.decompose()
        
        # 3. Remove by common non-content classes/ids
        unwanted_patterns = [
            # Navigation
            lambda tag: tag.name in ['div', 'section'] and tag.get('class') and 
                       any('nav' in c.lower() for c in tag.get('class', [])),
            lambda tag: tag.name in ['div', 'section'] and tag.get('id') and 
                       'nav' in tag.get('id', '').lower(),
            # Sidebar
            lambda tag: tag.get('class') and any('sidebar' in c.lower() for c in tag.get('class', [])),
            lambda tag: tag.get('id') and 'sidebar' in tag.get('id', '').lower(),
            # Comments
            lambda tag: tag.get('class') and any('comment' in c.lower() for c in tag.get('class', [])),
            lambda tag: tag.get('id') and 'comment' in tag.get('id', '').lower(),
            # Ads and promotions
            lambda tag: tag.get('class') and any(p in str(tag.get('class')).lower() 
                       for p in ['advertisement', 'ad-', 'promo']),
            # Social sharing
            lambda tag: tag.get('class') and any('share' in c.lower() for c in tag.get('class', [])),
        ]
        
        for pattern in unwanted_patterns:
            for element in main_content.find_all(pattern):
                element.decompose()
        
        # 4. Smart detection: Remove sections that are link-heavy
        # Strategy: Find all sections/divs recursively and check from bottom up
        body = main_content.find('body') if main_content.find('body') else main_content
        
        # Find ALL sections/divs/footer elements (not just direct children)
        all_sections = body.find_all(['section', 'div', 'footer'], recursive=True)
        
        # Filter to get "container-level" elements (not deeply nested ones)
        # We want elements that don't contain other sections
        candidate_elements = []
        for element in all_sections:
            # Check if this element contains other section-like elements
            nested_sections = element.find_all(['section', 'div', 'footer'], recursive=True)
            # If it has fewer than 3 nested sections, it's a leaf/near-leaf container
            if len(nested_sections) < 3:
                candidate_elements.append(element)
        
        # Sort by position in document (using string position as proxy)
        try:
            candidate_elements.sort(key=lambda x: str(body).find(str(x)[:100]))
        except:
            pass  # If sorting fails, proceed with original order
        
        # Check from the end backwards for navigation/footer sections
        removed_count = 0
        for element in reversed(candidate_elements):
            # Don't remove too many sections
            if removed_count > 5:
                break
                
            text_content = element.get_text(strip=True)
            links = element.find_all('a')
            
            # Skip empty elements
            if not text_content or len(text_content) < 10:
                continue
            
            # Calculate metrics
            link_count = len(links)
            total_text_length = len(text_content)
            link_text_length = sum(len(link.get_text(strip=True)) for link in links)
            link_density = link_text_length / total_text_length if total_text_length > 0 else 0
            
            # Calculate average text per link (indicator of navigation lists)
            avg_text_per_link = total_text_length / link_count if link_count > 0 else float('inf')
            
            # Detect if this is likely a navigation/footer section:
            # Criteria 1: Many links (>15) regardless of density
            # Criteria 2: High link density (>40%) with moderate link count (>8)
            # Criteria 3: Many links (>12) with short average text per link (<80 chars)
            # Criteria 4: Extremely high link density (>60%) 
            is_navigation = (
                (link_count > 15) or
                (link_density > 0.4 and link_count > 8) or
                (link_count > 12 and avg_text_per_link < 80) or
                (link_density > 0.6)
            )
            
            if is_navigation:
                element.decompose()
                removed_count += 1
            else:
                # Once we hit substantial content (not navigation), stop removing
                # A section with >500 chars and <30% link density is likely real content
                if total_text_length > 500 and link_density < 0.3:
                    break
        
        result = str(body) if body else str(main_content)
        return result if result else html
    
    def html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown
        
        Args:
            html: HTML content
            
        Returns:
            Markdown formatted text
        """
        markdown = self.h2t.handle(html)
        
        # Clean up excessive newlines
        lines = markdown.split('\n')
        cleaned_lines = []
        empty_count = 0
        
        for line in lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count <= 2:  # Allow max 2 consecutive empty lines
                    cleaned_lines.append(line)
            else:
                empty_count = 0
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    async def convert_async(self, url: str, output_path: Optional[str] = None) -> tuple[str, str]:
        """Convert URL to Markdown (async version)
        
        Args:
            url: The URL to convert
            output_path: Optional output file path for logging
            
        Returns:
            Tuple of (markdown_content, page_title)
            
        Raises:
            Exception: If conversion fails
        """
        try:
            # Fetch HTML content and crawl4ai's markdown
            html, crawl4ai_markdown = await self.fetch_url(url)
            
            # Strategy: Use crawl4ai markdown with cross-validation cleaning
            if crawl4ai_markdown and len(crawl4ai_markdown.strip()) > 100:
                # Use crawl4ai's markdown
                markdown = crawl4ai_markdown
                
                # Cross-validate with HTML to identify footer sections
                markdown: str = self.cross_validate_clean(markdown, html, output_path)
            else:
                # Fallback: If crawl4ai didn't produce good markdown, use our HTML method
                main_html = self.extract_main_content(html, url)
                markdown = self.html_to_markdown(main_html)
                markdown = self.clean_markdown(markdown)
            
            # Extract page title from cleaned markdown (prefer H1) or HTML <title>
            page_title = self._extract_title_from_markdown(markdown)
            if not page_title or page_title == 'Untitled':
                # Fallback to HTML <title>
                soup = BeautifulSoup(html, 'lxml')
                title = soup.find('title')
                page_title = title.get_text().strip() if title else 'Untitled'
            
            # Add metadata header
            header = f"# {page_title}\n\n"
            header += f"**Source:** {url}\n\n"
            header += "---\n\n"
            
            return header + markdown, page_title
            
        except Exception as e:
            raise Exception(f"Failed to convert content: {e}")
    
    def cross_validate_clean(self, markdown: str, html: str, output_path: Optional[str] = None) -> str:
        """Cross-validate markdown sections with HTML to remove footer/navigation
        
        Strategy:
        1. Parse markdown into sections by headings
        2. For each section, calculate link density in markdown
        3. Find corresponding text in HTML and check link density there too
        4. If both markdown and HTML show high link density, mark as footer
        5. Remove all footer sections from the end
        
        Args:
            markdown: Markdown content from crawl4ai
            html: Original HTML content
            output_path: Optional output file path for logging
            
        Returns:
            Cleaned markdown with footer removed
        """
        # Start logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = self.log_dir / f"clean_{timestamp}.log"
        self.log_file = open(self.log_path, "w", encoding="utf-8")
        
        # Print log file location to console (with flush to ensure immediate output)
        print("\n" + "="*80, flush=True)
        print(f"📋 日志文件: {self.log_path.absolute()}", flush=True)
        print("="*80 + "\n", flush=True)
        
        self._log("="*80)
        self._log("DEBUG: cross_validate_clean() started")
        self._log("="*80)
        self._log(f"Timestamp: {timestamp}")
        self._log(f"Log file: {self.log_path.absolute()}")
        self._log("")
        
        lines = markdown.split('\n')
        
        # Debug: Show first 60 lines of markdown
        self._log("\n--- First 60 lines of input markdown:")
        for i, line in enumerate(lines[:60]):
            preview = line[:100] if len(line) <= 100 else line[:97] + "..."
            self._log(f"  {i:3d}: {preview}")
        
        # STEP 0: Detect and remove header navigation (before article content)
        # Strategy: Find H1 title (article start) or first H2, and remove everything before it
        
        # First, look for H1 title (most reliable article start marker)
        h1_line = None
        first_h2_line = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('# ') and not stripped.startswith('## '):
                h1_line = i
                self._log(f"\n--- Found H1 title at line {i}: {stripped[:50]}...")
                break
        
        # If no H1, find first H2
        if h1_line is None:
            for i, line in enumerate(lines):
                if line.strip().startswith('## '):
                    first_h2_line = i
                    self._log(f"\n--- First ## heading found at line {i}: {line.strip()[:50]}...")
                    break
        
        # Determine content start: prefer H1, fallback to H2
        article_start_line = h1_line if h1_line is not None else first_h2_line
        
        if article_start_line is not None and article_start_line > 10:
            self._log(f"\n--- Analyzing header region (lines 0-{article_start_line})...")
            self._log(f"    Article content starts at line {article_start_line}")
            
            # Parse HTML to verify
            soup = BeautifulSoup(html, 'lxml')
            main_article = None
            main_selectors = ['article', '[role="main"]', 'main', '.post-content', 
                            '.article-content', '.blog-content', '.entry-content']
            for selector in main_selectors:
                main_article = soup.select_one(selector)
                if main_article:
                    self._log(f"    Found main article container: {selector}")
                    break
            
            # Count navigation content before article start
            header_lines = lines[:article_start_line]
            header_text = '\n'.join(header_lines)
            header_link_count = header_text.count('](')
            header_non_empty = [l for l in header_lines if l.strip()]
            
            self._log(f"\n--- Header region (lines 0-{article_start_line}):")
            self._log(f"    Non-empty lines: {len(header_non_empty)}, Links: {header_link_count}")
            
            # Show preview
            self._log(f"    Content preview (first 10 non-empty lines):")
            shown = 0
            for i, line in enumerate(header_lines):
                if line.strip() and shown < 10:
                    self._log(f"      {i}: {line.strip()[:80]}")
                    shown += 1
            
            # Decision: Remove header if it has navigation-like characteristics
            # OR if we found a clear H1 article title
            should_remove = False
            
            if h1_line is not None:
                # If we found H1 title, everything before it is header/nav
                should_remove = True
                reason = "H1 article title found"
            elif header_link_count > 15 or len(header_non_empty) > 20:
                # Many links or many lines suggest navigation
                should_remove = True  
                reason = "High navigation content"
            
            if should_remove:
                self._log(f"    >>> REMOVING header navigation ({reason})")
                markdown = '\n'.join(lines[article_start_line:])
                lines = markdown.split('\n')
            else:
                self._log(f"    -> Keeping header (low navigation content)")
        
        # STEP 1: Remove Table of Contents sections (may appear multiple times)
        # Look for "Contents" or "Table of contents" followed by many links
        toc_removed_count = 0
        lines = markdown.split('\n')
        
        # Keep removing TOCs until we don't find any more
        max_iterations = 5  # Prevent infinite loop
        for iteration in range(max_iterations):
            found_toc = False
            for i, line in enumerate(lines):
                stripped = line.strip().lower()
                # Look for various TOC patterns
                is_toc_heading = (
                    stripped == 'contents' or
                    stripped == 'table of contents' or
                    'table of contents' in stripped
                )
                
                if is_toc_heading:
                    # Check next 50 lines for link density
                    window_end = min(i + 50, len(lines))
                    window_lines = lines[i:window_end]
                    window_text = '\n'.join(window_lines)
                    link_count = window_text.count('](')
                    non_empty = sum(1 for l in window_lines if l.strip())
                    
                    if link_count > 8 and non_empty > 5:
                        # This is a TOC, find where it ends
                        # TOC ends when we hit a ## heading (not ###) or substantial paragraph
                        toc_end = i
                        for j in range(i + 1, window_end):
                            line_j = lines[j].strip()
                            # End of TOC: H2 heading (article content starts)
                            if line_j.startswith('## ') and not line_j.startswith('### '):
                                toc_end = j
                                self._log(f"\n--- Detected TOC at line {i}, ends at line {j}")
                                self._log(f"    Removed {j-i} lines of table of contents")
                                toc_removed_count += 1
                                break
                        
                        # Remove TOC lines
                        if toc_end > i:
                            markdown = '\n'.join(lines[:i] + lines[toc_end:])
                            lines = markdown.split('\n')
                            found_toc = True
                            break
            
            if not found_toc:
                break
        
        # Extract sections from markdown
        sections = self.extract_markdown_sections(markdown)
        
        self._log(f"\nDEBUG: Found {len(sections)} sections (TOCs removed: {toc_removed_count})")
        
        if not sections:
            # No sections found, use simple cleaning
            self._log("DEBUG: No sections found, using clean_markdown fallback")
            self.log_file.close()
            return self.clean_markdown(markdown)
        
        # Parse HTML for cross-validation
        soup = BeautifulSoup(html, 'lxml')
        
        # Mark sections as footer or content
        for idx, section in enumerate(sections):
            heading_text = section['heading'].lstrip('#').strip()
            
            # Calculate link metrics in markdown - CORRECTLY without link text
            content = section['content']
            lines_in_section = content.split('\n')
            non_empty_lines = [l for l in lines_in_section if l.strip()]
            link_lines = [l for l in non_empty_lines if '](' in l]
            
            # NEW: Calculate text length EXCLUDING link text
            text_length_no_links, link_count = self._calculate_text_length_without_links(content)
            
            # Link density metrics
            link_ratio = len(link_lines) / max(1, len(non_empty_lines))  # ratio of lines with links
            links_per_100_chars = link_count / max(1, text_length_no_links / 100)
            
            # Markdown detection: HIGH link density patterns
            md_high_links = (
                link_ratio > 0.6 or 
                links_per_100_chars > 1.5 or
                (link_count > 5 and text_length_no_links < 300) or
                link_count > 8
            )
            
            # Try to find corresponding section in HTML
            html_high_links = False
            
            # Search for heading text in HTML
            if heading_text:
                # Find all elements containing this heading text
                matching_elements = soup.find_all(
                    ['h2', 'h3', 'h4', 'div', 'section'],
                    string=lambda text: text and heading_text.lower() in text.lower()
                )
                
                for element in matching_elements:
                    # Get parent container (go up to find section/div)
                    parent = element.parent if element.parent else element
                    
                    # Try to find a better container
                    for _ in range(3):  # Go up max 3 levels
                        if parent and parent.name in ['section', 'div', 'footer']:
                            break
                        if parent:
                            parent = parent.parent
                    
                    if not parent:
                        continue
                    
                    # Calculate link density in HTML
                    parent_text = parent.get_text(strip=True)
                    parent_links = parent.find_all('a')
                    
                    if parent_text and len(parent_text) > 50:  # Valid section
                        html_link_count = len(parent_links)
                        html_text_length = len(parent_text)
                        html_links_per_100 = html_link_count / max(1, html_text_length / 100)
                        
                        # High link density in HTML (>1.5 links per 100 chars OR >8 links total)
                        if html_links_per_100 > 1.5 or html_link_count > 8:
                            html_high_links = True
                            break
            
            # Calculate additional metrics
            avg_chars_per_link = text_length_no_links / link_count if link_count > 0 else float('inf')
            
            # Check if section heading suggests it's navigation/promotional
            heading_lower = heading_text.lower()
            is_promo_heading = any(keyword in heading_lower for keyword in [
                'training more people', 'get your team', 'for business',
                'develop ai applications', 'start upskilling', 'learn more',
                'related', 'recommended', 'you might also like',
                'see more', 'browse courses', 'grow your'
            ])
            
            is_footer = (
                # Pattern 1: Extremely high link density (>3 links per 100 chars non-link text)
                links_per_100_chars > 3 or
                
                # Pattern 2: Very high link ratio (>70% of lines have links) with many links (>10)
                (link_ratio > 0.7 and link_count > 10) or
                
                # Pattern 3: Many links (>12) with short average context (<80 chars per link)
                (link_count > 12 and avg_chars_per_link < 80) or
                
                # Pattern 4: Both MD and HTML show high link density AND short section (<400 chars)
                (md_high_links and html_high_links and text_length_no_links < 400) or
                
                # Pattern 5: Very short section (<200 chars) with moderate-high link density (>1.5)
                (text_length_no_links < 200 and links_per_100_chars > 1.5) or
                
                # Pattern 6: MANY links (>50) regardless of density - typical footer
                link_count > 50 or
                
                # Pattern 7: Promotional/navigation heading with links
                (is_promo_heading and link_count > 0) or
                
                # Pattern 8: Section with ALL lines being links (100% link ratio, typical related posts)
                (link_ratio >= 1.0 and link_count > 0) or
                
                # Pattern 9: High link density (>0.8 links/100chars) with many links (>5)
                (links_per_100_chars > 0.8 and link_count > 5) or
                
                # Pattern 10: Medium link density (>0.6) with reasonable link count (>3)
                (links_per_100_chars > 0.6 and link_count > 3)
            )
            
            section['is_footer'] = is_footer
            section['in_footer_cascade'] = False  # Initialize, will be set later in cascade detection
            section['link_ratio'] = link_ratio
            section['links_per_100_chars'] = links_per_100_chars
            section['avg_chars_per_link'] = avg_chars_per_link
            section['text_length_no_links'] = text_length_no_links
            section['link_count'] = link_count
            
            # Debug output
            self._log(f"\n--- Section {idx}: {heading_text[:50]}...")
            self._log(f"    Lines: {len(lines_in_section)}, Non-empty: {len(non_empty_lines)}, Link lines: {len(link_lines)}")
            self._log(f"    Link count: {link_count}, Text length (no links): {text_length_no_links}")
            self._log(f"    Link ratio: {link_ratio:.2f}, Links/100chars: {links_per_100_chars:.2f}")
            self._log(f"    Avg chars per link: {avg_chars_per_link:.1f}")
            self._log(f"    MD high links: {md_high_links}, HTML high links: {html_high_links}")
            
            # Debug: Show found links if suspiciously high count
            if link_count > 10:
                found_links = re.findall(r'\[([^\]]+)\]\([^\)]+\)', content)
                self._log(f"    DEBUG: Found {len(found_links)} links:")
                for i, link_text in enumerate(found_links[:15]):  # Show first 15
                    self._log(f"      {i+1}. [{link_text[:50]}...]")
                if len(found_links) > 15:
                    self._log(f"      ... and {len(found_links) - 15} more")
            
            self._log(f"    >>> IS_FOOTER: {is_footer}")
        
        # Post-processing: Detect footer cascade
        self._log(f"\n--- Post-processing: Detecting footer cascade...")
        
        # Strategy: Find continuous footer sections at the END
        # Scan backwards to find where the footer cascade starts
        footer_cascade_start = len(sections)
        consecutive_footer_count = 0
        
        for i in range(len(sections) - 1, -1, -1):
            section = sections[i]
            
            # Check if this is footer or highly link-rich
            is_link_rich = (
                section['is_footer'] or
                (section['links_per_100_chars'] > 1.0 and section['link_count'] > 5) or
                (section['link_ratio'] >= 1.0 and section['link_count'] > 2)
            )
            
            if is_link_rich:
                consecutive_footer_count += 1
                footer_cascade_start = i
            else:
                # Check if this is substantial content
                is_substantial = (
                    section['text_length_no_links'] > 800 or
                    (section['text_length_no_links'] > 400 and section['links_per_100_chars'] < 0.4)
                )
                
                if is_substantial:
                    # Hit substantial content, stop cascade detection
                    self._log(f"  Hit substantial content at section {i}: {section['heading'][:50]}...")
                    self._log(f"  Text length: {section['text_length_no_links']}, Links/100chars: {section['links_per_100_chars']:.2f}")
                    break
                elif consecutive_footer_count > 0:
                    # Non-substantial, non-footer section between content and footer
                    # Don't break the cascade yet, just reset counter
                    consecutive_footer_count = 0
        
        # Only mark sections as footer if we found 2+ consecutive link-rich sections at the end
        # IMPORTANT: Also mark them as in_footer_cascade to distinguish from isolated footer-like sections
        if consecutive_footer_count >= 2:
            self._log(f"  Found {consecutive_footer_count} consecutive footer sections starting at {footer_cascade_start}")
            self._log(f"  Marking sections {footer_cascade_start} to {len(sections) - 1} as footer cascade")
            for i in range(footer_cascade_start, len(sections)):
                sections[i]['in_footer_cascade'] = True
                if not sections[i]['is_footer']:
                    sections[i]['is_footer'] = True
                    self._log(f"    Marked section {i} as footer: {sections[i]['heading'][:40]}...")
        else:
            self._log(f"  No significant footer cascade detected (only {consecutive_footer_count} consecutive)")
            # Mark all sections as NOT in cascade
            for section in sections:
                section['in_footer_cascade'] = False
        
        # Find the cutoff points: 
        # 1. Remove footer sections from the end
        # 2. Find article start (look for H1 title or first non-footer section)
        
        content_start_line = 0
        content_end_line = len(markdown.split('\n'))
        lines = markdown.split('\n')
        
        self._log(f"\n--- Finding content boundaries...")
        
        # Strategy for finding content start:
        # 1. Look for H1 title (# ...) - this marks the true article start
        # 2. If found, start from there
        # 3. If not found, use first non-footer section
        
        article_title_line = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Look for H1 heading (article title)
            if stripped.startswith('# ') and not stripped.startswith('## '):
                article_title_line = i
                self._log(f"Found H1 title at line {i}: {stripped[:50]}...")
                break
        
        if article_title_line is not None:
            # Start from the H1 title
            content_start_line = article_title_line
            self._log(f"Content starts at line {content_start_line} (H1 title)")
        else:
            # Fallback: use first non-footer section
            first_real_section_idx = None
            for i in range(len(sections)):
                if not sections[i]['is_footer']:
                    first_real_section_idx = i
                    break
            
            if first_real_section_idx is not None:
                content_start_line = sections[first_real_section_idx]['start_line']
                self._log(f"Content starts at line {content_start_line} (first non-footer section)")
            else:
                self._log(f"WARNING: No non-footer sections found!")
                content_start_line = 0
        
        # Find content end (remove bottom navigation)
        # IMPORTANT: Only remove sections that are BOTH is_footer=True AND in_footer_cascade=True
        # This prevents removing isolated link-rich sections that have substantial content
        self._log(f"--- Finding content end (scanning backwards)...")
        for i in range(len(sections) - 1, -1, -1):
            in_cascade = sections[i].get('in_footer_cascade', False)
            self._log(f"Section {i}: is_footer={sections[i]['is_footer']}, in_cascade={in_cascade}, heading={sections[i]['heading'][:40]}...")
            if sections[i]['is_footer'] and in_cascade:
                content_end_line = sections[i]['start_line']
                self._log(f"  -> Set end cutoff to line {content_end_line}")
            else:
                # Stop at first section that's not in footer cascade
                self._log(f"  -> Hit non-cascade section, stopping")
                break
        
        # ADDITIONAL CHECK: Look for footer markers within sections
        # These often appear within the last section but mark the start of footer content
        # Check patterns like: H4 headings, "* * *" dividers, "Author" labels, etc.
        if sections:
            # Check all sections marked as is_footer=True but not in cascade
            # Also check the last 10 sections to catch any footer markers
            sections_to_check = []
            for idx, section in enumerate(sections):
                if section['is_footer'] and not section.get('in_footer_cascade', False):
                    sections_to_check.append(idx)
            
            # Also add the last 10 sections (to catch markers in non-footer sections)
            last_n = min(10, len(sections))
            for idx in range(len(sections) - last_n, len(sections)):
                if idx not in sections_to_check:
                    sections_to_check.append(idx)
            
            sections_to_check.sort()  # Process in order
            self._log(f"  Checking sections for footer markers: {sections_to_check}")
            
            for section_idx in sections_to_check:
                section = sections[section_idx]
                
                # Skip if already in footer cascade
                if section.get('in_footer_cascade', False):
                    continue
                
                section_lines = lines[section['start_line']:section['end_line']+1]
                
                for offset, line in enumerate(section_lines):
                    stripped = line.strip()
                    found_footer_marker = False
                    marker_description = ""
                    
                    # Pattern 1: H2/H3/H4 footer headings
                    # H2: Marketing slogans, product taglines (e.g., "Less structure, more intelligence")
                    # H3: Footer categories (e.g., "产品", "资源", "社区", "Product", "Resources")
                    # H4: Article footers (e.g., "Related posts", "Stay updated")
                    if stripped.startswith('## ') or stripped.startswith('### ') or stripped.startswith('#### '):
                        # Determine heading level
                        if stripped.startswith('#### '):
                            heading_text = stripped[5:].lower()
                            heading_level = 'H4'
                        elif stripped.startswith('### '):
                            heading_text = stripped[4:].lower()
                            heading_level = 'H3'
                        else:  # H2
                            heading_text = stripped[3:].lower()
                            heading_level = 'H2'
                        
                        # H4 markers (article-level footer)
                        h4_footer_markers = [
                            'related post', 'related article', 'related content',
                            'stay updated', 'subscribe', 'newsletter',
                            'more from', 'you might also like', 'recommended',
                            'about the author', 'follow us', 'learn more about'
                        ]
                        
                        # H3 markers (site navigation footer categories)
                        h3_footer_markers = [
                            '产品', 'product', 'products',
                            '资源', 'resource', 'resources',
                            '社区', 'community',
                            '公司', 'company', 'about',
                            '下载', 'download', 'downloads',
                            '比较', 'compare', 'comparison',
                            '联系', 'contact', 'contact us',
                            '支持', 'support',
                            '法律', 'legal',
                            '关注', 'follow', 'follow us',
                            'get started', 'quick links',
                            '服务', 'service', 'services'
                        ]
                        
                        # H2 markers (marketing/product slogans)
                        h2_footer_markers = [
                            'less structure', 'more intelligence',
                            'get started', 'start free',
                            'ready to', 'join us',
                            'try', 'free trial'
                        ]
                        
                        # Check if heading matches footer patterns
                        if heading_level == 'H4' and any(marker in heading_text for marker in h4_footer_markers):
                            found_footer_marker = True
                            marker_description = f"H4 heading: {stripped[:60]}"
                        elif heading_level == 'H3' and any(marker == heading_text for marker in h3_footer_markers):
                            found_footer_marker = True
                            marker_description = f"H3 footer category: {stripped[:60]}"
                        elif heading_level == 'H2' and any(marker in heading_text for marker in h2_footer_markers):
                            found_footer_marker = True
                            marker_description = f"H2 footer slogan: {stripped[:60]}"
                    
                    # Pattern 2: Horizontal rule followed by author info
                    # Look for "* * *" or "---" followed by "Author" or author image
                    if stripped in ['* * *', '---', '***', '* * * *']:
                        # Check next few lines for author indicators
                        for next_offset in range(offset + 1, min(offset + 5, len(section_lines))):
                            next_line = section_lines[next_offset].strip().lower()
                            if any(indicator in next_line for indicator in ['author', '![', 'topics', 'categories']):
                                found_footer_marker = True
                                marker_description = f"Divider + author info at offset {offset}"
                                break
                    
                    # Pattern 3: Standalone "Author" or "Topics" line (common in blog posts)
                    if stripped.lower() in ['author', 'topics', 'categories', 'tags', 'share this']:
                        found_footer_marker = True
                        marker_description = f"Footer label: {stripped}"
                    
                    if found_footer_marker:
                        footer_start_line = section['start_line'] + offset
                        self._log(f"\n  -> Found footer marker in section {section_idx} at line {footer_start_line}: {marker_description}")
                        
                        # Verify this is actually footer content (check remaining content)
                        remaining_lines = section_lines[offset:]
                        remaining_text = '\n'.join(remaining_lines)
                        remaining_text_no_links, remaining_links = self._calculate_text_length_without_links(remaining_text)
                        
                        # For author/topics markers, be more lenient
                        is_definitely_footer = (
                            remaining_links > 5 or  # Has links (social media, related articles, etc.)
                            'author' in marker_description.lower() or
                            'topics' in marker_description.lower() or
                            'divider' in marker_description.lower()
                        )
                        
                        if is_definitely_footer:
                            content_end_line = footer_start_line
                            self._log(f"     >>> Cutting at footer marker (line {footer_start_line})")
                            # Stop checking once we found and cut
                            break
                
                # If we found a marker and cut, stop checking other sections
                if content_end_line < len(lines):
                    break
        
        self._log(f"\nContent range: lines {content_start_line} to {content_end_line}")
        
        # Extract content between start and end
        lines = markdown.split('\n')
        result_lines = lines[content_start_line:content_end_line]
        
        # Clean up trailing empty lines
        while result_lines and not result_lines[-1].strip():
            result_lines.pop()
        
        self._log(f"Result lines: {len(result_lines)} (from {len(lines)})")
        self._log("="*80 + "\n")
        
        # Close log file
        self.log_file.close()
        
        return '\n'.join(result_lines)
    
    def extract_markdown_sections(self, markdown: str) -> list[dict]:
        """Extract sections from markdown with their metadata
        
        Args:
            markdown: Markdown content
            
        Returns:
            List of section dicts with keys: start_line, end_line, heading, content, link_count
        """
        lines = markdown.split('\n')
        sections = []
        current_section = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Detect H2/H3 headings
            if stripped.startswith('## ') or stripped.startswith('### '):
                # Save previous section
                if current_section:
                    current_section['end_line'] = i - 1
                    current_section['content'] = '\n'.join(lines[current_section['start_line']:i])
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'start_line': i,
                    'end_line': len(lines) - 1,
                    'heading': stripped,
                    'level': 2 if stripped.startswith('## ') else 3
                }
        
        # Save last section
        if current_section:
            current_section['end_line'] = len(lines) - 1
            current_section['content'] = '\n'.join(lines[current_section['start_line']:])
            sections.append(current_section)
        
        # Calculate link density for each section (link_count will be calculated separately)
        for section in sections:
            content = section['content']
            # Basic link count (will be recalculated more accurately in cross_validate_clean)
            section['link_count'] = content.count('](')
            section['text_length'] = len(content.strip())  # Keep for now for compatibility
            section['link_density'] = section['link_count'] / max(1, section['text_length'] / 100)
            
        return sections
    
    def clean_markdown(self, markdown: str) -> str:
        """Clean up markdown content by removing navigation and unwanted elements
        
        Focus on markdown-level patterns to remove footer/navigation sections.
        
        Args:
            markdown: Raw markdown content
            
        Returns:
            Cleaned markdown
        """
        lines = markdown.split('\n')
        
        # Step 1: Find content start (remove top navigation if present)
        content_start_idx = 0
        found_content = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            # Found substantial paragraph (likely article content)
            if (len(line_stripped) > 150 and 
                not line_stripped.startswith('[') and 
                not line_stripped.startswith('*') and
                line_stripped.count('](') < 3):
                
                lookback = min(30, i)
                short_count = sum(1 for j in range(max(0, i-lookback), i) 
                                 if lines[j].strip() and len(lines[j].strip()) < 100)
                
                if short_count >= 10:
                    content_start_idx = i
                    found_content = True
                    break
            
            # Or heading + paragraph pattern
            if line_stripped.startswith('#'):
                for j in range(i+1, min(i+10, len(lines))):
                    if len(lines[j].strip()) > 150 and lines[j].strip().count('](') < 3:
                        lookback = min(30, i)
                        short_count = sum(1 for k in range(max(0, i-lookback), i)
                                         if lines[k].strip() and len(lines[k].strip()) < 100)
                        if short_count >= 10:
                            content_start_idx = i
                            found_content = True
                            break
                if found_content:
                    break
        
        # Step 2: Find content end (critical for removing bottom navigation)
        content_end_idx = len(lines)
        
        # Scan backwards to find footer start
        # Look for characteristic patterns of footer sections
        for i in range(len(lines) - 1, max(content_start_idx + 20, 0), -1):
            line = lines[i].strip()
            
            # Pattern 1: H2/H3 heading followed by many links in next lines
            if line.startswith('##'):
                # Check the next 25 lines for link density
                window_end = min(i + 25, len(lines))
                window_lines = lines[i:window_end]
                
                # Count lines with links
                link_lines = sum(1 for l in window_lines if l.strip() and '](' in l)
                heading_lines = sum(1 for l in window_lines if l.strip().startswith('###'))
                non_empty = sum(1 for l in window_lines if l.strip())
                
                # Footer pattern: multiple headings + many link lines
                # If >40% are link lines AND we have multiple sub-headings
                if non_empty > 5:
                    link_ratio = link_lines / non_empty
                    if (link_ratio > 0.4 and heading_lines >= 2) or (link_ratio > 0.5):
                        content_end_idx = i
                        break
            
            # Pattern 2: Multiple consecutive lines with multiple links each
            # (footer navigation lists pattern)
            if i > content_start_idx + 30:
                # Look at 10-line window
                window_start = max(content_start_idx, i - 10)
                window_lines = lines[window_start:i+1]
                
                # Count lines with 2+ links (navigation list pattern)
                multi_link_lines = sum(1 for l in window_lines 
                                      if l.strip() and l.count('](') >= 2)
                non_empty = sum(1 for l in window_lines if l.strip())
                
                # If >70% of lines have multiple links, it's likely footer
                if non_empty > 5 and multi_link_lines / non_empty > 0.7:
                    content_end_idx = window_start
                    break
        
        # Step 3: Additional validation - don't cut article conclusion
        # Make sure we're not cutting into article content
        if content_end_idx < len(lines):
            # Check if we're cutting off substantial paragraphs
            # Look back from cut point to see if there's real content
            check_back = 10
            for i in range(max(content_end_idx - check_back, content_start_idx), content_end_idx):
                line = lines[i].strip()
                # If we find a substantial paragraph (>200 chars, few links)
                # before the cut point, we might be cutting real content
                if len(line) > 200 and line.count('](') <= 1:
                    # This looks like article content, be more conservative
                    # Re-scan forward to find a better cut point
                    for j in range(i + 1, min(i + 30, len(lines))):
                        check_line = lines[j].strip()
                        # Look for clear footer markers
                        if (check_line.startswith('##') and 
                            j + 5 < len(lines) and
                            sum(1 for k in range(j, min(j+10, len(lines))) 
                                if lines[k].strip() and '](' in lines[k]) >= 5):
                            content_end_idx = j
                            break
                    break
        
        # Extract main content
        result_lines = []
        empty_count = 0
        
        for i in range(content_start_idx, content_end_idx):
            line = lines[i]
            
            if not line.strip():
                empty_count += 1
                if empty_count <= 2:  # Max 2 consecutive empty lines
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines).strip()
    
    def log_final_output(self, output_path: str):
        """Prepend the final output file path to the log file
        
        Args:
            output_path: The final saved markdown file path
        """
        if self.log_path and self.log_path.exists():
            # Read existing log content
            with open(self.log_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            # Write the output path at the beginning, then append existing content
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write(f"Saved to: {output_path}\n")
                f.write("="*80 + "\n\n")
                f.write(existing_content)
    
    def convert(self, url: str, output_path: Optional[str] = None) -> tuple[str, str]:
        """Convert URL to Markdown (sync wrapper)
        
        Args:
            url: The URL to convert
            output_path: Optional output file path for logging
            
        Returns:
            Tuple of (markdown_content, page_title)
            
        Raises:
            Exception: If conversion fails
        """
        # Run the async conversion
        return asyncio.run(self.convert_async(url, output_path))
