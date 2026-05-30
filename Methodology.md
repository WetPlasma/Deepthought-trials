# Research Methodology: Target Company Sourcing (Ahmedabad Hub)
### DeepThought Business Analytics Internship — Part A

---

## 1. Geographic and Segment Strategy
**Chosen City:** Ahmedabad, Gujarat
**Chosen Segments:** * Basket A (Custom synthesis & specialty chemicals)
* Basket B (Complex APIs & regulated pharma)

**Justification:** Ahmedabad is a powerhouse for India's pharmaceutical and specialty chemical manufacturing. The region has a high density of promoter-driven MSMEs operating within the Rs.50Cr–Rs.500Cr revenue band. The Gujarat industrial ecosystem is heavily focused on capacity expansion and export compliance (USFDA, EU-GMP), which naturally aligns with the high-growth, systems-driven "Federer" profile DeepThought is targeting.

## 2. Sourcing the Raw Universe
To avoid generic IT or massive conglomerate results, I bypassed standard Google searches and sourced the initial target list using domain-specific registries:
* **DSIR Directory Search:** Extracted companies headquartered in Gujarat with recognized in-house R&D units (a strong proxy for the C3 Differentiation score).
* **Gujarat FDCA & USFDA Databases:** Cross-referenced pharma manufacturers in Ahmedabad with recent regulatory approvals to signal export tailwinds and systems maturity.
* **Tofler Advanced Filtering:** Filtered the resulting lists strictly for active private/unlisted public companies falling within the Rs.50Cr–Rs.500Cr operating revenue band.

## 3. The Automation Pipeline (E1 & E2 Gates)
To efficiently process the raw universe at scale without wasting manual hours on unqualified targets, I built a custom Python qualification pipeline (`dt_sourcing_pipeline.py`). 

**How the script works:**
1. **Extraction:** It uses `BeautifulSoup` with custom User-Agent headers to scrape the target company's website, stripping out non-contextual HTML (headers, footers, scripts) to extract clean text data.
2. **AI Qualification:** The text is passed to the Google Gemini REST API using a highly constrained prompt. 
3. **Strict Evaluation:** The LLM acts as an ICP analyst, strictly evaluating the text against DeepThought's two core eligibility gates:
   * **E1 (Producer):** It ensures the company actually manufactures physical goods in-house. I explicitly programmed it to flag and FAIL service companies, IT consultancies, and Contract Research Organizations (CROs).
   * **E2 (Accessible):** It verifies the presence of physical facilities in India.
4. **Structured Output:** The pipeline forces a JSON response and compiles the results into a structured Pandas DataFrame, ready for deep scoring.

*Note: In testing, the pipeline successfully identified that a company like Veeda Clinical Research, despite operating in the life sciences space, is a CRO (service provider) and correctly failed it at the E1 gate, preventing wasted research time.*

## 4. Deep Scoring and Human QA (C3-C8)
While AI is excellent at binary classification (E1/E2), LLMs are prone to hallucinating financial data and specific founder credentials. Therefore, the E1/E2-qualified list was evaluated manually for the remaining Federer criteria:
* **Differentiation (C3) & Tech DM (C4):** Verified by manually checking founder LinkedIn profiles for academic credentials and checking corporate sites for proprietary equipment or patents.
* **Growth Signals (C6) & Systems Maturity (C7):** Verified by checking recent news for facility expansions, MCA filings for revenue growth, and career pages for ERP/SAP hiring signals.

## 5. Key Learnings About the Segment
* **The "Generic" Trap:** Ahmedabad has hundreds of pharma manufacturers, but many are bulk generic producers with zero differentiation (commodity players). It requires careful reading of their product pages to separate generic API manufacturers from those doing complex/custom synthesis.
* **The "Service" Trap:** The life sciences sector is full of analytical testing labs and clinical trial managers. Using AI to auto-filter these out at the E1 stage saved roughly 40% of the manual research time.