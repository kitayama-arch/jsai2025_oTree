from otree.api import Page, WaitPage
from .models import Constants
import random

class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1

class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    def is_displayed(self):
        return self.player.role() == 'A'

    def vars_for_template(self):
        if self.group.is_final_prediction:
            return {
                'round_number': self.round_number,
                'Ax': self.group.final_scenario_x_a,
                'Bx': self.group.final_scenario_x_b,
                'Ay': self.group.final_scenario_y_a,
                'By': self.group.final_scenario_y_b,
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
        # 現在のラウンドの決定を保存
        if self.group.is_final_prediction:
            scenario_data = {
                'round': self.round_number,
                'payoff_x_a': self.group.final_scenario_x_a,
                'payoff_x_b': self.group.final_scenario_x_b,
                'payoff_y_a': self.group.final_scenario_y_a,
                'payoff_y_b': self.group.final_scenario_y_b,
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

class WaitForA(WaitPage):
    def after_all_players_arrive(self):
        # A役のプレイヤーを取得
        dictator = [p for p in self.group.get_players() if p.role() == 'A'][0]
        # 報酬を設定
        dictator.set_payoffs()

class SelectRoundWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def after_all_players_arrive(self):
        # 全ラウンドから2回分をランダムに選択
        selected_rounds = random.sample(range(1, Constants.num_rounds + 1), 2)
        self.group.selected_round = selected_rounds[0]  # 互換性のために1つ目を保存
        
        # 全プレイヤーに情報を保存
        for p in self.group.get_players():
            selected_payoffs = []
            selected_details = []
            
            # 2つの選択されたラウンドについて情報を収集
            for round_num in selected_rounds:
                round_player = p.in_round(round_num)
                round_group = round_player.group
                
                # シナリオ情報の取得
                if round_num == Constants.num_rounds:
                    # 最終ラウンドの場合
                    scenario = random.choice(Constants.prediction_scenarios)
                else:
                    # 通常ラウンドの場合
                    scenario = Constants.training_scenarios[round_num - 1]
                
                # A役プレイヤーの選択を取得
                dictator = [pl for pl in round_group.get_players() if pl.role() == 'A'][0]
                
                # 報酬と詳細を保存
                selected_payoffs.append(round_player.payoff)
                selected_details.append({
                    'round': round_num,
                    'choice': dictator.choice,
                    'payoff_x_a': scenario[0][0],
                    'payoff_x_b': scenario[0][1],
                    'payoff_y_a': scenario[1][0],
                    'payoff_y_b': scenario[1][1],
                    'is_final_prediction': round_num == Constants.num_rounds
                })
            
            # 情報を保存
            p.participant.vars['selected_base_rounds'] = selected_rounds
            p.participant.vars['selected_base_payoffs'] = selected_payoffs
            p.participant.vars['selected_round_details'] = selected_details
            # 合計報酬を計算
            total_game_payoff = sum(selected_payoffs)
            p.participant.vars['total_base_payoff'] = total_game_payoff
            
            # ログに計算式を出力
            initial_endowment = p.participant.vars.get('initial_endowment', 1200)
            total_payoff = total_game_payoff + initial_endowment
            
            print(f"""
=== プレイヤー {p.id_in_group} ({p.role()}役) の報酬計算 ===
選択されたラウンド: {selected_rounds}

1回目 (ラウンド {selected_rounds[0]}):
- 選択: {selected_details[0]['choice']}
- 報酬: {selected_payoffs[0]}ポイント
- シナリオ: X({selected_details[0]['payoff_x_a']}, {selected_details[0]['payoff_x_b']}) or Y({selected_details[0]['payoff_y_a']}, {selected_details[0]['payoff_y_b']})
- 追加ラウンド: {'はい' if selected_details[0]['is_final_prediction'] else 'いいえ'}

2回目 (ラウンド {selected_rounds[1]}):
- 選択: {selected_details[1]['choice']}
- 報酬: {selected_payoffs[1]}ポイント
- シナリオ: X({selected_details[1]['payoff_x_a']}, {selected_details[1]['payoff_x_b']}) or Y({selected_details[1]['payoff_y_a']}, {selected_details[1]['payoff_y_b']})
- 追加ラウンド: {'はい' if selected_details[1]['is_final_prediction'] else 'いいえ'}

計算式:
実労働タスク報酬: {initial_endowment}
ゲーム報酬: {selected_payoffs[0]} + {selected_payoffs[1]} = {total_game_payoff}
最終報酬: {initial_endowment} + {total_game_payoff} = {total_payoff}
""")

class Results(Page):
    def vars_for_template(self):
        return {
            'round_number': self.round_number,
            'payoff': self.player.payoff,
            'role': self.player.role(),
            'is_final_prediction': self.group.is_final_prediction
        }

class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        selected_rounds = self.participant.vars['selected_base_rounds']
        selected_payoffs = self.participant.vars['selected_base_payoffs']
        details = self.participant.vars['selected_round_details']
        total_game_payoff = self.participant.vars['total_base_payoff']
        
        # 各ラウンドの情報を組み合わせる
        rounds_info = []
        for i in range(len(selected_rounds)):
            rounds_info.append({
                'round_number': details[i]['round'],
                'is_final_prediction': details[i]['is_final_prediction'],
                'payoff_x_a': details[i]['payoff_x_a'],
                'payoff_x_b': details[i]['payoff_x_b'],
                'payoff_y_a': details[i]['payoff_y_a'],
                'payoff_y_b': details[i]['payoff_y_b'],
                'choice': details[i]['choice'],
                'payoff': selected_payoffs[i]
            })
        
        return {
            'rounds_info': rounds_info,
            'role': self.player.role(),
            'initial_endowment': self.participant.vars.get('initial_endowment', 1200),
            'total_game_payoff': total_game_payoff,
            'total_payoff': total_game_payoff + self.participant.vars.get('initial_endowment', 1200)
        }

page_sequence = [Introduction, Decision, WaitForA, Results, SelectRoundWaitPage, FinalResults] 