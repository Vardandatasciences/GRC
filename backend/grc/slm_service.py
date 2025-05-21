import json
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def analyze_security_incident(incident_description):
    # Initialize the local SLM model
    llm = OllamaLLM(model="mistral:7b-instruct")
   
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
        return {
            "error": "Failed to parse incident analysis",
            "details": str(e),
            "raw_response": response
        } 