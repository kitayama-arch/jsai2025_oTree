from otree.api import Page, WaitPage
from .models import Constants

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'gakubu', 'gakunen']

class PreferenceQuestions(Page):
    form_model = 'player'
    form_fields = [
        'selfish_preference',
        'equality_preference',
        'efficiency_preference',
        'competitive_preference'
    ]

class AIFeedback(Page):
    form_model = 'player'
    form_fields = [
        'ai_satisfaction',
        'ai_understanding',
        'tech_trust',
        'prediction_accuracy',
        'rf_understanding'
    ]

class FinalResults(Page):
    def vars_for_template(self):
        # 実験条件に応じた報酬の取得
        if self.session.config['name'] == 'ai_experiment':
            # AI学習条件の場合
            dictator_payoff = self.participant.vars.get('selected_dictator_payoff', 0)
            ai_payoff = self.participant.vars.get('ai_prediction_payoff', 0)
            total_payoff = dictator_payoff + ai_payoff
            
            return {
                'total_payoff': total_payoff,
                'dictator_payoff': dictator_payoff,
                'ai_payoff': ai_payoff
            }
        else:
            # 基本条件の場合
            # Base_dictator_appで保存された報酬を取得
            total_game_payoff = self.participant.vars.get('total_base_payoff', 0)
            selected_payoffs = self.participant.vars.get('selected_base_payoffs', [0, 0])
            
            return {
                'total_payoff': total_game_payoff,
                'dictator_payoff1': selected_payoffs[0],
                'dictator_payoff2': selected_payoffs[1]
            }

page_sequence = [Demographics, PreferenceQuestions, AIFeedback, FinalResults] 