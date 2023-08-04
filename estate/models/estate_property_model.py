from odoo import fields, models, api
from odoo.exceptions import UserError, AccessError
# from dateutil.relativedelta import relativedelta

class EstateProperties(models.Model):

	_name = "estate.property"

	_description = "Model for Real-Estate Properties"


	# name = fields.Char('Name',default='Unknown', required=True)
	title = fields.Char()
	description=fields.Text('Description')
	postcode=fields.Char('Postcode')
	date_availability = fields.Date('Date', copy=False,
									default=lambda self: fields.Datetime.today())
	# date_availability=fields.Date('Date', copy=False, )
	expected_price=fields.Float('Expected Price', required=True)
	selling_price=fields.Float('Selling Price', copy=False)
	bedrooms=fields.Integer(string='Bedrooms', default=2)
	living_area=fields.Integer('Living Area (sqm)')
	facades=fields.Integer('Facecades')
	garage=fields.Boolean('Garage')
	garden=fields.Boolean('Garden')
	garden_area=fields.Integer('Garden Area')
	garden_orientation = fields.Selection(
		string='Garden Orientation',
		selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
		help="Choose the orientation of the garden (North, South, East, or West)"
	)

	_sql_constraints = [
		('positive_expected_price', 'CHECK(expected_price > 0)', 'Expected price must be strictly positive!'),
		('positive_selling_price', 'CHECK(selling_price >= 0)', 'Selling price must be positive!')
	]

	state = fields.Selection(default='New' , selection=[('new', 'New'),('sold', 'Sold'),('canceled', 'Canceled')],string='State',copy=False)
	last_seen = fields.Datetime("Last Seen", default=lambda self: fields.Datetime.now())
	property_type=fields.Many2one('estate.property.type')
	# salesman = fields.Many2one('estate.property.type', string="Salesman")
	buyer = fields.Many2one('res.partner', string="Buyer", copy=False)
	# user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True,
	# 						  default=lambda self: self.env.user)



	# @api.model
	# def _default_name(self):
	# 	return self.env.user.name if self.env.user else 'Unknown'
	# salesperson=fields.Char('Sales_Person', default=_default_name, required=True)
	salesman = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True,
							  default=lambda self: self.env.user)

	tag_ids=fields.Many2many('estate.property.tag')

	offer_id=fields.One2many('estate.property.offer','property_id')
	total_area=fields.Integer('Total Area (sqm)', compute="_compute_balance")
	best_price=fields.Float('Best price')


	# price = fields.Float('Price')
	# status = fields.Selection(
	# 	[('accepted', 'Accepted'), ('refused', 'Refused')],
	# 	string='Status',
	# 	copy=False
	# )
	# partner_id = fields.Many2one('res.partner')

	@api.depends('living_area', 'garden_area')
	def _compute_balance(self):
		for line in self:
			line.total_area = line.living_area+line.garden_area




	partner_id = fields.Many2one("res.partner", string="Partner")


	@api.onchange("garden")
	def _onchange_partner_id(self):


		# Check if the garden field is set to True
		if self.garden:
			# Set default values for garden_area and garden_orientation
			self.garden_area = 10
			self.garden_orientation = 'north'
		else:
			# Clear the fields when garden is unset
			self.garden_area = False
			self.garden_orientation = False




		@api.constrains('expected_price', 'selling_price')
		def _check_selling_price(self):
			for record in self:
				if not float_is_zero(record.expected_price, precision_digits=2):
					if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) == -1:
						raise exceptions.ValidationError(
							"Selling price cannot be lower than 90% of the expected price!")


	def action_sold(self):
		for property in self:
			if property.state == 'canceled':
				raise UserError('A canceled property cannot be set as sold.')

	def action_cancel(self):
		for property in self:
			if property.state == 'sold':
				raise UserError('A sold property cannot be canceled.')
