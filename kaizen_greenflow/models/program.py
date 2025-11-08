from odoo import fields, models, api

class CSRProgram(models.Model):
    _name = "csr.program"
    _description = "CSR Program"
    
    name = fields.Char(string="Program Name", required=True)
    category = fields.Selection([
        ('environmental', 'Environmental'),
        ('ethical', 'Ethical'), 
        ('philanthropic', 'Philanthropic'),
        ('economic', 'Economic')
    ], required=True)
    description = fields.Text(string="Description")
    status = fields.Selection([
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], default='planned')
    
    # NEW: Add relationship to initiatives
    initiative_ids = fields.One2many('csr.initiative', 'program_id', string="Initiatives")
    initiative_count = fields.Integer(compute='_compute_initiative_count', string="# Initiatives")
    
    @api.depends('initiative_ids')
    def _compute_initiative_count(self):
        for program in self:
            program.initiative_count = len(program.initiative_ids)