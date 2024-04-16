"""

Tools to work with anomaly correlation
"""
import logging


from maas_cds.model import CdsCamsTickets


LOGGER = logging.getLogger("AnomalyMixin")


class AnomalyMixin:
    """


    A mixin for entities having a cams_tickets attribute so origin and description
    can be updated according to the
    """

    @property
    def ticket_set(self):
        """A property wrapping the cams_tickets into a set

        Returns:
            set: a set of ticket identifier
        """
        return set(self.cams_tickets)

    def set_last_attached_ticket(self, ticket: CdsCamsTickets):
        """
        set last ticket and update origin / description

        Args:
            ticket (CdsCamsTickets): last attached ticket
        """
        LOGGER.debug("set_last_attached_ticket(%s, %s)", self, ticket)

        if not ticket.meta.id in self.cams_tickets:
            self.cams_tickets.append(ticket.meta.id)

        # fill last_* attributes
        self.last_attached_ticket = ticket.meta.id
        self.last_attached_ticket_url = ticket.url

        # fill fields from correlation file
        self.cams_origin = ticket.origin
        self.cams_description = ticket.description

    def unset_last_attached_ticket(self):
        """
        unset last ticket and update origin / description and populate to
        last ticket if any.

        warning: last_attached_ticket has to be removed from cams_tickets before call
        """
        if len(self.cams_tickets) > 0:

            # sure, we could search for the most recent but mget is blazing fast
            # and the cardinality will never be high
            tickets = list(CdsCamsTickets.mget_by_ids(self.cams_tickets))

            tickets.sort(key=lambda ticket: ticket.updated or ticket.created)

            self.set_last_attached_ticket(tickets[-1])

        else:
            # no more ticket attached: reset fields
            self.last_attached_ticket = None
            self.last_attached_ticket_url = None
            self.cams_origin = None
            self.cams_description = None
