from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c
)
import csv
import os
import random

class Constants(BaseConstants):
    name_in_url = 'ml_app'
    players_per_group = 2
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
        # dictator_appと同じグループを維持
        for player in self.get_players():
            participant = player.participant
            participant.vars['ml_id_in_group'] = participant.vars.get('dictator_id_in_group', 0)
        
        # 予測用の6つのゲームからランダムに1つを選択
        for group in self.get_groups():
            group.selected_scenario_index = random.randrange(len(Constants.prediction_scenarios))

class Group(BaseGroup):
    predicted_choice = models.StringField()  # AIの予測結果（'X' or 'Y'）
    selected_scenario_index = models.IntegerField()  # 選択されたシナリオのインデックス

class Player(BasePlayer):
    payoff_A = models.CurrencyField()
    payoff_B = models.CurrencyField()

    def role(self):
        return 'A' if self.id_in_group == 1 else 'B'

    def set_payoffs(self):
        # AIの予測結果による報酬を設定
        scenario = Constants.prediction_scenarios[self.group.selected_scenario_index]
        if self.group.predicted_choice == 'X':
            self.payoff_A = scenario[0][0]
            self.payoff_B = scenario[0][1]
        else:
            self.payoff_A = scenario[1][0]
            self.payoff_B = scenario[1][1]

        # AIの予測結果による報酬を設定
        if self.role() == 'A':
            self.payoff = self.payoff_A
        else:
            self.payoff = self.payoff_B

        # AIの予測結果による報酬をparticipant.varsに保存
        if self.role() == 'A':
            self.participant.vars['ai_prediction_payoff'] = self.payoff_A
        else:
            self.participant.vars['ai_prediction_payoff'] = self.payoff_B

        # ディクテーターゲームの報酬を設定
        if 'selected_dictator_payoff' in self.participant.vars:
            # AIの予測結果による報酬とディクテーターゲームの報酬の合計を設定
            self.participant.payoff = self.participant.vars['selected_dictator_payoff'] + self.payoff 