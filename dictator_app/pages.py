from otree.api import Page, WaitPage
from .models import Constants
import random

class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1

class AIExplanation(Page):
    def is_displayed(self):
        return self.round_number == 1

class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    def vars_for_template(self):
        scenario = Constants.payoff_scenarios[self.round_number - 1]
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
        scenario = Constants.payoff_scenarios[self.round_number - 1]
        if 'dictator_decisions' not in self.participant.vars:
            self.participant.vars['dictator_decisions'] = []
        
        decision = {
            'round': self.round_number,
            'payoff_x_a': scenario[0][0],
            'payoff_x_b': scenario[0][1],
            'payoff_y_a': scenario[1][0],
            'payoff_y_b': scenario[1][1],
            'choice': self.player.choice,
            'payoff': self.player.payoff
        }
        self.participant.vars['dictator_decisions'].append(decision)

class Results(Page):
    def vars_for_template(self):
        return {
            'round_number': self.round_number,
            'payoff': self.player.payoff,
            'role': self.player.role(),
        }

    def before_next_page(self):
        # 最終ラウンドでランダムに1回分の報酬を選ぶ
        if self.round_number == Constants.num_rounds:
            # ランダムにラウンドを選択
            selected_round = random.randint(1, Constants.num_rounds)
            
            # 選択されたラウンドのプレイヤーを取得
            selected_player = self.player.in_round(selected_round)
            
            # 選択されたラウンドの報酬を保存
            self.participant.vars['selected_dictator_payoff'] = selected_player.payoff
            self.participant.vars['selected_round'] = selected_round

page_sequence = [Introduction, AIExplanation, Decision, Results] 