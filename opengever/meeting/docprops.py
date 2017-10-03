from opengever.dossier.interfaces import IDocPropertyProvider
from opengever.meeting.proposal import IProposal
from zope.component import adapter
from zope.interface import implementer


@implementer(IDocPropertyProvider)
@adapter(IProposal)
class ProposalDocPropertyProvider(object):

    def __init__(self, context):
        self.context = context

    def get_meeting_properties(self):
        properties = {
            'decision_number': '',
            'agenda_item_number': '',
        }

        proposal_model = self.context.load_model()
        agenda_item = proposal_model.agenda_item
        if agenda_item:
            properties['decision_number'] = agenda_item.get_decision_number()
            properties['agenda_item_number'] = agenda_item.number

        return properties

    def get_properties(self):
        return {'ogg.meeting.' + key: value or ''
                for key, value
                in self.get_meeting_properties().items()}
