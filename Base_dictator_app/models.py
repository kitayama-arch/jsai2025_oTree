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
                player.participant.vars['is_final_round'] = True
                # 最終ラウンドのシナリオを選択して保存
                selected_scenario = random.choice(Constants.prediction_scenarios)
                player.scenario_x_a = c(selected_scenario[0][0])
                player.scenario_x_b = c(selected_scenario[0][1])
                player.scenario_y_a = c(selected_scenario[1][0])
                player.scenario_y_b = c(selected_scenario[1][1])
        else:
            # 通常ラウンドの場合
            for player in self.get_players():
                player.participant.vars['is_final_round'] = False
                scenario = Constants.training_scenarios[self.round_number - 1]
                player.scenario_x_a = c(scenario[0][0])
                player.scenario_x_b = c(scenario[0][1])
                player.scenario_y_a = c(scenario[1][0])
                player.scenario_y_b = c(scenario[1][1])

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
    
    # シナリオデータを保存するフィールド
    scenario_x_a = models.CurrencyField(initial=0)
    scenario_x_b = models.CurrencyField(initial=0)
    scenario_y_a = models.CurrencyField(initial=0)
    scenario_y_b = models.CurrencyField(initial=0)

    def role(self):
        return 'A'

    def set_payoffs(self):
        """報酬を設定する"""
        # 選択に基づいて報酬を設定
        if self.choice == 'X':
            self.payoff_dictator = self.scenario_x_a
            self.payoff_receiver = self.scenario_x_b
        else:
            self.payoff_dictator = self.scenario_y_a
            self.payoff_receiver = self.scenario_y_b

        # プレイヤーの報酬を設定
        self.payoff = self.payoff_dictator

        # 決定を記録
        if 'dictator_decisions' not in self.participant.vars:
            self.participant.vars['dictator_decisions'] = []
        
        decision = {
            'round_number': self.round_number,
            'is_final_round': self.participant.vars.get('is_final_round', False),
            'choice': self.choice,
            'payoff_dictator': self.payoff_dictator,
            'payoff_receiver': self.payoff_receiver,
            'scenario': {
                'x': (self.scenario_x_a, self.scenario_x_b),
                'y': (self.scenario_y_a, self.scenario_y_b)
            }
        }
        self.participant.vars['dictator_decisions'].append(decision) 