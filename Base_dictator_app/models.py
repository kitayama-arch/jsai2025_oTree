from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c,
    widgets
)
import csv
import os
import random

class Constants(BaseConstants):
    name_in_url = 'base_dictator'
    players_per_group = None  # すべてのプレイヤーを1つのグループに
    num_rounds = 16

    # CSVからペイオフシナリオを読み込む
    csv_path = os.path.join(os.path.dirname(__file__), 'payoff_scenarios.csv')
    training_scenarios = []  # Is_Training = True のシナリオ
    prediction_scenarios = []  # Is_Training = False のシナリオ
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario = (
                (int(row['Option_X_Dictator']), int(row['Option_X_Receiver'])),
                (int(row['Option_Y_Dictator']), int(row['Option_Y_Receiver']))
            )
            if row['Is_Training'] == 'True':
                training_scenarios.append(scenario)
            else:
                prediction_scenarios.append(scenario)

class Subsession(BaseSubsession):
    def creating_session(self):
        # 各ラウンドで使用するシナリオを設定
        if self.round_number == Constants.num_rounds:
            # 最終ラウンドの場合
            for player in self.get_players():
                player.participant.vars['is_final_prediction'] = True
                # 最終ラウンドのシナリオを選択して保存
                selected_scenario = random.choice(Constants.prediction_scenarios)
                player.final_scenario_x_a = c(selected_scenario[0][0])
                player.final_scenario_x_b = c(selected_scenario[0][1])
                player.final_scenario_y_a = c(selected_scenario[1][0])
                player.final_scenario_y_b = c(selected_scenario[1][1])
        else:
            # 通常ラウンドの場合
            for player in self.get_players():
                player.participant.vars['is_final_prediction'] = False
                scenario = Constants.training_scenarios[self.round_number - 1]
                player.final_scenario_x_a = c(scenario[0][0])
                player.final_scenario_x_b = c(scenario[0][1])
                player.final_scenario_y_a = c(scenario[1][0])
                player.final_scenario_y_b = c(scenario[1][1])

class Group(BaseGroup):
    selected_round = models.IntegerField(initial=0)  # 選ばれたラウンド番号を保存
    is_final_prediction = models.BooleanField(initial=False)  # 最終予測ラウンドかどうか
    # 最終ラウンドのシナリオを保存
    final_scenario_x_a = models.CurrencyField()
    final_scenario_x_b = models.CurrencyField()
    final_scenario_y_a = models.CurrencyField()
    final_scenario_y_b = models.CurrencyField()

class Player(BasePlayer):
    choice = models.StringField(
        choices=['X', 'Y'],
        widget=widgets.RadioSelect,
        label='配分を選択してください'
    )
    payoff_A = models.CurrencyField(initial=0)
    payoff_B = models.CurrencyField(initial=0)
    
    # シナリオデータを保存するフィールド（初期値を0に設定）
    final_scenario_x_a = models.CurrencyField(initial=0)
    final_scenario_x_b = models.CurrencyField(initial=0)
    final_scenario_y_a = models.CurrencyField(initial=0)
    final_scenario_y_b = models.CurrencyField(initial=0)

    def role(self):
        return 'A'

    def set_payoffs(self):
        if self.participant.vars.get('is_final_prediction'):
            if self.choice == 'X':
                self.payoff = self.final_scenario_x_a
                self.payoff_A = self.final_scenario_x_a
                self.payoff_B = self.final_scenario_x_b
            else:
                self.payoff = self.final_scenario_y_a
                self.payoff_A = self.final_scenario_y_a
                self.payoff_B = self.final_scenario_y_b
        else:
            scenario = Constants.training_scenarios[self.round_number - 1]
            if self.choice == 'X':
                self.payoff = c(scenario[0][0])
                self.payoff_A = c(scenario[0][0])
                self.payoff_B = c(scenario[0][1])
            else:
                self.payoff = c(scenario[1][0])
                self.payoff_A = c(scenario[1][0])
                self.payoff_B = c(scenario[1][1])

        # 自分とペアのプレイヤーの報酬を設定（このラウンドのみ）
        if self.role() == 'A':
            self.payoff = self.payoff_A
            # B役のプレイヤーを取得して報酬を設定
            other_player = self.get_others_in_group()[0]
            other_player.payoff = self.payoff_B
            other_player.payoff_A = self.payoff_A
            other_player.payoff_B = self.payoff_B 