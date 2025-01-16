from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c,
    widgets
)
import csv
import os

class Constants(BaseConstants):
    name_in_url = 'dictator'
    players_per_group = None  # すべてのプレイヤーを1つのグループに
    num_rounds = 15  # 15ラウンドに変更

    # CSVからペイオフシナリオを読み込む
    csv_path = os.path.join(os.path.dirname(__file__), 'payoff_scenarios.csv')
    payoff_scenarios = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Is_Training'] == 'True':
                payoff_scenarios.append((
                    (int(row['Option_X_Dictator']), int(row['Option_X_Receiver'])),
                    (int(row['Option_Y_Dictator']), int(row['Option_Y_Receiver']))
                ))

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    choice = models.StringField(
        choices=['X', 'Y'],
        widget=widgets.RadioSelect,
        label='配分を選択してください'
    )
    payoff_A = models.CurrencyField(initial=0)
    payoff_B = models.CurrencyField(initial=0)

    def role(self):
        return 'A'

    def set_payoffs(self):
        # A役のプレイヤーの選択に基づいて配分を決定
        scenario = Constants.payoff_scenarios[self.round_number - 1]
        if self.choice == 'X':
            self.payoff = c(scenario[0][0])
            self.payoff_A = c(scenario[0][0])
            self.payoff_B = c(scenario[0][1])
        else:
            self.payoff = c(scenario[1][0])
            self.payoff_A = c(scenario[1][0])
            self.payoff_B = c(scenario[1][1]) 