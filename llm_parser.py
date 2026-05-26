import json
from typing import Dict, Any, List, Optional
import ollama
from pydantic import BaseModel, Field
from utils import logger

# Unified strict schema representation using Pydantic
class GraduateProfile(BaseModel):
    name: str = Field(default="", description="Full identity name of the graduate.")
    graduation_year: str = Field(default="", description="The year the student graduated from NSD.")
    current_profession: str = Field(default="", description="Current primary work or role title.")
    current_location: str = Field(default="", description="City or country where they currently operate.")
    website: str = Field(default="", description="Official personal URL link.")
    portfolio: str = Field(default="", description="Showcase portfolio link.")
    linkedin: str = Field(default="", description="LinkedIn URL.")
    instagram: str = Field(default="", description="Instagram user page link.")
    facebook: str = Field(default="", description="Facebook page link.")
    youtube: str = Field(default="", description="YouTube channel url.")
    imdb: str = Field(default="", description="IMDb talent page profile link.")
    plays_acted_in: List[str] = Field(default_factory=list)
    plays_directed: List[str] = Field(default_factory=list)
    plays_written: List[str] = Field(default_factory=list)
    theatre_groups: List[str] = Field(default_factory=list)
    film_appearances: List[str] = Field(default_factory=list)
    tv_appearances: List[str] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)
    public_phone_numbers: List[str] = Field(default_factory=list, description="Only verified public contact numbers.")
    public_emails: List[str] = Field(default_factory=list, description="Only verified public emails.")
    sources: List[str] = Field(default_factory=list, description="URLs containing referenced details.")

def _call_ollama_with_fallback(prompt: str, schema: Any) -> Optional[str]:
    """Tries extraction via gemma3, seamlessly falling back to llama3:8b if unavailable."""
    models_to_try = ["gemma3", "llama3:8b"]
    
    for model in models_to_try:
        try:
            logger.info(f"Attempting structured inference using LLM model: {model}")
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.0},
                format='json'  # Forces structural mode serialization natively
            )
            return response['message']['content']
        except Exception as e:
            logger.warning(f"Model '{model}' run failure or missing in local Ollama instance: {e}")
    return None

def parse_intel_with_llm(target_name: str, target_year: Any, evidence_data: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Compiles contextual search results and uses a local LLM to 
    extract data into the structured schema.
    """
    if not evidence_data:
        logger.warning(f"No collected evidence data available to parse for {target_name}.")
        return GraduateProfile(name=target_name, graduation_year=str(target_year)).model_dump()

    # Compile context block
    context_chunks = []
    for entry in evidence_data:
        context_chunks.append(f"SOURCE URL: {entry['url']}\nSNIPPET: {entry['snippet']}\nRAW TEXT CONTENT:\n{entry.get('page_text', '')}\n---")
    
    combined_context = "\n".join(context_chunks)[:25000] # Safe limit boundary context chunk

    prompt = f"""
You are a senior data extraction system. Your job is to extract highly accurate, structured information about a National School of Drama (NSD) graduate from the background data context provided below.

Target Person: {target_name}
Target Graduation Year Range: {target_year}

Instructions:
1. Extract structured information ONLY from the provided context text data. 
2. Do not invent, extrapolate, or guess data. 
3. If information is uncertain, missing, or belongs to a different person with a similar name, return null or an empty string/array for those fields.
4. Do not guess phone numbers or emails. Only collect if explicitly visible as a public contact.
5. You must populate the 'sources' field with the exact URLs from which valid profile field information was successfully extracted.

JSON Schema Requirement:
Return valid JSON adhering exactly to this structure:
{json.dumps(GraduateProfile.model_json_schema(), indent=2)}

Background Context Data:
{combined_context}
"""

    response_text = _call_ollama_with_fallback(prompt, GraduateProfile)
    
    if not response_text:
        logger.error(f"Critical: Local LLM extraction failed entirely for {target_name}.")
        return GraduateProfile(name=target_name, graduation_year=str(target_year)).model_dump()

    try:
        parsed_json = json.loads(response_text)
        # Validation pass over Pydantic data modeling definitions
        validated_profile = GraduateProfile(**parsed_json)
        return validated_profile.model_dump()
    except Exception as parse_err:
        logger.error(f"Failed parsing LLM validation output loop structure: {parse_err}. Raw output context: {response_text}")
        return GraduateProfile(name=target_name, graduation_year=str(target_year)).model_dump()