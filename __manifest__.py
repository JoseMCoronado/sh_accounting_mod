# -*- coding: utf-8 -*-
{
    'name': 'Commissioned Accounting Modifications',
    'category': 'Accounting',
    'author': 'GFP Solutions',
    'summary': 'Custom',
    'version': '1.0',
    'description': """
Accounting modifications commissioned by Speedhut. Check Flow for modification details.

THIS MODULE IS PROVIDED AS IS - INSTALLATION AT USERS' OWN RISK - AUTHOR OF MODULE DOES NOT CLAIM ANY
RESPONSIBILITY FOR ANY BEHAVIOR ONCE INSTALLED.
        """,

    'depends':['base','account_accountant','purchase','account_cancel','l10n_us_check_printing'],
    'data':['views/ir_ui_views.xml','views/ir_ui_qweb.xml'],
    'installable': True,
}
