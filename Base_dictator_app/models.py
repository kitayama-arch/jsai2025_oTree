from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c,
    widgets
)
import csv
import os
import random

class Constants(BaseConstants):
    name_in_url = 'base_dictator'
    players_per_group = 2
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
                print(f"[DEBUG] 予測用シナリオを読み込み: X=({scenario[0][0]}, {scenario[0][1]}), Y=({scenario[1][0]}, {scenario[1][1]})")

class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly(fixed_id_in_group=True)
        
        if self.round_number == Constants.num_rounds:
            print(f"\n[DEBUG] 最終ラウンド（16回目）のセッション作成開始")
            print(f"利用可能な予測シナリオ数: {len(Constants.prediction_scenarios)}")
            for i, scenario in enumerate(Constants.prediction_scenarios):
                print(f"シナリオ{i+1}: X=({scenario[0][0]}, {scenario[0][1]}), Y=({scenario[1][0]}, {scenario[1][1]})")
            
            # 最終ラウンドではIs_Training=Falseのシナリオからランダムに1つ選択
            for group in self.get_groups():
                group.is_final_prediction = True
                # 最終ラウンドのシナリオを選択して保存
                selected_scenario = random.choice(Constants.prediction_scenarios)
                group.final_scenario_x_a = selected_scenario[0][0]
                group.final_scenario_x_b = selected_scenario[0][1]
                group.final_scenario_y_a = selected_scenario[1][0]
                group.final_scenario_y_b = selected_scenario[1][1]
                
                print(f"\n[DEBUG] グループ{group.id_in_subsession}の最終ラウンドシナリオ:")
                print(f"選択されたシナリオ: X=({selected_scenario[0][0]}, {selected_scenario[0][1]}), Y=({selected_scenario[1][0]}, {selected_scenario[1][1]})")
                print(f"保存された値:")
                print(f"選択肢X: A={group.final_scenario_x_a}, B={group.final_scenario_x_b}")
                print(f"選択肢Y: A={group.final_scenario_y_a}, B={group.final_scenario_y_b}")
        else:
            # それ以外のラウンドではIs_Training=Trueのシナリオを使用
            for group in self.get_groups():
                group.is_final_prediction = False

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
    payoff_A = models.CurrencyField()
    payoff_B = models.CurrencyField()

    def role(self):
        return 'A' if self.id_in_group == 1 else 'B'

    def set_payoffs(self):
        if self.group.is_final_prediction:
            print(f"\n[DEBUG] プレイヤー{self.id_in_group}（{self.role()}役）の最終ラウンド報酬設定:")
            print(f"保存されているシナリオ:")
            print(f"選択肢X: A={self.group.final_scenario_x_a}, B={self.group.final_scenario_x_b}")
            print(f"選択肢Y: A={self.group.final_scenario_y_a}, B={self.group.final_scenario_y_b}")
            
            # 最終ラウンドの場合、保存されたシナリオを使用
            if self.choice == 'X':
                self.payoff_A = self.group.final_scenario_x_a
                self.payoff_B = self.group.final_scenario_x_b
            else:
                self.payoff_A = self.group.final_scenario_y_a
                self.payoff_B = self.group.final_scenario_y_b
            
            print(f"選択: {self.choice}")
            print(f"設定された報酬: A={self.payoff_A}, B={self.payoff_B}")
        else:
            # 通常ラウンドの場合
            scenario = Constants.training_scenarios[self.round_number - 1]
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