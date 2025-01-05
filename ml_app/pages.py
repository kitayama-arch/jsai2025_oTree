from otree.api import Page, WaitPage
from .models import Constants
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def create_features(Ax, Bx, Ay, By):
    """特徴量8項目を作成"""
    return [
        Ax, Bx,           # X選択時
        Ay, By,           # Y選択時
        Ax + Bx, Ay + By, # 効率性
        Ax - Ay, Bx - By  # 不平等度等
    ]

def train_and_predict(dictator_data, scenario_16):
    """
    dictator_data: list of dicts
      e.g. [{'Ax':900, 'Bx':140, 'Ay':800, 'By':520, 'choice': 'X'}, ...]
    scenario_16: tuple((Ax, Bx), (Ay, By))
    """
    # --- 1) 学習データ整形
    X_train = []
    y_train = []
    for d in dictator_data:
        Ax, Bx = d['Ax'], d['Bx']
        Ay, By = d['Ay'], d['By']
        X_train.append(create_features(Ax, Bx, Ay, By))
        # choiceを 1 or 0 に変換
        y_train.append(1 if d['choice'] == 'X' else 0)
    
    # --- 2) モデル学習
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X_train, y_train)

    # --- 3) 予測用データの特徴量作成
    (Ax_16, Bx_16), (Ay_16, By_16) = scenario_16
    X_test = np.array(create_features(Ax_16, Bx_16, Ay_16, By_16)).reshape(1, -1)

    pred = clf.predict(X_test)[0]  # 1 -> 'X', 0 -> 'Y'
    return 'X' if pred == 1 else 'Y'

class Introduction(Page):
    pass

class AIDecision(Page):
    def before_next_page(self):
        # dictator_appの16回分のデータを取得
        dictator_data = []
        for p in self.group.get_players():
            if p.role() == 'A':  # ディクテーターのデータのみ必要
                for round_data in p.participant.vars.get('dictator_decisions', []):
                    dictator_data.append({
                        'Ax': round_data['payoff_x_a'],
                        'Bx': round_data['payoff_x_b'],
                        'Ay': round_data['payoff_y_a'],
                        'By': round_data['payoff_y_b'],
                        'choice': round_data['choice']
                    })
        
        # 予測用シナリオを取得
        scenario = Constants.prediction_scenarios[self.group.selected_scenario_index]
        
        # AI予測実行
        self.group.predicted_choice = train_and_predict(dictator_data, scenario)
        
        # 報酬を設定
        for p in self.group.get_players():
            p.set_payoffs()

class Results(Page):
    def vars_for_template(self):
        scenario = Constants.prediction_scenarios[self.group.selected_scenario_index]
        return {
            'predicted_choice': self.group.predicted_choice,
            'payoff': self.player.payoff,
            'Ax': scenario[0][0],
            'Bx': scenario[0][1],
            'Ay': scenario[1][0],
            'By': scenario[1][1],
        }

page_sequence = [Introduction, AIDecision, Results] 