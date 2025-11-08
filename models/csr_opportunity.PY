# -*- coding: utf-8 -*-
from odoo import fields, models, api

class CSROpportunity(models.Model):
    _name = 'csr.opportunity'
    _description = 'External CSR Opportunity'
    _order = 'date desc'
    
    description = fields.Text(string="Description")

    name = fields.Char(string="Opportunity Name", required=True)
    ngo = fields.Char(string="Partner NGO/Organization")
    date = fields.Date(string="Event Date")
    location_name = fields.Char(string="Location")
    
    linked_sdg = fields.Selection([
        ('sdg1', 'SDG 1: No Poverty'), ('sdg2', 'SDG 2: Zero Hunger'), 
        ('sdg3', 'SDG 3: Good Health and Well-being'), ('sdg4', 'SDG 4: Quality Education'),
        ('sdg5', 'SDG 5: Gender Equality'), ('sdg6', 'SDG 6: Clean Water and Sanitation'),
        ('sdg7', 'SDG 7: Affordable and Clean Energy'), ('sdg8', 'SDG 8: Decent Work and Economic Growth'),
        ('sdg9', 'SDG 9: Industry, Innovation, and Infrastructure'), ('sdg10', 'SDG 10: Reduced Inequality'),
        ('sdg11', 'SDG 11: Sustainable Cities and Communities'), ('sdg12', 'SDG 12: Responsible Consumption and Production'),
        ('sdg13', 'SDG 13: Climate Action'), ('sdg14', 'SDG 14: Life Below Water'),
        ('sdg15', 'SDG 15: Life on Land'), ('sdg16', 'SDG 16: Peace and Justice Strong Institutions'),
        ('sdg17', 'SDG 17: Partnerships to achieve the Goal'), ('other', 'Other/Not Classified')
    ], string="Linked SDG", default='other')
    
    # In a real app, you might add a geo-point field for a map view
    # location_latitude = fields.Float(string="Latitude")
    # location_longitude = fields.Float(string="Longitude")
    
    @api.model
    def _fetch_opportunities_from_globalgiving(self):
        """
        Scheduled action to fetch new opportunities from GlobalGiving API.
        """
        self.env.cr.execute("INSERT INTO ir_logging(name, type, message) VALUES (%s, %s, %s)", 
                            ('CSROpportunity._fetch_opportunities_from_globalgiving', 'info', 'Starting GlobalGiving opportunity fetch.'))
        
        # 1. Get the organization's lacking SDGs
        org = self.env['csr.organization'].search([], limit=1)
        if not org:
            self.env.cr.execute("INSERT INTO ir_logging(name, type, message) VALUES (%s, %s, %s)", 
                                ('CSROpportunity._fetch_opportunities_from_globalgiving', 'warning', 'No csr.organization record found. Cannot determine lacking SDGs.'))
            return
            
        lacking_sdg_codes = org.lacking_sdgs.mapped('code')
        if not lacking_sdg_codes:
            self.env.cr.execute("INSERT INTO ir_logging(name, type, message) VALUES (%s, %s, %s)", 
                                ('CSROpportunity._fetch_opportunities_from_globalgiving', 'info', 'No lacking SDGs found. Fetching general opportunities.'))
            # Fallback to fetching a few general opportunities if no lacking SDGs are identified
            lacking_sdg_codes = ['sdg4', 'sdg13'] 

        # 2. Fetch opportunities using the utility method
        opportunities_data = self.env['csr.utils'].fetch_globalgiving_opportunities(lacking_sdg_codes)
        
        # 3. Create or update csr.opportunity records
        for data in opportunities_data:
            # Simple check to prevent duplicates (e.g., based on name and NGO)
            existing_opportunity = self.search([('name', '=', data.get('name')), ('ngo', '=', data.get('ngo'))], limit=1)
            
            vals = {
                'name': data.get('name'),
                'ngo': data.get('ngo'),
                'date': data.get('date'),
                'location_name': data.get('location'),
                'linked_sdg': data.get('sdg_code'),
                'description': data.get('description'),
            }
            
            if existing_opportunity:
                existing_opportunity.write(vals)
            else:
                self.create(vals)
                
        self.env.cr.execute("INSERT INTO ir_logging(name, type, message) VALUES (%s, %s, %s)", 
                            ('CSROpportunity._fetch_opportunities_from_globalgiving', 'info', f'Finished GlobalGiving opportunity fetch. Created/Updated {len(opportunities_data)} records.'))