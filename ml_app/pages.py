from otree.api import Page, WaitPage
from .models import Constants
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import logging

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
    # データの存在チェック
    if not dictator_data or len(dictator_data) < 3:  # 3ラウンド分のデータが必要
        print("Warning: Not enough training data available!")
        return 'X'  # デフォルト値を返す
        
    # --- 1) 学習データ整形
    X_train = []
    y_train = []
    
    print(f"=== AI学習データ ===")
    print(f"学習データ数: {len(dictator_data)}件")
    
    for d in dictator_data:
        try:
            Ax, Bx = d['Ax'], d['Bx']
            Ay, By = d['Ay'], d['By']
            print(f"ラウンドデータ: X({Ax},{Bx}), Y({Ay},{By}), 選択={d['choice']}")
            X_train.append(create_features(Ax, Bx, Ay, By))
            y_train.append(1 if d['choice'] == 'X' else 0)
        except KeyError as e:
            print(f"Warning: Missing key in data: {e}")
            print(f"Data record: {d}")
            continue
    
    # データの存在を再チェック
    if not X_train:
        print("Warning: No valid training examples after processing!")
        return 'X'  # デフォルト値を返す
    
    # NumPy配列に変換
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    
    print(f"=== 特徴量変換結果 ===")
    print(f"X_train shape: {X_train.shape}")
    print(f"y_train shape: {y_train.shape}")
    
    # --- 2) モデル学習
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X_train, y_train)

    # --- 3) 予測用データの特徴量作成
    (Ax_16, Bx_16), (Ay_16, By_16) = scenario_16
    print(f"\n=== 予測シナリオ ===")
    print(f"Option X: ({Ax_16}, {Bx_16})")
    print(f"Option Y: ({Ay_16}, {By_16})")
    
    X_test = np.array(create_features(Ax_16, Bx_16, Ay_16, By_16)).reshape(1, -1)
    print(f"X_test shape: {X_test.shape}")

    pred = clf.predict(X_test)[0]  # 1 -> 'X', 0 -> 'Y'
    predicted_choice = 'X' if pred == 1 else 'Y'
    print(f"\n=== 予測結果 ===")
    print(f"予測選択: {predicted_choice}")
    
    return predicted_choice

class Introduction(Page):
    pass

class AIDecision(Page):
    def before_next_page(self):
        # dictator_appの3回分のデータを取得
        dictator_data = []
        for p in self.group.get_players():
            if p.role() == 'A':  # ディクテーターのデータのみ必要
                decisions = p.participant.vars.get('dictator_decisions', [])
                print(f"\n=== プレイヤー{p.id_in_group}の決定データ ===")
                print(f"取得した決定数: {len(decisions)}件")
                
                for round_data in decisions:
                    try:
                        data = {
                            'Ax': round_data['payoff_x_a'],
                            'Bx': round_data['payoff_x_b'],
                            'Ay': round_data['payoff_y_a'],
                            'By': round_data['payoff_y_b'],
                            'choice': round_data['choice']
                        }
                        dictator_data.append(data)
                        print(f"ラウンドデータ追加: {data}")
                    except KeyError as e:
                        print(f"Error processing round data: {e}")
                        print(f"Round data: {round_data}")
        
        # 予測用シナリオを取得
        scenario = Constants.prediction_scenarios[self.group.selected_scenario_index]
        print(f"\n=== 選択されたシナリオ ===")
        print(f"シナリオ: {scenario}")
        
        # AI予測実行
        self.group.predicted_choice = train_and_predict(dictator_data, scenario)
        print(f"\n=== 最終予測結果 ===")
        print(f"予測選択: {self.group.predicted_choice}")
        
        # 報酬を設定
        print(f"\n=== 報酬計算 ===")
        for p in self.group.get_players():
            p.set_payoffs()
            print(f"プレイヤー{p.id_in_group}({p.role()})の報酬:")
            print(f"- AI予測による報酬: {p.participant.vars.get('ai_prediction_payoff', 0)}")
            print(f"- ディクテーターゲーム報酬: {p.participant.vars.get('selected_dictator_payoff', 0)}")
            print(f"- 合計報酬: {p.participant.payoff}")

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