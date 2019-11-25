from odoo import models, fields, api


class project(models.Model):
    _name = 'heavy_equipment.project'
    _inherits = {'project.project': 'project_id'}
    _order = 'name'

    project_id = fields.Many2one(
        string='Proyecto',
        comodel_name='project.project',
        delegate=True,
        required=True,
        readonly=False,
        ondelete='cascade',
    )

    contractor = fields.Many2one(
        comodel_name='res.partner',
        string='Contratista',
    )

    start = fields.Date(
        string='Fecha de Inicio',
    )

    end = fields.Date(
        string='Fecha de Finalización',
    )

    description = fields.Text(
        string='Descripción',
    )

    vehicles = fields.Many2many(
        comodel_name='fleet.vehicle',
        string='Vehículos en Obra',
    )

    state = fields.Selection(
        [('draft', 'Borrador'),
         ('active', 'En ejecución'),
         ('done', 'Finalizado')],
        string='Estado',
        default='draft',
    )


class site(models.Model):
    _name = 'heavy_equipment.site'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
    )

    project = fields.Many2many(
        comodel_name='heavy_equipment.project',
        string='Proyecto',
        required='True',
    )

    external = fields.Boolean(
        string='Externo',
        required=True,
    )

    description = fields.Text(
        string='Descripción',
    )


class route(models.Model):
    _name = 'heavy_equipment.route'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
    )

    project = fields.Many2many(
        comodel_name='heavy_equipment.project',
        string='Proyecto',
        required='True',
    )

    active = fields.Boolean(
        default=True,
    )

    origin = fields.Many2one(
        comodel_name='heavy_equipment.site',
        string='Origen',
        required=True,
    )

    destination = fields.Many2one(
        comodel_name='heavy_equipment.site',
        string='Destino',
        required=True,
    )

    distance = fields.Float(
        string='Distancia de Acarreo',
        default=0,
    )

    currency_id = fields.Many2one(
        string='Moneda',
        comodel_name='res.currency',
        default=lambda x: x.env['res.currency'].search([], limit=1),
    )

    cost = fields.monetary(
        string='costo (m3/km)',
        currency_field='currency_id',
    )

    @api.constrains('distance')
    def _no_negative(self):
        data = self.mapped('distance')
        if any(n < 0 for n in data):
            raise models.ValidationError('No se aceptan números negativos')

    @api.onchange('origin', 'destination')
    def _name_route(self):
        if self.origin and self.destination:
            self.name = self.origin.name + ' - ' + self.destination.name


class material(models.Model):
    _name = 'heavy_equipment.material'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
    )

    description = fields.Text(
        string='Descripción',
    )

    project = fields.Many2many(
        comodel_name='heavy_equipment.project',
        string='Proyecto',
        required='True',
    )

    currency_id = fields.Many2one(
        string='Moneda',
        comodel_name='res.currency',
        default=lambda x: x.env['res.currency'].search([], limit=1),
    )

    cost = fields.Monetary(
        string='Costo (M3)',
        currency_field='currency_id',
    )

    price = fields.Monetary(
        string='Precio (M3)',
        currency_field='currency_id',
    )


class work(models.Model):
    _name = 'heavy_equipment.work'
    _order = 'date'

    project = fields.Many2one(
        comodel_name='heavy_equipment.project',
        string='Proyecto',
        required='True',
    )

    vehicle = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículo',
        required='True',
    )

    plate = fields.Char(
        comodel_name='fleet.vehicle',
        string='Placa',
        related='vehicle.license_plate',
        store=True,
    )

    date = fields.Date(
        string='Fecha',
        required='True',
    )

    work_type = fields.Selection(
        string='Tipo de Trabajo',
        required=True,
        default='trans',
        selection=[('trans', 'Transporte'),
                   ('hora', 'Horario')],
    )

    internal = fields.Boolean(
        string='Interno',
    )

    material = fields.Many2one(
        comodel_name='heavy_equipment.material',
    )

    route = fields.Many2one(
        comodel_name='heavy_equipment.route',
        string='Ruta',
    )

    site = fields.Many2one(
        comodel_name='heavy_equipment.site',
        string='Sitio',
    )

    amount = fields.Integer(
        string='Número de Viajes',
        default=1,
    )

    unit_quantity = fields.Float(
        string='Cantidad (Horas ó M3)',
        required=True,
    )

    total_quantity = fields.Float(
        string='Total',
        readonly=True,
        compute='_compute_total',
    )

    currency_id = fields.Many2one(
        string='moneda',
        comodel_name='res.currency',
        readonly=True,
    )

    total_cost = fields.monetary(
        string='Costo Total',
        currency_field='currency_id',
    )

    @api.depends('unit_quantity', 'amount', 'work_type')
    def _compute_total(self):
        for record in self:
            if record.work_type == 'hora':
                record.total_quantity = record.unit_quantity
                record.amount = 1
            else:
                record.total_quantity = record.unit_quantity * record.amount

    @api.constrains('amount', 'unit_quantity', 'work_type')
    def _no_negative(self):
        data = self.mapped('amount') + self.mapped('unit_quantity')
        if any(n <= 0 for n in data):
            raise models.ValidationError('No se aceptan 0 o \
                                         números negativos')


# class rate(models.Model):
#     _name = 'heavy_equipment.rate'
#     _order = 'name'
#
#     project = fields.Many2one(
#         comodel_name='heavy_equipment.project',
#         string='Proyecto',
#         required='True',
#     )
#
#     vehicle = fields.Many2many(
#         comodel_name='fleet.vehicle',
#         string='Vehículos',
#         required='True',
#     )
#
#     work_type = fields.Selection(
#         string='Tipo de Trabajo',
#         required=True,
#         default='trans',
#         selection=[('trans', 'Transporte'),
#                    ('hora', 'Horario')],
#     )
#
#     currency_id = fields.Many2one(
#         string='Moneda',
#         comodel_name='res.currency',
#         readonly=True,
#     )
#
#     cost = fields.monetary(
#         string='Costo Unitario',
#         currency_field='currency_id',
#     )
