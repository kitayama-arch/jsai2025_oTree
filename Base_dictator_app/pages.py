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
        if self.participant.vars.get('is_final_round'):
            return {
                'round_number': self.round_number,
                'Ax': self.player.scenario_x_a,
                'Bx': self.player.scenario_x_b,
                'Ay': self.player.scenario_y_a,
                'By': self.player.scenario_y_b,
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

class Results(Page):
    def vars_for_template(self):
        return {
            'round_number': self.round_number,
            'payoff': self.player.payoff,
            'role': self.player.role(),
            'is_final_round': self.participant.vars.get('is_final_round', False)
        }

class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        print("\n=== ベースライン条件の報酬計算開始 ===")
        # ランダムに2ラウンドを選択
        selected_rounds = random.sample(range(1, Constants.num_rounds + 1), 2)
        selected_payoffs = []
        round_details = []
        
        print(f"選択されたラウンド: {selected_rounds}")
        
        for round_num in selected_rounds:
            round_player = self.player.in_round(round_num)
            
            if round_num == Constants.num_rounds:
                scenario = random.choice(Constants.prediction_scenarios)
            else:
                scenario = Constants.training_scenarios[round_num - 1]
            
            choice = round_player.choice
            payoff = round_player.payoff_dictator

            selected_payoffs.append(payoff)
            round_details.append({
                'round_number': round_num,
                'is_final_round': round_num == Constants.num_rounds,
                'payoff_x_dictator': scenario[0][0],
                'payoff_x_receiver': scenario[0][1],
                'payoff_y_dictator': scenario[1][0],
                'payoff_y_receiver': scenario[1][1],
                'choice': choice,
                'payoff': payoff
            })
            print(f"ラウンド{round_num}の報酬: {payoff}")

        # 合計報酬を計算
        total_payoff = sum(selected_payoffs)
        print(f"合計報酬: {total_payoff}")
        
        # 参加者の変数を保存
        self.participant.vars['selected_rounds'] = selected_rounds
        self.participant.vars['selected_round_payoffs'] = selected_payoffs
        self.participant.vars['round_details'] = round_details
        self.participant.vars['dictator_game_payoff'] = total_payoff
        
        # 最終的な報酬を設定
        self.participant.payoff = total_payoff
        
        print("=== 報酬計算完了 ===\n")
        return {
            'round_details': round_details,
            'role': self.player.role(),
            'total_payoff': total_payoff,
            'selected_round_payoffs': selected_payoffs
        }

page_sequence = [Introduction, Decision, Results, FinalResults] 