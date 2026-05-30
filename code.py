import json
import logging
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AhmedabadPipeline")


API_KEY = "API KEY HERE"
CURRENT_MODEL = "gemini-3.5-flash"

def extract_website_text(domain: str) -> str:
    """Fetches and cleans website content for LLM ingestion."""
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"
        
    try:

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(domain, headers=headers, timeout=12, allow_redirects=True)
        
        if response.status_code != 200:
            logger.warning(f"Skipping {domain}: HTTP Status {response.status_code}")
            return ""
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        
        for tag in soup(["script", "style", "header", "footer", "nav", "meta"]):
            tag.decompose()
            
        text_data = soup.get_text(separator=" ", strip=True)
        return text_data[:3500] 
        
    except Exception as e:
        logger.error(f"Failed to scrape {domain}: {str(e)}")
        return ""

def verify_icp_gates(company: str, website_text: str, model_name: str = CURRENT_MODEL) -> dict:
    """Queries the Gemini REST API to evaluate the two core eligibility gates."""
    if not website_text:
        return {
            "E1_Status": "FAIL", "E1_Evidence": "No website data available.",
            "E2_Status": "FAIL", "E2_Evidence": "No website data available."
        }

    prompt = f"""
    You are an expert B2B qualification analyst verifying targets for an industrial ICP.
    Analyze this text extracted from the company website for '{company}':
    ---
    {website_text}
    ---
    Evaluate strict compliance against these two rules:
    Rule 1 (E1: Producer): Does this company manufacture physical items, chemical formulations, or provide specialized proprietary in-house engineering? Mark FAIL if they are purely a distributor, trading firm, CRO, or IT consultancy.
    Rule 2 (E2: Accessible): Is their production facility, plant, or corporate headquarters located inside India?
    
    Return ONLY a raw JSON object with this structure (no markdown formatting or backticks):
    {{
        "E1_Status": "PASS or FAIL",
        "E1_Evidence": "A direct, short sentence explaining what they produce in-house.",
        "E2_Status": "PASS or FAIL",
        "E2_Evidence": "A brief sentence identifying their factory or office presence in India."
    }}
    """
    
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "response_mime_type": "application/json"
        }
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        response_data = response.json()
        
       
        if "error" in response_data:
            error_msg = response_data["error"].get("message", "")
            logger.error(f"API Error response: {error_msg}")
            
          
            if "not found" in error_msg and model_name == "gemini-3.5-flash":
                logger.info("Switching endpoint to gemini-2.5-flash fallback...")
                return verify_icp_gates(company, website_text, model_name="gemini-2.5-flash")
                
            return {"E1_Status": "ERROR", "E1_Evidence": error_msg, "E2_Status": "ERROR", "E2_Evidence": error_msg}
            
        raw_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw_text)
        
    except Exception as e:
        logger.error(f"LLM processing failure for {company}: {str(e)}")
        return {"E1_Status": "ERROR", "E1_Evidence": "Parsing failed.", "E2_Status": "ERROR", "E2_Evidence": "Parsing failed."}

def run_sourcing_pipeline(target_list: list, output_csv: str):
    """Loops through targets, qualifies them, and exports a standardized DataFrame."""
    logger.info("Initializing Ahmedabad industrial pipeline execution...")
    processed_records = []
    
    for company in target_list:
        logger.info(f"Processing target: {company['name']}")
        
        web_context = extract_website_text(company["url"])
        gate_results = verify_icp_gates(company["name"], web_context)
        
      
        row = {
            "Company name": company["name"],
            "Website": company["url"],
            "City / Location": company.get("city", "Ahmedabad"),
            "Segment": company.get("segment", "Unknown"),
            "What they make": "Pending Manual Review",
            "Revenue band (estimate)": "Pending Manual Review",
            "Decision-maker": "Pending Manual Review",
            "E1: Producer": f"{gate_results.get('E1_Status', 'ERROR')} - {gate_results.get('E1_Evidence', '')}",
            "E2: Accessible": f"{gate_results.get('E2_Status', 'ERROR')} - {gate_results.get('E2_Evidence', '')}",
            "Overall Federer Score": "Pending Manual Review",
            "Overall verdict": "Pending Manual Review",
            "Personalization hook": "Pending Manual Review"
        }
        processed_records.append(row)
        
     
        time.sleep(2)

    df = pd.DataFrame(processed_records)
    df.to_csv(output_csv, index=False)
    logger.info(f"Execution complete. Output saved to: {output_csv}")


if __name__ == "__main__":
  
    ahmedabad_targets = [
        {"name": "Troikaa Pharmaceuticals", "url": "troikaa.com", "city": "Ahmedabad", "segment": "Basket B - Complex APIs"},
        {"name": "Dynemic Products", "url": "dynemic.com", "city": "Ahmedabad", "segment": "Basket A - Specialty Chem"},
        {"name": "Veeda Clinical Research", "url": "veedacr.com", "city": "Ahmedabad", "segment": "Test Case - Fails E1 (CRO)"}
    ]
    
    output_file_name = "Ahmedabad_DeepThought_Targets.csv"
    run_sourcing_pipeline(ahmedabad_targets, output_file_name)