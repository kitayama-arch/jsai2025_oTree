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

    def before_next_page(self):
        # 現在のラウンドの決定を保存
        scenario = Constants.payoff_scenarios[self.round_number - 1]
        if 'base_dictator_decisions' not in self.participant.vars:
            self.participant.vars['base_dictator_decisions'] = []
        
        decision = {
            'round': self.round_number,
            'payoff_x_a': scenario[0][0],
            'payoff_x_b': scenario[0][1],
            'payoff_y_a': scenario[1][0],
            'payoff_y_b': scenario[1][1],
            'choice': self.player.choice
        }
        self.participant.vars['base_dictator_decisions'].append(decision)

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
        # グループ全体で使用する選択ラウンドを決定
        selected_round = random.randint(1, Constants.num_rounds)
        self.group.selected_round = selected_round
        
        # 選択されたラウンドの情報を保存
        scenario = Constants.payoff_scenarios[selected_round - 1]
        # A役のプレイヤーから選択を取得
        dictator = [p for p in self.group.in_round(selected_round).get_players() if p.role() == 'A'][0]
        
        # 全プレイヤーに情報を保存
        for p in self.group.get_players():
            p.participant.vars['selected_base_round'] = selected_round
            p.participant.vars['selected_base_dictator_payoff'] = p.in_round(selected_round).payoff
            p.participant.vars['selected_round_details'] = {
                'round': selected_round,
                'choice': dictator.choice,
                'payoff_x_a': scenario[0][0],
                'payoff_x_b': scenario[0][1],
                'payoff_y_a': scenario[1][0],
                'payoff_y_b': scenario[1][1]
            }

class Results(Page):
    def vars_for_template(self):
        return {
            'round_number': self.round_number,
            'payoff': self.player.payoff,
            'role': self.player.role(),
        }

class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        selected_round = self.participant.vars['selected_base_round']
        selected_payoff = self.participant.vars['selected_base_dictator_payoff']
        details = self.participant.vars['selected_round_details']
        
        return {
            'selected_round': selected_round,
            'selected_payoff': selected_payoff,
            'role': self.player.role(),
            'initial_endowment': self.participant.vars.get('initial_endowment', 1200),
            'total_payoff': selected_payoff + self.participant.vars.get('initial_endowment', 1200),
            'selected_choice': details['choice'],
            'payoff_x_a': details['payoff_x_a'],
            'payoff_x_b': details['payoff_x_b'],
            'payoff_y_a': details['payoff_y_a'],
            'payoff_y_b': details['payoff_y_b']
        }

page_sequence = [Introduction, Decision, WaitForA, Results, SelectRoundWaitPage, FinalResults] 