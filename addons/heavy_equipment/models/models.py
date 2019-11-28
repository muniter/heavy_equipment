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

    rate = fields.Many2one(
        string='Tarifa',
        comodel_name='heavy_equipment.rate',
    )

    currency_id = fields.Many2one(
        string='Moneda',
        related='rate.currency_id',
    )

    rate_val = fields.Monetary(
        related='rate.rate',
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
        string='Costo Compra (M3)',
        currency_field='currency_id',
    )

    price = fields.Monetary(
        string='Precio Venta (M3)',
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

    route_distance = fields.Float(
        string='Acarreo (Km)',
        related='route.distance',
        readonly=True,
    )

    volume_distance = fields.Float(
        string='M3/Km',
        readonly=True,
        compute='_compute_cost',
        store=True,
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
        string='Cantidad (Hr ó M3)',
        required=True,
    )

    total_quantity = fields.Float(
        string='Total',
        readonly=True,
        compute='_compute_total',
    )

    rate = fields.Many2one(
        required=False,
        readonly=False,
        store=True,
        compute='_compute_rate',
        string='Tarifa',
        comodel_name='heavy_equipment.rate',
    )

    currency_id = fields.Many2one(
        string='Moneda',
        related='rate.currency_id',
    )

    rate_val = fields.Monetary(
        related='rate.rate',
        currency_field='currency_id',
    )

    total_cost = fields.Monetary(
        string='Costo Total',
        store=True,
        currency_field='currency_id',
        compute='_compute_cost',
    )

    @api.constrains('amount', 'unit_quantity')
    def _no_negative(self):
        data = self.mapped('amount') + self.mapped('unit_quantity')
        if any(n <= 0 for n in data):
            raise models.ValidationError('No se aceptan 0 o \
                                         números negativos')

    @api.onchange('work_type', 'vehicle', 'project')
    def _select_rate(self):
        for record in self:
            if record.work_type == 'trans':
                record.rate = record.route.rate
            elif record.project and record.vehicle and not record.rate:
                record.rate = record.env['heavy_equipment.rate'].search(
                    [('project', '=', record.project.id),
                     ('work_type', '=', 'hora'),
                     ('vehicles', 'in', record.vehicle.id)])

    @api.depends('work_type', 'vehicle', 'project')
    def _compute_rate(self):
        for record in self:
            if record.work_type == 'trans':
                record.rate = record.route.rate
            elif record.project and record.vehicle and not record.rate:
                record.rate = record.env['heavy_equipment.rate'].search(
                    [('project', '=', record.project.id),
                     ('work_type', '=', 'hora'),
                     ('vehicles', 'in', record.vehicle.id)])

    @api.depends('unit_quantity', 'amount', 'work_type')
    def _compute_total(self):
        for record in self:
            if record.work_type == 'hora':
                record.total_quantity = record.unit_quantity
                record.amount = 1
            else:
                record.total_quantity = record.unit_quantity * record.amount

    @api.depends('route_distance', 'rate', 'rate_val', 'total_quantity',
                 'volume_distance')
    def _compute_cost(self):
        for record in self:
            if record.work_type == 'trans':
                rate = record.rate.rate * record.route.distance
                record.volume_distance = record.total_quantity *\
                    record.route_distance
            else:
                rate = record.rate.rate
                record.volume_distance = 0

            record.total_cost = record.total_quantity * rate


class rate(models.Model):
    _name = 'heavy_equipment.rate'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
    )

    description = fields.Text(
        string='Descripción',
    )

    project = fields.Many2one(
        comodel_name='heavy_equipment.project',
        string='Proyecto',
        required='False',
    )

    vehicles = fields.Many2many(
        comodel_name='fleet.vehicle',
        string='Vehículos',
        required='True',
    )

    work_type = fields.Selection(
        string='Tipo de Trabajo',
        required=True,
        default='trans',
        selection=[('trans', 'Transporte'),
                   ('hora', 'Horario')],
    )

    currency_id = fields.Many2one(
        string='Moneda',
        comodel_name='res.currency',
        default=lambda x: x.env['res.currency'].search([], limit=1),
    )

    rate = fields.Monetary(
        string='Tarifa M3/Km o Hr',
        currency_field='currency_id',
    )
