from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c,
    widgets
)
import csv
import os

class Constants(BaseConstants):
    name_in_url = 'base_dictator'
    players_per_group = 2
    num_rounds = 3  # 一時的に3ラウンドに変更（本番では16ラウンド）

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
    def creating_session(self):
        self.group_randomly(fixed_id_in_group=True)

class Group(BaseGroup):
    selected_round = models.IntegerField(initial=0)  # 選ばれたラウンド番号を保存

class Player(BasePlayer):
    choice = models.StringField(
        choices=['X', 'Y'],
        widget=widgets.RadioSelect,
        label='配分を選択してください'
    )
    payoff_A = models.CurrencyField()
    payoff_B = models.CurrencyField()

    def role(self):
        return 'A' if self.id_in_group == 1 else 'B'

    def set_payoffs(self):
        # A役のプレイヤーの選択に基づいて配分を決定
        scenario = Constants.payoff_scenarios[self.round_number - 1]
        if self.choice == 'X':
            self.payoff_A = scenario[0][0]
            self.payoff_B = scenario[0][1]
        else:
            self.payoff_A = scenario[1][0]
            self.payoff_B = scenario[1][1]

        # 自分とペアのプレイヤーの報酬を設定
        if self.role() == 'A':
            self.payoff = self.payoff_A
            # B役のプレイヤーを取得して報酬を設定
            other_player = self.get_others_in_group()[0]
            other_player.payoff = self.payoff_B
            other_player.payoff_A = self.payoff_A
            other_player.payoff_B = self.payoff_B 