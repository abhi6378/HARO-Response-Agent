import requests
import datetime
from io import BytesIO
from pypdf import PdfReader
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ResearcherAgent:
    def __init__(self, serp_api_key, openai_key):
        self.serp_api_key = serp_api_key
        self.openai_key = openai_key

    def is_high_dr(self, link):
        """Checks if a domain is likely High DR (Authority)."""
        high_authority_domains = [
            ".gov", ".edu", "forbes.com", "techcrunch.com", "bloomberg.com",
            "nytimes.com", "wsj.com", "hbr.org", "mckinsey.com", "gartner.com",
            "statista.com", "hubspot.com", "salesforce.com", "adobe.com",
            "bbc.com", "reuters.com", "investopedia.com", "nature.com"
        ]
        for domain in high_authority_domains:
            if domain in link:
                return True
        return False

    def search_web(self, query):
        """Fetches High DR web results via SerpApi."""
        if not self.serp_api_key:
            return "ERROR: SERP API Key is missing.", []

        print(f" [WEB] Searching High DR sources for: '{query}'")
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.serp_api_key,
                "num": 10
            }
            response = requests.get("https://serpapi.com/search", params=params)
            results = response.json()

            if "error" in results:
                return f"SerpApi Error: {results['error']}", []

            organic_results = results.get("organic_results", [])
            high_dr_findings = []
            normal_findings = []
            links_log = []

            for result in organic_results:
                title = result.get("title")
                link = result.get("link")
                snippet = result.get("snippet")
                entry = f"Source: {title} ({link})\nFact: {snippet}\n"
                
                links_log.append(link)

                if self.is_high_dr(link):
                    high_dr_findings.append(entry)
                else:
                    normal_findings.append(entry)

            # Prioritize High DR
            final_output = "--- HIGH AUTHORITY SOURCES ---\n" + ("\n".join(high_dr_findings) if high_dr_findings else "None")
            final_output += "\n\n--- GENERAL SOURCES ---\n" + "\n".join(normal_findings[:3])
            
            return final_output, links_log

        except Exception as e:
            return f"Web Search Failed: {str(e)}", []

    def search_google_scholar(self, query, start_year=None):
        """
        Fetches papers via Google Scholar (SerpApi) and scrapes PDF content.
        Stops after successfully getting content from 2 papers.
        """
        if not self.serp_api_key:
            return "No SERP Key provided.", []

        # Default to last year if no year provided
        if not start_year:
            start_year = datetime.datetime.now().year - 1

        print(f" [SCHOLAR] Searching papers from {start_year}...")

        # --- 1. Robust Session Setup ---
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://scholar.google.com/'
        }

        # --- 2. Search Params ---
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": self.serp_api_key,
            "as_ylo": start_year,
            "hl": "en",
            "num": 10 
        }

        try:
            response = requests.get("https://serpapi.com/search", params=params)
            results = response.json()
            organic_results = results.get("organic_results", [])

            paper_contents = []
            successful_links = []

            for index, result in enumerate(organic_results):
                # Stop if we have 2 good papers
                if len(paper_contents) >= 2:
                    break

                title = result.get("title")
                print(f"   Processing Paper: {title}")

                # Find PDF Link
                pdf_url = None
                if "resources" in result:
                    for resource in result["resources"]:
                        if resource.get("file_format") == "PDF":
                            pdf_url = resource.get("link")
                            break
                
                if not pdf_url:
                    continue

                # --- 3. Download & Extract ---
                try:
                    pdf_res = session.get(pdf_url, headers=headers, timeout=15, stream=True)
                    
                    if pdf_res.status_code == 200:
                        pdf_file = BytesIO()
                        for chunk in pdf_res.iter_content(chunk_size=8192):
                            if chunk:
                                pdf_file.write(chunk)
                        pdf_file.seek(0)
                        
                        reader = PdfReader(pdf_file)
                        if len(reader.pages) > 0:
                            # Extract first 2 pages max
                            text = ""
                            for i in range(min(2, len(reader.pages))):
                                text += reader.pages[i].extract_text()
                            
                            clean_text = text.replace('\n', ' ')[:2500] 
                            
                            paper_contents.append(f"Paper: {title} ({start_year}+)\nContent: {clean_text}...\n")
                            successful_links.append(f"{title}: {pdf_url}")
                            print(f"     [+] Successfully extracted: {title}")
                        else:
                            print("     [x] Empty PDF.")
                    else:
                        print(f"     [x] Failed to download {pdf_url} (Status: {pdf_res.status_code})")

                except Exception as e:
                    print(f"     [x] Error processing PDF: {e}")
                    continue

            final_text = "\n".join(paper_contents) if paper_contents else "No accessible PDF content found."
            return final_text, successful_links

        except Exception as e:
            return f"Scholar Search Failed: {str(e)}", []

    def summarize_findings(self, query, web_data, academic_data):
        """
        Uses OpenAI (GPT-4o-mini) to compress research into a Brief.
        """
        if not self.openai_key:
            return f"OpenAI Key Missing. Raw Data:\n{web_data}\n{academic_data}"

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            ROLE: Lead Research Analyst.
            TASK: Synthesize the provided raw research into a structured **Research Brief** (500-600 words).
            QUERY: "{query}"
            
            RAW WEB DATA:
            {web_data}
            
            RAW ACADEMIC PAPERS (Google Scholar PDFs):
            {academic_data}
            
            ### OUTPUT GUIDELINES:
            1. **Consolidate:** Merge similar points from web and academic sources.
            2. **Authority:** Highlight stats and facts from the High DR sources and Scholar Papers.
            3. **Structure:**
               - **Executive Summary** (50 words)
               - **Key Trends & Statistics** (Bullet points)
               - **Academic/Deep Insights** (Specific findings from the papers)
               - **Strategic Angle** (What is the unique insight here?)
            4. **Length:** Strictly 500-600 words.
            """
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a research analyst summarizing complex data."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            return f"Summarization Failed: {str(e)}"

    def fetch_data(self, query, strategy, year=None):
        # 1. Gather Raw Data
        web_text, web_links = self.search_web(query)
        scholar_text, scholar_links = self.search_google_scholar(query, year)
        
        # 2. Synthesize/Summarize
        research_brief = self.summarize_findings(query, web_text, scholar_text)
        
        # 3. Compile Logs for Flask
        all_logs = {
            "web_links": web_links,
            "scholar_links": scholar_links
        }
        
        return research_brief, all_logs