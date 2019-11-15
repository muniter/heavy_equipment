{
    'name': "heavy_equipment",

    'summary': """
        Module to control heavy equipment work, Hours and material move""",
    'description': """
    This module is used to track the work dump trucks do on a stie, and the
    other heavy equipment.
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base', 'project', 'fleet'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
