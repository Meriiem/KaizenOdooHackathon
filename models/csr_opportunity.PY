# -*- coding: utf-8 -*-
from odoo import fields, models, api

class CSROpportunity(models.Model):
    _name = 'csr.opportunity'
    _description = 'External CSR Opportunity'
    _order = 'date desc'

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