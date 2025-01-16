from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c
)
import csv
import os
import random

class Constants(BaseConstants):
    name_in_url = 'ml_app'
    players_per_group = None  # すべてのプレイヤーを1つのグループに
    num_rounds = 1

    # CSVから予測用のペイオフシナリオを読み込む
    csv_path = os.path.join(os.path.dirname(__file__), '../dictator_app/payoff_scenarios.csv')
    prediction_scenarios = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Is_Training'] == 'False':
                prediction_scenarios.append((
                    (int(row['Option_X_Dictator']), int(row['Option_X_Receiver'])),
                    (int(row['Option_Y_Dictator']), int(row['Option_Y_Receiver']))
                ))

class Subsession(BaseSubsession):
    def creating_session(self):
        # 予測用の6つのゲームからランダムに1つを選択
        for player in self.get_players():
            player.selected_scenario_index = random.randrange(len(Constants.prediction_scenarios))

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    predicted_choice = models.StringField()  # AIの予測結果（'X' or 'Y'）
    selected_scenario_index = models.IntegerField()  # 選択されたシナリオのインデックス
    payoff_A = models.CurrencyField(initial=0)
    payoff_B = models.CurrencyField(initial=0)

    def role(self):
        return 'A'

    def set_payoffs(self):
        # AIの予測結果による報酬を設定
        scenario = Constants.prediction_scenarios[self.selected_scenario_index]
        if self.predicted_choice == 'X':
            self.payoff = c(scenario[0][0])
            self.payoff_A = c(scenario[0][0])
            self.payoff_B = c(scenario[0][1])
        else:
            self.payoff = c(scenario[1][0])
            self.payoff_A = c(scenario[1][0])
            self.payoff_B = c(scenario[1][1])

        # AIの予測結果による報酬をparticipant.varsに保存
        self.participant.vars['ai_prediction_payoff'] = self.payoff

        # ディクテーターゲームの報酬を設定
        if 'selected_dictator_payoff' in self.participant.vars:
            # AIの予測結果による報酬とディクテーターゲームの報酬の合計を設定
            self.participant.payoff = self.participant.vars['selected_dictator_payoff'] + self.payoff 