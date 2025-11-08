{
    'name': 'KAIZEN: CSR & Sustainability Tracker',
    'summary': 'Empowering Employees, Tracking Impact, Amplifying Sustainability.',
    'version': '1.0',
    'category': 'Human Resources/CSR',
    'author': 'Meriem Aoudia & Maha Junaid',
    'license': 'LGPL-3',
    'depends': ['base', 'hr', 'mail'], 
    
    'data': [
        'security/ir.model.access.csv',
        
        # Load model views first
        'views/csr_activity_views.xml',
        'views/csr_reward_views.xml',
        'views/csr_department_views.xml',
        'views/csr_opportunity_views.xml', 
        'views/csr_employee_views.xml',
        'views/csr_organization_views.xml',
        
        # Load menus
        'views/menu.xml',
        
        # Load data
        'data/reward_data.xml',
        'data/demo_data.xml',
        'data/extra_demo_data.xml', # <-- ADDED NEW DATA FILE
    ],
    'application': True,
    'installable': True,
    
    'assets': {
        'web.assets_backend': [
            'kaizen_greenflow/static/description/icon.png',
        ],
    },
}