from otree.api import Page, WaitPage

class Welcome(Page):
    form_model = 'player'
    form_fields = ['consent']

    def app_after_this_page(self, upcoming_apps):
        if not self.player.consent:
            return upcoming_apps[-1]

page_sequence = [Welcome] 