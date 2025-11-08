# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class CSRReward(models.Model):
    _name = "csr.reward"
    _description = "Employee Reward Catalog"
    _rec_name = "name"
    
    name = fields.Char(string="Reward Name", required=True)
    point_cost = fields.Integer(string="Point Cost", required=True)
    description = fields.Text(string="Description")
    is_active = fields.Boolean(default=True)
    
    def action_request_redemption(self):
        self.ensure_one()
        employee_profile = self.env['csr.employee.profile'].search([('employee_id.user_id', '=', self.env.user.id)], limit=1)
        
        if not employee_profile:
            raise UserError(_("You must have an active CSR Employee Profile linked to your user to redeem rewards."))
            
        if employee_profile.total_impact_points >= self.point_cost:
            # Simple deduction for demonstration. In real life, a new 'csr.redemption' model would be created
            # This is not ideal in a concurrent environment, but fine for demo
            employee_profile.write({
                'total_impact_points': employee_profile.total_impact_points - self.point_cost
            })
            
            # Log the activity for the manager
            manager = employee_profile.employee_id.parent_id
            
            # --- CRITICAL FIX: Changed 'kaizen_csr_tracker' to 'kaizen_greenflow' ---
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f"Reward Redemption: {self.name}",
                'note': f"Employee {employee_profile.name} redeemed {self.point_cost} points for '{self.name}'. Please arrange for fulfillment.",
                'res_id': employee_profile.id,
                'res_model_id': self.env.ref('kaizen_greenflow.model_csr_employee_profile').id,
                'user_id': manager.user_id.id if manager and manager.user_id else self.env.user.id,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success!'),
                    'message': _(f"You have redeemed {self.point_cost} points for {self.name}. Your manager has been notified for fulfillment."),
                    'sticky': False,
                    'type': 'success',
                }
            }
        else:
            raise UserError(_(f"You only have {employee_profile.total_impact_points} points. You need {self.point_cost} points to redeem this reward."))