# -*- coding: utf-8 -*-
from odoo import http

# class HeavyEquipment(http.Controller):
#     @http.route('/heavy_equipment/heavy_equipment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/heavy_equipment/heavy_equipment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('heavy_equipment.listing', {
#             'root': '/heavy_equipment/heavy_equipment',
#             'objects': http.request.env['heavy_equipment.heavy_equipment'].search([]),
#         })

#     @http.route('/heavy_equipment/heavy_equipment/objects/<model("heavy_equipment.heavy_equipment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('heavy_equipment.object', {
#             'object': obj
#         })