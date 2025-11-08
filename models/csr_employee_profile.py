# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError # Import ValidationError

class CSREmployeeProfile(models.Model):
    _name = 'csr.employee.profile'
    _description = 'CSR Employee Profile Extension'
    _order = "total_impact_points desc"
    
    _inherit = ['mail.thread'] 

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade', index=True)
    
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True)
    name = fields.Char(related='employee_id.name', readonly=True, store=True)
    image_128 = fields.Image(related='employee_id.image_128', string="Image 128", readonly=True)
    
    total_impact_points = fields.Integer(string="Total Impact Points", default=0, compute='_compute_csr_metrics', store=True)
    volunteering_hours = fields.Float(string="Total Volunteering Hours", default=0.0, compute='_compute_csr_metrics', store=True)
    donation_amount = fields.Monetary(string="Total Donation Amount", default=0.0, compute='_compute_csr_metrics', store=True, currency_field='company_currency_id')
    company_currency_id = fields.Many2one(related='employee_id.company_id.currency_id', string='Company Currency', readonly=True)
    
    activity_ids = fields.One2many('csr.activity', 'employee_profile_id', string="CSR Activities")
    
    rank_display = fields.Char(string="Current Rank", compute='_compute_rank', store=False)

    @api.depends('activity_ids')
    def _compute_csr_metrics(self):
        for employee_profile in self:
            approved_activities = employee_profile.activity_ids.filtered(lambda r: r.status == 'approved')
            employee_profile.volunteering_hours = sum(approved_activities.mapped('hours'))
            employee_profile.donation_amount = sum(approved_activities.mapped('donation_amount'))
            employee_profile.total_impact_points = sum(approved_activities.mapped('impact_points'))

    # --- THIS IS THE PYTHON FIX ---
    #
    # The compute method _compute_rank (store=False) was depending on
    # _compute_csr_metrics (store=True) via 'total_impact_points'.
    # This creates a complex dependency chain at load time which breaks the registry.
    # By changing the dependency to 'activity_ids' (the same as _compute_csr_metrics),
    # we break the circular chain.
    #
    @api.depends('activity_ids')
    def _compute_rank(self):
        # We must re-call the compute manually to ensure points are up-to-date
        # for the ranking calculation, as Odoo might run this compute first.
        self._compute_csr_metrics() 
        
        sorted_profiles = self.env['csr.employee.profile'].search([], order='total_impact_points desc')
        rank_map = {profile.id: rank + 1 for rank, profile in enumerate(sorted_profiles)}
        
        for profile in self:
            profile.rank_display = f"#{rank_map.get(profile.id, 'N/A')}"
            
    @api.constrains('employee_id')
    def _check_employee_id_unique(self):
        for record in self:
            if self.search_count([('employee_id', '=', record.employee_id.id), ('id', '!=', record.id)]) > 0:
                raise ValidationError('An employee can only have one CSR Profile.')

    def action_redeem_reward(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Redeem Rewards'),
            'res_model': 'csr.reward',
            'view_mode': 'kanban',
            'domain': [('is_active', '=', True)],
            'target': 'new',
        }
    
    def action_view_activities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('My Activities'),
            'res_model': 'csr.activity',
            'view_mode': 'list,form', # Use 'list', not 'tree'
            'domain': [('employee_profile_id', '=', self.id)],
            'context': {
                'default_employee_profile_id': self.id,
                'default_employee_id': self.employee_id.id
            }
        }