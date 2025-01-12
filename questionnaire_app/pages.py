from otree.api import Page, WaitPage
from .models import Constants

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender']

class AIFeedback(Page):
    form_model = 'player'
    form_fields = [
        'ai_satisfaction', 
        'ai_understanding',
        'choice_reason',
        'choice_reason_detail'
    ]

class FinalResults(Page):
    def vars_for_template(self):
        # 共通の変数
        initial_endowment = self.participant.vars.get('initial_endowment', 1200)
        
        # 実験条件に応じた報酬の取得
        if self.session.config['name'] == 'ai_experiment':
            # AI学習条件の場合
            dictator_payoff = self.participant.vars.get('selected_dictator_payoff', 0)
            ai_payoff = self.participant.vars.get('ai_prediction_payoff', 0)
            total_payoff = initial_endowment + dictator_payoff + ai_payoff
            
            return {
                'total_payoff': total_payoff,
                'dictator_payoff': dictator_payoff,
                'ai_payoff': ai_payoff,
                'initial_endowment': initial_endowment
            }
        else:
            # 基本条件の場合
            base_dictator_payoff = self.participant.vars.get('total_base_payoff', 0)
            total_payoff = initial_endowment + base_dictator_payoff
            
            return {
                'total_payoff': total_payoff,
                'base_dictator_payoff': base_dictator_payoff,
                'initial_endowment': initial_endowment
            }

page_sequence = [Demographics, FinalResults] 