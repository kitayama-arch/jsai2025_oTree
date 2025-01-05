from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
)

class Constants(BaseConstants):
    name_in_url = 'welcome'
    players_per_group = None
    num_rounds = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    consent = models.BooleanField(
        label='実験参加に同意しますか？',
        choices=[
            [True, 'はい'],
            [False, 'いいえ'],
        ]
    ) 