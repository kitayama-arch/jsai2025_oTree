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
        scenario = Constants.payoff_scenarios[self.round_number - 1]
        return {
            'round_number': self.round_number,
            'Ax': scenario[0][0],
            'Bx': scenario[0][1],
            'Ay': scenario[1][0],
            'By': scenario[1][1],
        }

class WaitForA(WaitPage):
    def after_all_players_arrive(self):
        # A役のプレイヤーを取得
        dictator = [p for p in self.group.get_players() if p.role() == 'A'][0]
        # 報酬を設定
        dictator.set_payoffs()

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

page_sequence = [Introduction, Decision, WaitForA, Results] 