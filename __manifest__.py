{
    'name': 'KAIZEN: CSR & Sustainability Tracker',
    'summary': 'Empowering Employees, Tracking Impact, Amplifying Sustainability.',
    'version': '1.0',
    'category': 'Human Resources/CSR',
    'author': 'Meriem & Maha',
    'license': 'LGPL-3',
    'depends': ['base', 'hr', 'mail'], # Inherits hr.employee, uses mail for chatter
    
    'data': [
        'security/ir.model.access.csv',
        
        # Load model views first, in order of dependency
        'views/csr_activity_views.xml',
        'views/csr_reward_views.xml',
        'views/csr_department_views.xml',
        'views/csr_opportunity_views.xml', # <-- FIX: Added new view file
        
        # Load the 'employee' and 'organization' views which depend on the above
        'views/csr_employee_views.xml',
        'views/csr_organization_views.xml',
        
        # Load menus last
        'views/menu.xml',
        
        # Load data/demo data after all views are loaded
        'data/reward_data.xml',
        'data/demo_data.xml',
    ],
    'application': True,
    'installable': True,
    
    'assets': {
        'web.assets_backend': [
            'kaizen_greenflow/static/description/icon.png',
        ],
    },
}