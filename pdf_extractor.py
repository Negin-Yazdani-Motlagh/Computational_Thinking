import json
import requests
import time
import re
import urllib.parse
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Paper:
    title: str
    year: int
    venue: str
    url: str
    citations: int
    pdf: Optional[str] = None

class PDFExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Rate limiting
        self.request_delay = 1  # seconds between requests
        self.last_request_time = 0
        
        # Statistics
        self.stats = {
            'total_papers': 0,
            'papers_with_pdfs': 0,
            'papers_without_pdfs': 0,
            'pdfs_found': 0,
            'pdfs_not_found': 0
        }

    def rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    def clean_title_for_search(self, title: str) -> str:
        """Clean title for better search results."""
        # Remove special characters and normalize
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    def search_semantic_scholar(self, title: str, year: int) -> Optional[str]:
        """Search Semantic Scholar API for PDF links."""
        try:
            self.rate_limit()
            
            # Clean title for search
            clean_title = self.clean_title_for_search(title)
            
            # Search using Semantic Scholar API
            search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': clean_title,
                'year': f"{year-1}-{year+1}",  # Allow 1 year flexibility
                'fields': 'title,year,openAccessPdf,url,externalIds',
                'limit': 5
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for paper in data.get('data', []):
                    # Check if titles match closely
                    paper_title = paper.get('title', '').lower()
                    search_title = clean_title.lower()
                    
                    # Simple similarity check
                    if self.titles_similar(paper_title, search_title):
                        # Check for open access PDF
                        open_access = paper.get('openAccessPdf')
                        if open_access and open_access.get('url'):
                            logger.info(f"Found PDF via Semantic Scholar: {title}")
                            return open_access['url']
                            
        except Exception as e:
            logger.warning(f"Semantic Scholar search failed for '{title}': {e}")
        
        return None

    def search_arxiv(self, title: str, year: int) -> Optional[str]:
        """Search arXiv for papers."""
        try:
            self.rate_limit()
            
            clean_title = self.clean_title_for_search(title)
            
            # arXiv API search
            search_url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f'ti:"{clean_title}"',
                'start': 0,
                'max_results': 5
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    entry_title = entry.find('{http://www.w3.org/2005/Atom}title')
                    if entry_title is not None:
                        if self.titles_similar(entry_title.text.lower(), clean_title.lower()):
                            # Get PDF link
                            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                                if link.get('type') == 'application/pdf':
                                    pdf_url = link.get('href')
                                    logger.info(f"Found PDF via arXiv: {title}")
                                    return pdf_url
                                    
        except Exception as e:
            logger.warning(f"arXiv search failed for '{title}': {e}")
        
        return None

    def search_crossref(self, title: str, year: int) -> Optional[str]:
        """Search CrossRef for DOI and potential PDF links."""
        try:
            self.rate_limit()
            
            clean_title = self.clean_title_for_search(title)
            
            # CrossRef API search
            search_url = "https://api.crossref.org/works"
            params = {
                'query': clean_title,
                'rows': 5,
                'filter': f'from-pub-date:{year-1},until-pub-date:{year+1}'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('message', {}).get('items', []):
                    item_title = ' '.join(item.get('title', []))
                    
                    if self.titles_similar(item_title.lower(), clean_title.lower()):
                        # Check for open access links
                        links = item.get('link', [])
                        for link in links:
                            if link.get('content-type') == 'application/pdf':
                                logger.info(f"Found PDF via CrossRef: {title}")
                                return link.get('URL')
                                
        except Exception as e:
            logger.warning(f"CrossRef search failed for '{title}': {e}")
        
        return None

    def search_google_scholar_scrape(self, title: str, year: int) -> Optional[str]:
        """Scrape Google Scholar for PDF links (use with caution due to rate limits)."""
        try:
            self.rate_limit()
            time.sleep(random.uniform(2, 5))  # Extra delay for Google Scholar
            
            clean_title = self.clean_title_for_search(title)
            
            # Google Scholar search URL
            query = f'"{clean_title}" filetype:pdf'
            search_url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(search_url, headers=headers, timeout=15)
            if response.status_code == 200:
                # Simple regex to find PDF links
                pdf_pattern = r'href="([^"]*\.pdf[^"]*)"'
                matches = re.findall(pdf_pattern, response.text)
                
                for match in matches:
                    if 'scholar.google' not in match and match.startswith('http'):
                        logger.info(f"Found PDF via Google Scholar scraping: {title}")
                        return match
                        
        except Exception as e:
            logger.warning(f"Google Scholar scraping failed for '{title}': {e}")
        
        return None

    def resolve_doi_to_pdf(self, paper_url: str) -> Optional[str]:
        """Try to resolve DOI or paper URL to find PDF."""
        try:
            # Extract DOI if present
            doi_pattern = r'10\.\d{4,}/[^\s]+'
            doi_match = re.search(doi_pattern, paper_url)
            
            if doi_match:
                doi = doi_match.group()
                # Try Unpaywall API
                unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email=researcher@example.com"
                
                self.rate_limit()
                response = self.session.get(unpaywall_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('is_oa') and data.get('best_oa_location'):
                        pdf_url = data['best_oa_location'].get('url_for_pdf')
                        if pdf_url:
                            logger.info(f"Found PDF via Unpaywall: {doi}")
                            return pdf_url
                            
        except Exception as e:
            logger.warning(f"DOI resolution failed for '{paper_url}': {e}")
        
        return None

    def titles_similar(self, title1: str, title2: str, threshold: float = 0.7) -> bool:
        """Check if two titles are similar enough."""
        # Simple word-based similarity
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold

    def find_pdf_for_paper(self, paper: Paper) -> Optional[str]:
        """Try multiple methods to find PDF for a paper."""
        if paper.pdf:  # Already has PDF
            return paper.pdf
            
        logger.info(f"Searching for PDF: {paper.title} ({paper.year})")
        
        # Try different search methods in order of reliability
        search_methods = [
            self.search_semantic_scholar,
            self.search_arxiv,
            self.search_crossref,
            lambda title, year: self.resolve_doi_to_pdf(paper.url),
            # self.search_google_scholar_scrape,  # Uncomment with caution
        ]
        
        for method in search_methods:
            try:
                if method == self.resolve_doi_to_pdf:
                    pdf_url = method(paper.url)
                else:
                    pdf_url = method(paper.title, paper.year)
                    
                if pdf_url:
                    # Validate PDF URL
                    if self.validate_pdf_url(pdf_url):
                        return pdf_url
                        
            except Exception as e:
                logger.warning(f"Search method failed: {e}")
                continue
        
        logger.info(f"No PDF found for: {paper.title}")
        return None

    def validate_pdf_url(self, url: str) -> bool:
        """Validate that URL points to an accessible PDF."""
        try:
            self.rate_limit()
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            # Check if it's a PDF or if content-type suggests PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type or url.lower().endswith('.pdf'):
                return response.status_code == 200
                
        except Exception as e:
            logger.warning(f"PDF validation failed for {url}: {e}")
        
        return False

    def process_papers_file(self, input_file: str, output_file: str, max_workers: int = 3):
        """Process papers file and find missing PDFs."""
        logger.info(f"Loading papers from {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            papers_data = json.load(f)
        
        papers = [Paper(**paper_data) for paper_data in papers_data]
        
        # Filter papers without PDFs
        papers_without_pdfs = [p for p in papers if not p.pdf]
        
        self.stats['total_papers'] = len(papers)
        self.stats['papers_with_pdfs'] = len(papers) - len(papers_without_pdfs)
        self.stats['papers_without_pdfs'] = len(papers_without_pdfs)
        
        logger.info(f"Total papers: {self.stats['total_papers']}")
        logger.info(f"Papers with PDFs: {self.stats['papers_with_pdfs']}")
        logger.info(f"Papers without PDFs: {self.stats['papers_without_pdfs']}")
        
        # Process papers to find PDFs
        logger.info("Starting PDF search...")
        
        # Use threading for parallel processing (with rate limiting)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_paper = {
                executor.submit(self.find_pdf_for_paper, paper): paper 
                for paper in papers_without_pdfs[:100]  # Limit to first 100 for testing
            }
            
            for future in as_completed(future_to_paper):
                paper = future_to_paper[future]
                try:
                    pdf_url = future.result()
                    if pdf_url:
                        paper.pdf = pdf_url
                        self.stats['pdfs_found'] += 1
                    else:
                        self.stats['pdfs_not_found'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing {paper.title}: {e}")
                    self.stats['pdfs_not_found'] += 1
        
        # Convert back to dict format and save
        updated_papers = []
        for paper in papers:
            updated_papers.append({
                'title': paper.title,
                'year': paper.year,
                'venue': paper.venue,
                'url': paper.url,
                'citations': paper.citations,
                'PDF': paper.pdf
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_papers, f, indent=2, ensure_ascii=False)
        
        # Print final statistics
        logger.info("\n" + "="*50)
        logger.info("PDF EXTRACTION RESULTS")
        logger.info("="*50)
        logger.info(f"Total papers processed: {self.stats['total_papers']}")
        logger.info(f"Papers with existing PDFs: {self.stats['papers_with_pdfs']}")
        logger.info(f"Papers without PDFs: {self.stats['papers_without_pdfs']}")
        logger.info(f"New PDFs found: {self.stats['pdfs_found']}")
        logger.info(f"PDFs not found: {self.stats['pdfs_not_found']}")
        logger.info(f"Success rate: {(self.stats['pdfs_found'] / max(1, self.stats['papers_without_pdfs'])) * 100:.1f}%")
        logger.info(f"Updated file saved as: {output_file}")

def main():
    """Main function to run PDF extraction."""
    extractor = PDFExtractor()
    
    input_file = "top_50_venues_papers.json"
    output_file = "top_50_venues_papers_with_pdfs.json"
    
    extractor.process_papers_file(input_file, output_file, max_workers=2)

if __name__ == "__main__":
    main() 
