from odoo import fields, models, api


class EstateProperties(models.Model):

	_name = "estate.property.offer"

	_description = "Model for Real-Estate Properties"

	price = fields.Float('Price')
	status = fields.Selection(
		[('accepted', 'Accepted'), ('refused', 'Refused')],
		string='Status',
		copy=False
	)
	partner_id = fields.Many2one('res.partner', required=True)
	property_id = fields.Many2one('estate.property', required=True)
	validity = fields.Integer('Validity (Days)', default=7)
	date_deadline = fields.Date( string='Deadline',default=lambda self: fields.Date.today())


	def action_accept_offer(self):
		self.status = 'accepted'


	def action_refuse_offer(self):
		self.status = 'refused'



