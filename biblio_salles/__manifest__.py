{
    'name': 'Médiathèque — réservation des salles',
    'summary': "Exercice à rendre du chapitre 8 : champs calculés et liés",
    'version': '19.0.1.0.0',
    'category': 'Training',
    'author': 'HELB — Cours ERP',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/room_views.xml',
        'data/room_data.xml',
    ],
    'application': True,
}
