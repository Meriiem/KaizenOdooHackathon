# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import json

class CSROrganization(models.Model):
    """
    This is a singleton model to hold organization-wide CSR data.
    There should only be one record of this model.
    """
    _name = 'csr.organization'
    _description = 'Organization CSR Dashboard'
    
    # SDG Metrics
    sdg_metrics = fields.Text(
        string="SDG Contribution Metrics (JSON)",
        compute='_compute_sdg_metrics',
        store=True,
        compute_sudo=False, 
        help="JSON string storing total impact points per SDG."
    )
    
    # Field to display the lacking SDGs nicely
    lacking_sdgs_display = fields.Char(
        string="Lacking SDGs", 
        compute='_compute_lacking_sdgs_display', 
        store=False,
        compute_sudo=False 
    )
    
    sdg_metrics_html = fields.Html(
        string="SDG Metrics Grid",
        compute='_compute_sdg_metrics_html',
        store=False
    )

    name = fields.Char(default="Organization CSR Dashboard", readonly=True)

    # --- Metrics computed from csr.activity ---
    total_approved_activities = fields.Integer(
        string="Total Approved Activities",
        compute='_compute_organization_metrics',
        store=True
    )
    total_offset_estimate = fields.Float(
        string="Total CO₂ Offset (kg)",
        compute='_compute_organization_metrics',
        store=True
    )
    
    # --- Metrics computed from csr.department ---
    department_carbon_budget = fields.Float(
        string="Total Carbon Budget (kg)",
        compute='_compute_department_metrics',
        store=True
    )
    current_carbon_used = fields.Float(
        string="Total Carbon Used (kg)",
        compute='_compute_department_metrics',
        store=True
    )
    budget_usage_percentage = fields.Float(
        string="Total Budget Usage (%)",
        compute='_compute_department_metrics',
        store=True
    )
    
    # --- AI/Gemini Placeholder Field ---
    recommendation_text = fields.Html(
        string="AI Recommendations",
        compute='_compute_ai_recommendations',
        store=False
    )
    
    # --- FIX: Added the missing field from the XML view ---
    opportunity_ids = fields.Many2many(
        'csr.opportunity', 
        string="Strategic Opportunities",
        compute='_compute_opportunity_ids',
        store=False
    )

    @api.depends('name') # Re-compute when activities are approved
    def _compute_organization_metrics(self):
        """
        This compute method should be triggered manually by 'csr.activity'
        or run on a cron job. For this demo, we'll make it depend on 'name'
        so it computes once.
        """
        for rec in self:
            approved_activities = self.env['csr.activity'].search([('status', '=', 'approved')])
            rec.total_approved_activities = len(approved_activities)
            rec.total_offset_estimate = sum(approved_activities.mapped('carbon_offset_estimate'))

    @api.depends('total_approved_activities') # Depends on the result of _compute_organization_metrics
    def _compute_sdg_metrics(self):
        for rec in self:
            approved_activities = self.env['csr.activity'].search([('status', '=', 'approved')])
            
            # 1. Calculate total impact points per SDG
            sdg_impact = {}
            total_impact = 0
            for activity in approved_activities:
                sdg = activity.sdg_category
                points = activity.impact_points
                sdg_impact[sdg] = sdg_impact.get(sdg, 0) + points
                total_impact += points
            
            # 2. Calculate percentage contribution and store as JSON
            sdg_percentages = {}
            sdg_codes = [f"sdg{i}" for i in range(1, 18)]
            
            for sdg in sdg_codes:
                impact = sdg_impact.get(sdg, 0)
                percentage = (impact / total_impact) * 100 if total_impact > 0 else 0
                sdg_percentages[sdg] = {'impact': impact, 'percentage': round(percentage, 2)}
                
            rec.sdg_metrics = json.dumps(sdg_percentages)

    @api.depends('sdg_metrics')
    def _compute_lacking_sdgs_display(self):
        for rec in self:
            if not rec.sdg_metrics:
                rec.lacking_sdgs_display = "N/A"
                continue
            
            try:
                sdg_percentages = json.loads(rec.sdg_metrics)
            except (json.JSONDecodeError, TypeError):
                rec.lacking_sdgs_display = "Error parsing metrics"
                continue

            # Filter out 'other' before sorting
            filtered_sdgs = {k: v for k, v in sdg_percentages.items() if k != 'other'}

            # 3. Determine Lacking SDGs (Top 3 lowest percentages)
            sorted_sdgs = sorted(filtered_sdgs.items(), key=lambda item: item[1]['percentage'])
            
            lacking_sdg_codes = [item[0] for item in sorted_sdgs][:3] # Take the top 3 lowest
            
            if not lacking_sdg_codes:
                rec.lacking_sdgs_display = "All SDGs have contributions."
            else:
                display_list = [f"{code.upper()} ({sdg_percentages[code]['percentage']}%)" for code in lacking_sdg_codes]
                rec.lacking_sdgs_display = ", ".join(display_list)
                
    @api.depends('sdg_metrics')
    def _compute_sdg_metrics_html(self):
        """
        This compute method generates the HTML for the SDG grid,
        moving the logic out of the XML view to prevent the 't-set' error.
        """
        for rec in self:
            if not rec.sdg_metrics:
                rec.sdg_metrics_html = "<p>No SDG data computed yet.</p>"
                continue
            
            try:
                sdg_data = json.loads(rec.sdg_metrics)
            except (json.JSONDecodeError, TypeError):
                rec.sdg_metrics_html = "<p class='text-danger'>Error loading SDG metrics.</p>"
                continue
            
            html_cards = []
            # Filter 'other' and sort by SDG number
            sdg_items = sorted(
                [item for item in sdg_data.items() if item[0] != 'other'], 
                key=lambda x: int(x[0].replace('sdg', ''))
            )

            for sdg_code, data in sdg_items:
                percentage = data.get('percentage', 0)
                impact = data.get('impact', 0)
                sdg_number = sdg_code.replace('sdg', '')
                
                # Determine border color based on percentage
                border_color = '#dc3545' if percentage < 5 else '#28a745' # Red if < 5%, else Green
                
                card_html = f"""
                <div class="col-lg-2 col-md-3 col-sm-6">
                    <div class="card text-center mb-3" style="border: 2px solid {border_color};">
                        <div class="card-body">
                            <h5 class="card-title">SDG {sdg_number}</h5>
                            <p class="card-text mb-0"><strong>{percentage}%</strong></p>
                            <small class="text-muted">{impact} Points</small>
                        </div>
                    </div>
                </div>
                """
                html_cards.append(card_html)
            
            # Join all cards into a single row
            rec.sdg_metrics_html = f"""<div class="row">{"".join(html_cards)}</div>"""

    @api.depends('name') # Re-compute when department budgets change
    def _compute_department_metrics(self):
        """
        This compute method should be triggered manually by 'csr.department'
        or run on a cron job.
        """
        for rec in self:
            all_depts = self.env['csr.department'].search([])
            total_budget = sum(all_depts.mapped('carbon_budget'))
            total_used = sum(all_depts.mapped('carbon_used'))
            
            rec.department_carbon_budget = total_budget
            rec.current_carbon_used = total_used
            if total_budget > 0:
                rec.budget_usage_percentage = (total_used / total_budget) * 100
            else:
                rec.budget_usage_percentage = 0.0
    
    @api.depends('lacking_sdgs_display')
    def _compute_ai_recommendations(self):
        """
        Generates AI-powered recommendations based on lacking SDGs.
        """
        for rec in self:
            if rec.lacking_sdgs_display and 'N/A' not in rec.lacking_sdgs_display and 'Error' not in rec.lacking_sdgs_display:
                recommendation = f"""
                    <p><strong>AI-Powered Recommendation:</strong></p>
                    <p>Our analysis indicates that the following SDGs are currently <strong>lagging</strong>: {rec.lacking_sdgs_display}.</p>
                    <p><strong>Strategic Action:</strong> We recommend prioritizing activities that target these areas. Check the <strong>Opportunities</strong> section for new projects fetched from GlobalGiving that align with these goals.</p>
                    <p>To incentivize participation, consider offering a <strong>50% Impact Point Bonus</strong> for all approved activities classified under these lagging SDGs.</p>
                """
                rec.recommendation_text = recommendation
            else:
                rec.recommendation_text = "<p>All SDG contributions are well-balanced or data is pending. Keep up the great work!</p>"

    # --- FIX: Added compute method for the 'opportunity_ids' field ---
    @api.depends('sdg_metrics') 
    def _compute_opportunity_ids(self):
        """
        Finds opportunities that match the top 3 lacking SDGs.
        """
        for rec in self:
            if not rec.sdg_metrics:
                rec.opportunity_ids = [(5, 0, 0)] # Set to empty
                continue
            
            try:
                sdg_percentages = json.loads(rec.sdg_metrics)
            except (json.JSONDecodeError, TypeError):
                rec.opportunity_ids = [(5, 0, 0)]
                continue

            # Filter out 'other' before sorting
            filtered_sdgs = {k: v for k, v in sdg_percentages.items() if k != 'other'}
            
            # Determine Lacking SDGs (Top 3 lowest percentages)
            sorted_sdgs = sorted(filtered_sdgs.items(), key=lambda item: item[1]['percentage'])
            lacking_sdg_codes = [item[0] for item in sorted_sdgs][:3] # Get top 3 lacking
            
            if not lacking_sdg_codes:
                rec.opportunity_ids = [(5, 0, 0)] # No lacking SDGs, no opportunities to show
                continue
                
            # Search for opportunities that match these codes
            opportunity_recs = self.env['csr.opportunity'].search([('linked_sdg', 'in', lacking_sdg_codes)])
            rec.opportunity_ids = opportunity_recs

    def action_refresh_dashboard_metrics(self):
        """
        Button on the dashboard to manually refresh all metrics.
        """
        self.ensure_one()
        self._compute_organization_metrics()
        self._compute_sdg_metrics() # This will trigger the display compute
        self._compute_department_metrics()
        self._compute_ai_recommendations()
        
        # Also trigger the opportunity fetch
        self.env['csr.opportunity']._fetch_opportunities_from_globalgiving()
        
        return True