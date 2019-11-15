from odoo import models, fields, api


class project(models.Model):
    _name = 'heavy_equipment.project'
    _inherits = {'project.project': 'project_id'}
    _order = 'name'

    name = fields.Char(
        related='project_id.name',
        inherited=True,
        readonly=False,
        required=True,
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

    project = fields.Many2many(
        comodel_name='heavy_equipment.project',
        string='Proyecto',
        required='True',
    )

    active = fields.Bolean()

    site_1 = fields.Many2one(
        comodel_name='heavy_equipment.site',
        string='Sitio 1',
        required=True,
    )

    site_2 = fields.Many2one(
        comodel_name='heavy_equipment.site',
        string='Sitio 2',
        required=True,
    )

    distance = fields.Float(
        string='Distancia de Acarreo',
        default=0,
    )


class material(models.Model):
    _name = 'heavy_equipment.material'
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

    currency_id = fields.Many2one('res.currency')

    cost = fields.Monetary('Costo', 'currency_id')

    price = fields.Monetary('Precio', 'currency_id')


class work(models.Model):
    _name = 'heavy_equipment.work'
    _order = 'name'

    project = fields.Many2many(
        comodel_name='heavy_equipment.project',
        string='Proyecto',
        required='True',
    )

    vehicle = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículos en Obra',
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
        string='Cantidad Horas/M3',
        required=True,
    )

    total_quantity = fields.Float(
        string='Cantidad Total',
        readonly=True,
        compute=lambda x: x.unit_quantity * x.amount,
    )

    @api.constrains('repetitions', 'unit_quantity')
    def _no_negative(self):
        data = self.mapped('repetitions', 'unit_quantity')
        if any(n <= 0 for n in data):
            raise models.ValidationError('No se aceptan 0 o \
                                         números negativos')
