{
    'name': 'POS Custom Report',
    'version': '11.0',
    'category': 'Report',
    'author': 'Codisoft',
    'company': 'Codisoft',
    'website': 'http://www.codisoft.com',


    'depends': ['sale_management','account','pos_sale'],

    'data': [

        'views/sale_report.xml',
        'views/purcahse_order.xml',
        'views/invoice_report.xml',
        'data/report_paper.xml',




    ],
    'demo': [
    ],
    'images': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}