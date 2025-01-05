from otree.api import Page, WaitPage
from .models import Constants

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender']

class AIFeedback(Page):
    form_model = 'player'
    form_fields = ['ai_satisfaction', 'ai_understanding']

class FinalResults(Page):
    def vars_for_template(self):
        # ディクテーターゲームの報酬（ランダム1回分）
        dictator_payoff = self.participant.vars.get('selected_dictator_payoff', 0)
        
        # AI予測による報酬
        ai_payoff = self.participant.vars.get('ai_prediction_payoff', 0)
        
        # 合計（実労働タスクの報酬は含まない）
        total_payoff = dictator_payoff + ai_payoff
        
        return {
            'total_payoff': total_payoff,
            'dictator_payoff': dictator_payoff,
            'ai_payoff': ai_payoff
        }

page_sequence = [Demographics, AIFeedback, FinalResults] 