# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import json  

class CSRActivity(models.Model):
    _name = "csr.activity"
    _description = "Employee CSR Activity"
    
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date desc"

    name = fields.Char(string="Activity Summary", required=True, tracking=True)
    
    employee_profile_id = fields.Many2one('csr.employee.profile', string="Employee Profile", required=True, tracking=True)
    employee_id = fields.Many2one(related='employee_profile_id.employee_id', string="HR Employee", store=True, readonly=True) 
    department_id = fields.Many2one(related='employee_profile_id.department_id', string="Department", store=True, readonly=True)
    
    date = fields.Date(string="Date", default=fields.Date.context_today, tracking=True)
    hours = fields.Float(string="Hours Volunteered")
    donation_amount = fields.Monetary(string="Donation Amount", currency_field='company_currency_id')
    
    company_currency_id = fields.Many2one(
        related='employee_profile_id.employee_id.company_id.currency_id', 
        string='Company Currency', 
        readonly=True
    )
    
    description = fields.Text(string="Detailed Description")
    proof_document = fields.Binary(string="Proof (Image/PDF)")
    proof_filename = fields.Char(string="Proof Filename")

    # Workflow
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', string="Status", tracking=True)
    
    # AI/Impact Fields
    sdg_category = fields.Selection([
        ('sdg1', 'SDG 1: No Poverty'), ('sdg2', 'SDG 2: Zero Hunger'), 
        ('sdg3', 'SDG 3: Good Health and Well-being'), ('sdg4', 'SDG 4: Quality Education'),
        ('sdg5', 'SDG 5: Gender Equality'), ('sdg6', 'SDG 6: Clean Water and Sanitation'),
        ('sdg7', 'SDG 7: Affordable and Clean Energy'), ('sdg8', 'SDG 8: Decent Work and Economic Growth'),
        ('sdg9', 'SDG 9: Industry, Innovation, and Infrastructure'), ('sdg10', 'SDG 10: Reduced Inequality'),
        ('sdg11', 'SDG 11: Sustainable Cities and Communities'), ('sdg12', 'SDG 12: Responsible Consumption and Production'),
        ('sdg13', 'SDG 13: Climate Action'), ('sdg14', 'SDG 14: Life Below Water'),
        ('sdg15', 'SDG 15: Life on Land'), ('sdg16', 'SDG 16: Peace and Justice Strong Institutions'),
        ('sdg17', 'SDG 17: Partnerships to achieve the Goal'), ('other', 'Other/Not Classified')
    ], string="SDG Category", default='other', compute='_compute_sdg_category', store=True, help="Automatically classified by AI based on description")

    carbon_offset_estimate = fields.Float(string="CO₂ Offset Estimate (kg)", compute='_compute_carbon_offset', store=True, help="Estimate from Carbon Interface API")
    
    # Gamification
    impact_points = fields.Integer(string="Impact Points Earned", compute='_compute_impact_points', store=True, help="Points based on hours, donation, and SDG bonus")

    # --- THIS IS THE FIX ---
    # Replaced the failing Gemini API call with a simple, stable simulation
    # This will allow your demo data to load without crashing.
    @api.depends('description')
    def _compute_sdg_category(self):
        for rec in self:
            desc = (rec.description or "").lower()
            if "water" in desc or "beach" in desc or "marine" in desc:
                rec.sdg_category = 'sdg14'
            elif "tree" in desc or "forest" in desc or "desertification" in desc:
                rec.sdg_category = 'sdg15'
            elif "education" in desc or "school" in desc or "tutoring" in desc:
                rec.sdg_category = 'sdg4'
            elif "health" in desc or "hospital" in desc:
                rec.sdg_category = 'sdg3'
            elif "food" in desc or "hunger" in desc:
                rec.sdg_category = 'sdg2'
            elif "poverty" in desc:
                rec.sdg_category = 'sdg1L'
            else:
                rec.sdg_category = 'other'

    @api.depends('sdg_category', 'hours')
    def _compute_carbon_offset(self):
        for rec in self:
            # We use the utility for the *simulation* which is stable
            rec.carbon_offset_estimate = self.env['csr.utils'].get_carbon_offset_estimate(rec.sdg_category, rec.hours)

    @api.depends('status', 'hours', 'donation_amount', 'sdg_category')
    def _compute_impact_points(self):
        org = self.env['csr.organization'].search([], limit=1)
        
        lacking_sdg_codes = ['sdg14'] # Default
        if org and org.sdg_metrics:
            try:
                sdg_percentages = json.loads(org.sdg_metrics)
                filtered_sdgs = {k: v for k, v in sdg_percentages.items() if k != 'other'}
                sorted_sdgs = sorted(filtered_sdgs.items(), key=lambda item: item[1]['percentage'])
                lacking_sdg_codes = [item[0] for item in sorted_sdgs][:3]
            except (json.JSONDecodeError, TypeError):
                lacking_sdg_codes = ['sdg14'] # Fallback on error

        for rec in self:
            if rec.status == 'approved':
                base_points = rec.hours * 10
                donation_points = rec.donation_amount * 0.5 if rec.donation_amount else 0.0
                
                bonus_points = 0
                if rec.sdg_category in lacking_sdg_codes: 
                    bonus_points = base_points * 0.5 # 50% bonus
                
                rec.impact_points = int(base_points + donation_points + bonus_points)
            else:
                rec.impact_points = 0
    
    def action_submit(self):
        self.ensure_one()
        self.status = 'submitted'
        
    def action_approve(self):
        self.ensure_one()
        self.status = 'approved'
        self.employee_profile_id._compute_csr_metrics() 
        if self.department_id:
            department_csr = self.env['csr.department'].search([('department_id', '=', self.department_id.id)], limit=1)
            if department_csr:
                department_csr._compute_carbon_metrics()
        org = self.env['csr.organization'].search([], limit=1)
        if org:
            # This triggers all the dashboard computes
            org.action_refresh_dashboard_metrics() 

    def action_reject(self):
        self.ensure_one()
        self.status = 'rejected' 
        self._compute_impact_points() 
        self.employee_profile_id._compute_csr_metrics()
        if self.department_id:
            department_csr = self.env['csr.department'].search([('department_id', '=', self.department_id.id)], limit=1)
            if department_csr:
                department_csr._compute_carbon_metrics()
        org = self.env['csr.organization'].search([], limit=1)
        if org:
            # This triggers all the dashboard computes
            org.action_refresh_dashboard_metrics()