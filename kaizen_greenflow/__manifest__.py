{
    'name': 'CSR & Sustainability Tracker',
    'summary': 'Track and measure CSR initiatives and sustainability impact',
    'version': '1.0.1',
    'category': 'Sustainability',
    'author': 'Kaizen Team',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/initiative_views.xml',  # MUST COME FIRST
        'views/program_views.xml',     # THEN PROGRAM VIEWS
        'views/menu.xml',
    ],
    'application': True,
    'installable': True,
}