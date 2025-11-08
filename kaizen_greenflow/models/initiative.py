from odoo import fields, models

class CSRInitiative(models.Model):
    _name = "csr.initiative"
    _description = "CSR Initiative"
    
    name = fields.Char(string="Initiative Name", required=True)
    program_id = fields.Many2one('csr.program', string="Program", required=True)
    description = fields.Text(string="Description")
    
    target_value = fields.Float(string="Target Value")
    unit = fields.Char(string="Unit", help="e.g., kg CO2, hours, AED, etc.")
    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], default='planned')