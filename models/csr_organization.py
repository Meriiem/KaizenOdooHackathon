# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from collections import Counter

class CSROrganization(models.Model):
    _name = 'csr.organization'
    _description = 'Organization CSR Dashboard'

    name = fields.Char(default="Organization CSR Dashboard", readonly=True)

    total_approved_activities = fields.Integer(
        string="Total Approved Activities",
        compute='_compute_organization_metrics',
    )
    total_offset_estimate = fields.Float(
        string="Total CO₂ Offset (kg)",
        compute='_compute_organization_metrics',
    )
    
    department_carbon_budget = fields.Float(
        string="Total Carbon Budget (kg)",
        compute='_compute_department_metrics',
    )
    current_carbon_used = fields.Float(
        string="Total Carbon Used (kg)",
        compute='_compute_department_metrics',
    )
    budget_usage_percentage = fields.Float(
        string="Total Budget Usage (%)",
        compute='_compute_department_metrics',
    )
    
    recommendation_text = fields.Html(
        string="AI Recommendations",
        compute='_compute_ai_recommendations',
    )
    
    @api.model
    def action_open_dashboard(self):
        dashboard = self.env['csr.organization'].search([], limit=1)
        if not dashboard:
            dashboard = self.env['csr.organization'].create({'name': 'Organization CSR Dashboard'})
            # Manually compute fields on creation
            dashboard.action_refresh_dashboard_metrics()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Organization Dashboard',
            'res_model': 'csr.organization',
            'res_id': dashboard.id,
            # --- FIX: Must be 'kanban' to match the view file ---
            'view_mode': 'kanban',
            'target': 'main',
        }

    @api.depends('name') 
    def _compute_organization_metrics(self):
        for rec in self:
            approved_activities = self.env['csr.activity'].search([('status', '=', 'approved')])
            rec.total_approved_activities = len(approved_activities)
            rec.total_offset_estimate = sum(approved_activities.mapped('carbon_offset_estimate'))

    @api.depends('name') 
    def _compute_department_metrics(self):
        for rec in self:
            all_depts = self.env['csr.department'].search([])
            all_depts._compute_carbon_metrics() # Ensure budgets are computed
            
            total_budget = sum(all_depts.mapped('carbon_budget'))
            total_used = sum(all_depts.mapped('carbon_used'))
            
            rec.department_carbon_budget = total_budget
            rec.current_carbon_used = total_used
            if total_budget > 0:
                rec.budget_usage_percentage = (total_used / total_budget) * 100
            else:
                rec.budget_usage_percentage = 0.0
    
    @api.depends('name')
    def _compute_ai_recommendations(self):
        """
        Simulates an AI reading the data to find weak spots.
        """
        self.ensure_one()
        
        all_sdgs = [key for key, label in self.env['csr.activity']._fields['sdg_category'].selection if key != 'other']
        approved_activities = self.env['csr.activity'].search([('status', '=', 'approved')])
        sdg_counts = Counter(approved_activities.mapped('sdg_category'))
        
        weakest_sdg = 'sdg14' # Default
        min_count = float('inf')
        
        for sdg in all_sdgs:
            count = sdg_counts.get(sdg, 0)
            if count < min_count:
                min_count = count
                weakest_sdg = sdg
        
        matching_opportunity = self.env['csr.opportunity'].search([('linked_sdg', '=', weakest_sdg)], limit=1)
        
        # Use a mapping to get the full SDG label
        selection_dict = dict(self.env['csr.activity']._fields['sdg_category'].selection)
        sdg_label = selection_dict.get(weakest_sdg, 'N/A')
        
        rec_text = f"""
            <p><strong>AI-Generated Insight (Simulated):</strong></p>
            <p>Our contributions for <strong>{sdg_label}</strong> are currently the lowest, with only {min_count} approved activit(y/ies).</p>
        """
        
        if matching_opportunity:
            rec_text += f"""
                <p><strong>Recommendation:</strong></p>
                <p>Promote the upcoming '<strong>{matching_opportunity.name}</strong>' event, which directly supports this goal. Consider offering 1.5x bonus points for participation.</p>
            """
        else:
            rec_text += "<p><strong>Recommendation:</strong></p><p>No upcoming opportunities match this SDG. We should partner with an NGO focused on this area.</p>"
            
        self.recommendation_text = rec_text

    def action_refresh_dashboard_metrics(self):
        """
        Button on the dashboard to manually refresh all metrics.
        """
        self.ensure_one()
        # We also need to trigger the department compute
        self.env['csr.department'].search([])._compute_carbon_metrics()
        # By invalidating the fields, we force all computes to re-run
        self.invalidate_recordset([
            'total_approved_activities', 
            'total_offset_estimate', 
            'department_carbon_budget', 
            'current_carbon_used', 
            'budget_usage_percentage', 
            'recommendation_text'
        ])
        return True