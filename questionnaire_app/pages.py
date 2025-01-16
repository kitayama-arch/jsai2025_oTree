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

    def is_displayed(self):
        return self.session.config['name'] == 'ai_experiment'

class FinalResults(Page):
    def vars_for_template(self):
        print("\n=== 最終報酬計算開始 ===")
        # 実験条件に応じた報酬の取得
        if self.session.config['name'] == 'ai_experiment':
            # AI学習条件の場合
            dictator_payoff = self.participant.vars.get('dictator_game_payoff', 0)
            ai_payoff = self.participant.vars.get('ai_prediction_payoff', 0)
            selected_round = self.participant.vars.get('selected_round', 0)
            total_payoff = dictator_payoff + ai_payoff
            
            print(f"AI条件の報酬:")
            print(f"- ディクテーター報酬（ラウンド{selected_round}）: {dictator_payoff}")
            print(f"- AI予測報酬: {ai_payoff}")
            print(f"- 合計: {total_payoff}")
            
            # 最終的な報酬を設定
            self.participant.payoff = total_payoff

            # モデルに報酬を保存
            self.player.selected_dictator_round = selected_round
            self.player.selected_dictator_payoff = dictator_payoff
            self.player.ai_prediction_payoff = ai_payoff
            self.player.final_total_payoff = total_payoff
            
            return {
                'total_payoff': total_payoff,
                'dictator_payoff': dictator_payoff,
                'ai_payoff': ai_payoff,
                'selected_round': selected_round,
                'is_ai_condition': True
            }
        else:
            # 基本条件の場合
            # Base_dictator_appで保存された報酬を取得
            total_payoff = self.participant.vars.get('dictator_game_payoff', 0)
            selected_payoffs = self.participant.vars.get('selected_round_payoffs', [0, 0])
            
            print(f"ベースライン条件の報酬:")
            print(f"- 1回目: {selected_payoffs[0]}")
            if len(selected_payoffs) > 1:
                print(f"- 2回目: {selected_payoffs[1]}")
            print(f"- 合計: {total_payoff}")
            
            # 最終的な報酬を設定
            self.participant.payoff = total_payoff

            # モデルに報酬を保存
            self.player.final_total_payoff = total_payoff
            
            return {
                'total_payoff': total_payoff,
                'dictator_payoff1': selected_payoffs[0] if len(selected_payoffs) > 0 else 0,
                'dictator_payoff2': selected_payoffs[1] if len(selected_payoffs) > 1 else 0,
                'is_ai_condition': False
            }

page_sequence = [Demographics, PreferenceQuestions, AIFeedback, FinalResults] 