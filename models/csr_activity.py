# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

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
    
    rejection_reason = fields.Text(string="Rejection Reason", tracking=True)

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
    ], string="SDG Category", default='other', compute='_compute_sdg_and_impact', store=True, readonly=False, help="Automatically classified by AI based on description (simulated)")

    carbon_offset_estimate = fields.Float(string="CO₂ Offset Estimate (kg)", compute='_compute_sdg_and_impact', store=True, readonly=False, help="Estimate from Carbon Interface API (simulated)")
    
    # Gamification
    impact_points = fields.Integer(string="Impact Points Earned", compute='_compute_sdg_and_impact', store=True, help="10 points per hour + bonus for weak SDGs (simulated)")

    @api.depends('description', 'hours', 'donation_amount', 'status')
    def _compute_sdg_and_impact(self):
        for rec in self:
            sdg_cat = 'other' # Default
            if rec.description:
                desc_lower = rec.description.lower()
                if 'tree' in desc_lower or 'forest' in desc_lower or 'plant' in desc_lower:
                    sdg_cat = 'sdg15'
                elif 'water' in desc_lower or 'beach' in desc_lower or 'marine' in desc_lower:
                    sdg_cat = 'sdg14'
                elif 'education' in desc_lower or 'school' in desc_lower or 'tutor' in desc_lower:
                    sdg_cat = 'sdg4'
                elif 'food' in desc_lower or 'hunger' in desc_lower or 'charity kitchen' in desc_lower:
                    sdg_cat = 'sdg2'
                # --- THIS IS THE FIX ---
                # Changed 'sdg1s' to 'sdg1'
                elif 'poverty' in desc_lower or 'donation' in desc_lower:
                    sdg_cat = 'sdg1'
                elif 'health' in desc_lower or 'hospital' in desc_lower:
                    sdg_cat = 'sdg3'
            rec.sdg_category = sdg_cat

            if rec.sdg_category in ['sdg13', 'sdg14', 'sdg15']:
                rec.carbon_offset_estimate = rec.hours * 5.0
            else:
                rec.carbon_offset_estimate = 0.0

            if rec.status == 'approved':
                base_points = rec.hours * 10
                donation_points = rec.donation_amount * 0.5 
                
                bonus_points = 0
                if rec.sdg_category == 'sdg14': # Simulate SDG 14 is lagging
                    bonus_points = base_points * 0.5 
                
                rec.impact_points = int(base_points + donation_points + bonus_points)
            else:
                rec.impact_points = 0
    
    def action_submit(self):
        self.ensure_one()
        self.status = 'submitted'
        
    def action_approve(self):
        self.ensure_one()
        self.status = 'approved'
        self.rejection_reason = False # Clear rejection reason
        self.employee_profile_id._compute_csr_metrics() 
        if self.department_id:
            department_csr = self.env['csr.department'].search([('department_id', '=', self.department_id.id)], limit=1)
            if department_csr:
                department_csr._compute_carbon_metrics()
        self.env['csr.organization'].search([], limit=1).action_refresh_dashboard_metrics()

    def action_reject(self):
        self.ensure_one()
        self.status = 'rejected' 
        self._compute_sdg_and_impact()
        self.employee_profile_id._compute_csr_metrics()
        if self.department_id:
            department_csr = self.env['csr.department'].search([('department_id', '=', self.department_id.id)], limit=1)
            if department_csr:
                department_csr._compute_carbon_metrics()
        self.env['csr.organization'].search([], limit=1).action_refresh_dashboard_metrics()