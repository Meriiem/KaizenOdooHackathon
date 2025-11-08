# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError 

class CSRDepartment(models.Model):
    _name = 'csr.department'
    _description = 'CSR Departmental Carbon Budget'
    _rec_name = 'department_id'

    department_id = fields.Many2one('hr.department', string="HR Department", required=True, ondelete='cascade', index=True)
    
    # Set store=False to avoid the PostgreSQL 12 JSONB function error
    name = fields.Char(related='department_id.name', readonly=True, store=False)

    # Carbon Budget Fields
    carbon_budget = fields.Float(string="Annual Carbon Budget (kg)", default=10000.0, help="The maximum CO2 budget allocated to this department.")
    
    total_carbon_offset = fields.Float(
        string="Total Carbon Offset (kg)", 
        compute='_compute_carbon_metrics', 
        store=True, 
        help="Sum of carbon offsets from all approved activities by employees in this department."
    )
    
    carbon_used = fields.Float(
        string="Simulated Carbon Used (kg)", 
        compute='_compute_carbon_metrics', 
        store=True, 
        help="Simulated metric for carbon usage (e.g., 50% of offset is used as a placeholder for actual usage)."
    )
    
    budget_usage_percentage = fields.Float(
        string="Budget Usage (%)", 
        compute='_compute_carbon_metrics', 
        store=True
    )

    @api.depends('carbon_budget') # Depends on budget to calculate usage
    def _compute_carbon_metrics(self):
        
        # --- THIS IS THE FIX ---
        # We will use the public, stable 'read_group' method.
        # Its return format is guaranteed to be a list of dictionaries.
        
        # Get all department IDs we care about
        dept_ids = self.department_id.ids
        if not dept_ids:
            for dept in self:
                dept.total_carbon_offset = 0.0
                dept.carbon_used = 0.0
                dept.budget_usage_percentage = 0.0
            return

        activity_data = self.env['csr.activity'].read_group(
            domain=[('status', '=', 'approved'), ('department_id', 'in', dept_ids)],
            fields=['department_id', 'carbon_offset_estimate:sum'],  # 'fields' is correct here, it includes aggregates
            groupby=['department_id']
        )
        
        # 'read_group' returns a list of dicts.
        # data['department_id'] will be a tuple: (id, name).
        # data['carbon_offset_estimate'] will be the sum.
        offset_map = {data['department_id'][0]: data['carbon_offset_estimate'] for data in activity_data if data['department_id']}

        for dept in self:
            total_offset = offset_map.get(dept.department_id.id, 0.0)
            dept.total_carbon_offset = total_offset
            
            # Simulated: 50% of budget is "base usage", reduced by offsets
            base_usage = dept.carbon_budget * 0.5 
            dept.carbon_used = base_usage - total_offset
            
            if dept.carbon_budget > 0:
                dept.budget_usage_percentage = (dept.carbon_used / dept.carbon_budget) * 100
            else:
                dept.budget_usage_percentage = 0.0

    @api.constrains('department_id')
    def _check_department_id_unique(self):
        for record in self:
            if self.search_count([('department_id', '=', record.department_id.id), ('id', '!=', record.id)]) > 0:
                raise ValidationError('A CSR Department record already exists for this HR Department.')