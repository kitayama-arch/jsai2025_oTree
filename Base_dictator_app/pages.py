from otree.api import Page, WaitPage
from .models import Constants
import random

class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1

class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    def vars_for_template(self):
        if self.participant.vars.get('is_final_prediction'):
            return {
                'round_number': self.round_number,
                'Ax': self.player.final_scenario_x_a,
                'Bx': self.player.final_scenario_x_b,
                'Ay': self.player.final_scenario_y_a,
                'By': self.player.final_scenario_y_b,
            }
        else:
            scenario = Constants.training_scenarios[self.round_number - 1]
            return {
                'round_number': self.round_number,
                'Ax': scenario[0][0],
                'Bx': scenario[0][1],
                'Ay': scenario[1][0],
                'By': scenario[1][1],
            }

    def before_next_page(self):
        self.player.set_payoffs()
        # 現在のラウンドの決定を保存
        if self.participant.vars.get('is_final_prediction'):
            scenario_data = {
                'round': self.round_number,
                'payoff_x_a': self.player.final_scenario_x_a,
                'payoff_x_b': self.player.final_scenario_x_b,
                'payoff_y_a': self.player.final_scenario_y_a,
                'payoff_y_b': self.player.final_scenario_y_b,
                'choice': self.player.choice,
                'is_final_prediction': True
            }
        else:
            scenario = Constants.training_scenarios[self.round_number - 1]
            scenario_data = {
                'round': self.round_number,
                'payoff_x_a': scenario[0][0],
                'payoff_x_b': scenario[0][1],
                'payoff_y_a': scenario[1][0],
                'payoff_y_b': scenario[1][1],
                'choice': self.player.choice,
                'is_final_prediction': False
            }
        
        if 'base_dictator_decisions' not in self.participant.vars:
            self.participant.vars['base_dictator_decisions'] = []
        
        self.participant.vars['base_dictator_decisions'].append(scenario_data)

class Results(Page):
    def vars_for_template(self):
        return {
            'round_number': self.round_number,
            'payoff': self.player.payoff,
            'role': self.player.role(),
            'is_final_prediction': self.participant.vars.get('is_final_prediction', False)
        }

class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        print("\n=== ベースライン条件の報酬計算開始 ===")
        # ランダムに2ラウンドを選択
        selected_rounds = random.sample(range(1, Constants.num_rounds + 1), 2)
        selected_payoffs = []
        selected_details = []
        
        print(f"選択されたラウンド: {selected_rounds}")
        
        for round_num in selected_rounds:
            round_player = self.player.in_round(round_num)
            
            if round_num == Constants.num_rounds:
                scenario = random.choice(Constants.prediction_scenarios)
            else:
                scenario = Constants.training_scenarios[round_num - 1]
            
            choice = round_player.choice
            payoff = round_player.payoff

            selected_payoffs.append(payoff)
            selected_details.append({
                'round_number': round_num,
                'is_final_prediction': round_num == Constants.num_rounds,
                'payoff_x_a': scenario[0][0],
                'payoff_x_b': scenario[0][1],
                'payoff_y_a': scenario[1][0],
                'payoff_y_b': scenario[1][1],
                'choice': choice,
                'payoff': payoff
            })
            print(f"ラウンド{round_num}の報酬: {payoff}")

        # 合計報酬を計算（ディクテーターゲームの報酬のみ）
        total_game_payoff = sum(selected_payoffs)
        print(f"合計報酬: {total_game_payoff}")
        
        # 参加者の変数を保存
        self.participant.vars['selected_base_rounds'] = selected_rounds
        self.participant.vars['selected_base_payoffs'] = selected_payoffs
        self.participant.vars['selected_round_details'] = selected_details
        self.participant.vars['total_base_payoff'] = total_game_payoff
        
        # 最終的な報酬を設定（実労働タスクの報酬は含まない）
        self.participant.payoff = total_game_payoff
        
        print("=== 報酬計算完了 ===\n")
        return {
            'rounds_info': selected_details,
            'role': self.player.role(),
            'total_game_payoff': total_game_payoff
        }

page_sequence = [Introduction, Decision, Results, FinalResults] 