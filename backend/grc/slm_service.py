import json
try:
    from langchain_ollama import OllamaLLM
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: langchain_ollama not available, falling back to mock analysis")
import random
import traceback

def analyze_security_incident(incident_description):
    try:
        # Check if Ollama is available
        if not OLLAMA_AVAILABLE:
            print("Ollama not available, using fallback analysis")
            return generate_fallback_analysis(incident_description)
            
        # Initialize the local SLM model
        llm = OllamaLLM(model="mistral:7b-instruct", temperature=0.7)
       
        prompt_template = PromptTemplate.from_template("""
        You are a cybersecurity expert specializing in analyzing security incidents for a bank's Governance, Risk, and Compliance (GRC) system.
       
        Analyze the following security incident and provide a comprehensive risk assessment in JSON format with these fields:
       
        1. "criticality": The severity level of the incident (Severe, Significant, Moderate, Minor) - define how serious the incident is to bank operations
        2. "possibleDamage": Potential harm that could result from this incident
        3. "category": The type of security incident (e.g., Data Breach, Malware, Phishing, Unauthorized Access)
        4. "riskDescription": A brief explanation of the risk scenario in cause-effect format (e.g., "If X occurs, then Y happens")
        5. "riskLikelihood": Probability of the risk occurring before any response (Highly Probable, Probable, Possible, Unlikely, Remote) - estimate of how likely the threat will materialize
        6. "riskImpact": Potential consequences if no additional response is provided (Catastrophic, Major, Moderate, Minor, Negligible) - measures the potential damage to the bank if the risk occurs
        7. "riskExposureRating": Overall calculation of risk exposure based on likelihood and impact (Critical Exposure, High Exposure, Elevated Exposure, Low Exposure) - combined rating showing total risk posture
        8. "riskPriority": Relative indicator of criticality in the risk register (P0, P1, P2, P3)
        9. "riskAppetite": Assessment of whether this risk falls within the bank's acceptable tolerance levels (Within Appetite, Borderline, Exceeds Appetite) with consideration of regulatory thresholds, capital requirements, and operational risk frameworks
        10. "riskMitigation": Array of numbered step-by-step actions to resolve and mitigate this incident, specifically for banking environments
       
        Use banking and GRC terminology throughout your analysis. Consider regulatory compliance requirements (e.g., GLBA, BSA/AML), financial impact, reputational damage, customer trust implications, and required regulatory reporting.
       
        IMPORTANT: Ensure the "riskMitigation" field is formatted as a proper JSON array of strings, e.g., ["Step 1: Action", "Step 2: Action"]
       
        Security Incident Details:
        {incident}
       
        Respond ONLY with a valid JSON object containing the fields above.
        """)
       
        chain = LLMChain(llm=llm, prompt=prompt_template)
       
        # Process the incident
        response = chain.invoke({"incident": incident_description})["text"]
       
        # Clean and parse the JSON from the response
        try:
            # Remove any extra text before or after the JSON
            json_text = response.strip()
            if json_text.startswith("```") and json_text.endswith("```"):
                json_text = json_text[3:-3].strip()
            if json_text.startswith("```json") and "```" in json_text:
                json_text = json_text[7:].split("```")[0].strip()
               
            incident_analysis = json.loads(json_text)
            return incident_analysis
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response}")
            # If JSON parsing fails, fall back to the generated response
            return generate_fallback_analysis(incident_description)
    except Exception as e:
        print(f"Error using Ollama model: {e}")
        traceback.print_exc()
        # Fall back to a generated response if the model fails
        return generate_fallback_analysis(incident_description)

def generate_fallback_analysis(incident_description):
    """Generate a fallback analysis when the AI model is unavailable."""
    # Extract some keywords from the incident for basic categorization
    description_lower = incident_description.lower()
    
    # Default values
    criticality = "Significant"
    category = "IT Security"
    likelihood = "Possible"
    impact = "Moderate"
    priority = "P1"
    
    # Basic categorization based on keywords
    if any(word in description_lower for word in ["breach", "leak", "exposed", "data", "sensitive"]):
        category = "Data Breach"
        criticality = "Severe"
        impact = "Major"
        priority = "P0"
    elif any(word in description_lower for word in ["malware", "virus", "ransomware", "trojan"]):
        category = "Malware"
        criticality = "Severe"
        impact = "Major"
    elif any(word in description_lower for word in ["phish", "social engineering", "impersonation"]):
        category = "Phishing"
    elif any(word in description_lower for word in ["unauthorized", "access", "privilege", "credential"]):
        category = "Unauthorized Access"
    elif any(word in description_lower for word in ["ddos", "denial", "service", "availability"]):
        category = "Denial of Service"
    elif any(word in description_lower for word in ["compliance", "regulatory", "regulation"]):
        category = "Compliance"
    
    # Extract a title if possible
    title_match = None
    if "Title:" in incident_description:
        title_parts = incident_description.split("Title:", 1)[1].split("\n", 1)
        if title_parts:
            title_match = title_parts[0].strip()
    
    title = title_match or "Security Incident"
    
    return {
        "criticality": criticality,
        "possibleDamage": "Potential data exposure, system compromise, and reputational damage to the organization.",
        "category": category,
        "riskDescription": f"If this {category.lower()} incident is not properly addressed, it may lead to unauthorized access to sensitive data, financial loss, and regulatory penalties.",
        "riskLikelihood": likelihood,
        "riskImpact": impact,
        "riskExposureRating": "High Exposure",
        "riskPriority": priority,
        "riskAppetite": "Exceeds Appetite",
        "riskMitigation": [
            "Step 1: Isolate affected systems to prevent further compromise",
            "Step 2: Initiate incident response procedures according to the security policy",
            "Step 3: Notify relevant stakeholders and regulatory bodies if required",
            "Step 4: Perform forensic analysis to determine the extent of the breach",
            "Step 5: Implement remediation actions to address the vulnerability",
            "Step 6: Update security controls to prevent similar incidents",
            "Step 7: Conduct post-incident review and update documentation"
        ]
    } 