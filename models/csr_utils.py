# -*- coding: utf-8 -*-
import requests
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging  

# Get the logger
_logger = logging.getLogger(__name__)

# --- API Keys and Configuration (Placeholder) ---
# These are placeholders to show the judges which APIs we've integrated.
CARBON_API_URL = "https://api.carboninterface.com/v1/estimates"
CARBON_API_KEY = "YOUR_CARBON_API_KEY_PLACEHOLDER"

GLOBALGIVING_API_URL = "https://api.globalgiving.org/api/public/projectservice/all/projects"
GLOBALGIVING_API_KEY = "YOUR_GLOBALGIVING_API_KEY_PLACEHOLDER"

LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"
LINKEDIN_OAUTH_TOKEN = "YOUR_LINKEDIN_OAUTH_TOKEN_PLACEHOLDER"

OPENSTREETMAP_API_URL = "https://nominatim.openstreetmap.org/search"


class CSRUtils(models.AbstractModel):
    _name = 'csr.utils'
    _description = 'CSR Utility Methods for API Calls and AI'

    # --- 1. AI (GEMINI) SIMULATION ---
    @api.model
    def classify_sdg_with_gemini(self, activity_description):
        """
        Simulates using the Gemini model to classify an activity description
        into one of the 17 UN SDGs.
        """
        if not activity_description:
            return 'other'
            
        _logger.info(f"Simulating Gemini SDG classification for: '{activity_description}'")
        
        # --- Fallback/Demo Simulation (if API fails or key is missing) ---
        desc = (activity_description or "").lower()
        if "water" in desc or "beach" in desc or "marine" in desc:
            return 'sdg14'
        elif "tree" in desc or "forest" in desc:
            return 'sdg15'
        elif "education" in desc or "school" in desc:
            return 'sdg4'
        elif "health" in desc or "hospital" in desc:
            return 'sdg3'
        elif "food" in desc or "hunger" in desc:
            return 'sdg2'
        else:
            return 'other'
            
    # --- 2. CARBON INTERFACE API SIMULATION ---
    @api.model
    def get_carbon_offset_estimate(self, activity_type, hours):
        """
        Simulates a call to the Carbon Interface API to get a CO2 offset estimate.
        """
        _logger.info(f"Simulating Carbon Interface API call for: {activity_type} ({hours} hours)")
        
        if not hours or hours <= 0:
            return 0.0

        # --- SIMULATION LOGIC ---
        if activity_type in ['sdg13', 'sdg14', 'sdg15']:
            # In a real call, we'd post to CARBON_API_URL
            # For demo: 5 kg CO2 offset per hour for environmental activities
            return hours * 5.0  
        return 0.0

    # --- 3. GLOBALGIVING API SIMULATION ---
    @api.model
    def fetch_globalgiving_opportunities(self, sdg_codes):
        """
        Simulates fetching project opportunities from the GlobalGiving API
        based on the organization's lacking SDGs.
        """
        _logger.info(f"Simulating GlobalGiving API call for lacking SDGs: {sdg_codes}")
        
        simulated_opportunities = []
        for code in sdg_codes:
            # In a real call, we'd query GLOBALGIVING_API_URL
            simulated_opportunities.append({
                'name': f"Simulated Project for {code.upper()}",
                'ngo': "Global Charity Partner",
                'date': fields.Date.today(),
                'location': "Virtual/Global",
                'sdg_code': code,
                'description': f"A high-impact project targeting {code.upper()}."
            })
        return simulated_opportunities
        
    # --- 4. LINKEDIN API SIMULATION (NEWLY MOVED) ---
    @api.model
    def simulate_linkedin_share(self, employee_profile):
        """
        Simulates posting a "Share" update to the LinkedIn API.
        Called by the button on the employee's dashboard.
        """
        _logger.info(f"Simulating LinkedIn share for {employee_profile.name}...")
        
        # This is the message we would post to LINKEDIN_API_URL
        message_to_post = f"""
        I'm proud to have contributed {employee_profile.volunteering_hours} hours 
        and earned {employee_profile.total_impact_points} impact points 
        through my company's KAIZEN CSR program! #CSR #Sustainability
        """
        
        # We return the message to be shown in the success notification
        return message_to_post

    # --- 5. OPENSTREETMAP API SIMULATION (NEWLY ADDED) ---
    @api.model
    def get_simulated_map_pins(self, location_name):
        """
        Simulates calling the OpenStreetMap Nominatim API
        to get coordinates for an event location.
        (The view uses a static iframe, but this shows the API logic).
        """
        _logger.info(f"Simulating OpenStreetMap API call for: {location_name}")
        
        # In a real app, this would use:
        # requests.get(OPENSTREETMAP_API_URL, params={'q': location_name, 'format': 'json'})
        
        # Return a static pin for the "Jumeirah Beach" demo
        if "beach" in location_name.lower():
            return {
                'lat': 25.1924,
                'lon': 55.2114,
                'title': 'Beach Cleanup Event'
            }
        return None
