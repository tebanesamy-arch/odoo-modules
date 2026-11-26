from odoo import api, fields, models


class BiblioRoom(models.Model):
    _name = 'biblio.room'
    _description = 'Salle de travail'
    _order = 'name'

    name = fields.Char('Salle', required=True)
    seats = fields.Integer('Places')
    daily_price = fields.Float('Prix par jour', required=True)
    booking_ids = fields.One2many('biblio.room.booking', 'room_id', string='Réservations')
    # le nombre de réservations de la salle (champ calculé), pour le bouton intelligent
    booking_count = fields.Integer('Nombre de réservations', compute='_compute_booking_count')

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for room in self:
            room.booking_count = len(room.booking_ids)

    def action_view_bookings(self):
        """Bouton intelligent : ouvre la liste des réservations de cette salle."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Réservations',
            'res_model': 'biblio.room.booking',
            'view_mode': 'list,form',
            'domain': [('room_id', '=', self.id)],
            # une réservation créée depuis cette liste a la salle pré-remplie
            'context': {'default_room_id': self.id},
        }


class BiblioRoomBooking(models.Model):
    _name = 'biblio.room.booking'
    _description = "Réservation d'une salle"
    _order = 'start_date desc'

    room_id = fields.Many2one('biblio.room', string='Salle', required=True)
    customer = fields.Char('Réservé par', required=True)
    start_date = fields.Date('Début', required=True, default=fields.Date.context_today)
    end_date = fields.Date('Fin', required=True)
    deposit = fields.Float('Caution')

    # prix par jour : lu sur la salle (champ lié), pas recopié
    daily_price = fields.Float(related='room_id.daily_price', string='Prix par jour')
    # durée en jours, début et fin compris
    duration = fields.Integer('Durée (jours)', compute='_compute_duration')
    # prix total : stocké pour pouvoir trier et totaliser
    total_price = fields.Float('Prix total', compute='_compute_total_price', store=True)

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for booking in self:
            if booking.start_date and booking.end_date:
                # du 10 au 12 = 3 jours : on compte le premier et le dernier jour
                booking.duration = (booking.end_date - booking.start_date).days + 1
            else:
                booking.duration = 0

    @api.depends('start_date', 'end_date', 'room_id.daily_price')
    def _compute_total_price(self):
        for booking in self:
            if booking.start_date and booking.end_date:
                days = (booking.end_date - booking.start_date).days + 1
            else:
                days = 0
            booking.total_price = days * booking.room_id.daily_price

    # nom affiché : « Réservation <salle> – <date de début> »
    @api.depends('room_id.name', 'start_date')
    def _compute_display_name(self):
        for booking in self:
            date_str = booking.start_date.strftime('%d/%m/%Y') if booking.start_date else ''
            booking.display_name = f"Réservation {booking.room_id.name or ''} – {date_str}"

    # caution proposée quand on choisit la salle : 2 × le prix par jour
    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.deposit = 2 * self.room_id.daily_price
