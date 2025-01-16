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
    payoff_dictator = models.CurrencyField(initial=0)  # A役（独裁者）の報酬
    payoff_receiver = models.CurrencyField(initial=0)  # B役（受け手）の報酬

    def role(self):
        return 'A'

    def set_payoffs(self):
        """報酬を設定する"""
        # 選択に基づいて報酬を設定
        scenario = Constants.payoff_scenarios[self.round_number - 1]
        if self.choice == 'X':
            self.payoff_dictator = c(scenario[0][0])
            self.payoff_receiver = c(scenario[0][1])
        else:
            self.payoff_dictator = c(scenario[1][0])
            self.payoff_receiver = c(scenario[1][1])

        # プレイヤーの報酬を設定
        self.payoff = self.payoff_dictator

        # 決定を記録
        if 'dictator_decisions' not in self.participant.vars:
            self.participant.vars['dictator_decisions'] = []
        
        decision = {
            'round_number': self.round_number,
            'choice': self.choice,
            'payoff_dictator': self.payoff_dictator,
            'payoff_receiver': self.payoff_receiver,
            'scenario': {
                'x': scenario[0],
                'y': scenario[1]
            }
        }
        self.participant.vars['dictator_decisions'].append(decision) 