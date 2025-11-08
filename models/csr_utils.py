# -*- coding: utf-8 -*-
import requests
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from openai import OpenAI
import logging  # <-- FIX: Import Odoo's logger

# Get the logger
_logger = logging.getLogger(__name__)

# --- API Keys and Configuration (Placeholder) ---
CARBON_API_URL = "https://api.carboninterface.com/v1/estimates"
CARBON_API_KEY = "YOUR_CARBON_API_KEY" # Placeholder

GLOBALGIVING_API_URL = "https://api.globalgiving.org/api/public/projectservice/all/projects"
GLOBALGIVING_API_KEY = "YOUR_GLOBALGIVING_API_KEY" # Placeholder

class CSRUtils(models.AbstractModel):
    _name = 'csr.utils'
    _description = 'CSR Utility Methods for API Calls and AI'

    @api.model
    def classify_sdg_with_gemini(self, activity_description):
        """
        Uses the Gemini model (via OpenAI client) to classify an activity description
        into one of the 17 UN SDGs.
        """
        if not activity_description:
            return 'other'

        # List of SDGs for the prompt
        sdg_list = [
            "SDG 1: No Poverty", "SDG 2: Zero Hunger", "SDG 3: Good Health and Well-being",
            "SDG 4: Quality Education", "SDG 5: Gender Equality", "SDG 6: Clean Water and Sanitation",
            "SDG 7: Affordable and Clean Energy", "SDG 8: Decent Work and Economic Growth",
            "SDG 9: Industry, Innovation, and Infrastructure", "SDG 10: Reduced Inequality",
            "SDG 11: Sustainable Cities and Communities", "SDG 12: Responsible Consumption and Production",
            "SDG 13: Climate Action", "SDG 14: Life Below Water", "SDG 15: Life on Land",
            "SDG 16: Peace and Justice Strong Institutions", "SDG 17: Partnerships to achieve the Goal"
        ]
        
        system_prompt = (
            "You are an expert UN Sustainable Development Goal (SDG) classifier. "
            "Your task is to analyze a corporate social responsibility (CSR) activity description "
            "and return the single most relevant SDG code (e.g., 'sdg1', 'sdg17'). "
            "If no clear SDG is relevant, return 'other'. "
            "The available SDGs are: " + ", ".join(sdg_list)
        )

        user_prompt = f"Classify the following activity description: '{activity_description}'"

        try:
            # This line will fail if OPENAI_API_KEY is not set
            client = OpenAI() 
            response = client.chat.completions.create(
                model="gpt-4.1-mini", # Using the available model slug
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=10,
                temperature=0.0
            )
            
            result = response.choices[0].message.content.strip().lower()
            
            valid_codes = [f"sdg{i}" for i in range(1, 18)] + ['other']
            if result in valid_codes:
                return result
            
            for code in valid_codes:
                if code in result:
                    return code
            
            return 'other'

        except Exception as e:
            # --- FIX: Changed from raw SQL to Odoo's logger ---
            # This prevents the "NotNullViolation" crash.
            _logger.error(f"Gemini API Error: {e}")
            
            # --- Fallback Simulation (if API fails) ---
            desc = (activity_description or "").lower()
            if "water" in desc or "beach" in desc or "marine" in desc:
                return 'sdg14'
            elif "tree" in desc or "forest" in desc:
                return 'sdg15'
            elif "education" in desc or "school" in desc:
                return 'sdg4'
            else:
                return 'other'

    @api.model
    def get_carbon_offset_estimate(self, activity_type, hours):
        """
        Simulates a call to the Carbon Interface API to get a CO2 offset estimate.
        """
        if not hours or hours <= 0:
            return 0.0

        # --- SIMULATION LOGIC ---
        if activity_type in ['sdg13', 'sdg14', 'sdg15']:
            return hours * 5.0  # 5 kg CO2 offset per hour for environmental activities
        return 0.0

    @api.model
    def fetch_globalgiving_opportunities(self, sdg_codes):
        """
        Simulates fetching project opportunities from the GlobalGiving API based on lacking SDGs.
        """
        simulated_opportunities = []
        for code in sdg_codes:
            simulated_opportunities.append({
                'name': f"Simulated Project for {code.upper()}",
                'ngo': "Global Charity Partner",
                'date': fields.Date.today(),
                'location': "Virtual/Global",
                'sdg_code': code,
                'description': f"A high-impact project targeting {code.upper()} to help the organization meet its sustainability goals."
            })
        return simulated_opportunities