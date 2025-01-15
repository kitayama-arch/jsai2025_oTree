from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c
)
import random

class Constants(BaseConstants):
    name_in_url = 'real_effort'
    players_per_group = None
    num_rounds = 4  # 4つのタスク
    initial_points = 2000  # 初期ポイント
    points_per_task = 500  # タスクごとのポイント (2000/4)
    binary_length = 500  # バイナリ文字列の長さ
    patterns = ['00100', '11011', '10101', '01010']  # 各ラウンドで探すパターン（5桁）

class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            # ランダムなバイナリ文字列を生成
            binary_string = ''.join(random.choice('01') for _ in range(Constants.binary_length))
            # パターンを1回は必ず含めるように挿入
            pattern = Constants.patterns[self.round_number - 1]
            insert_pos = random.randint(0, Constants.binary_length - len(pattern))
            binary_string = (
                binary_string[:insert_pos] + 
                pattern + 
                binary_string[insert_pos + len(pattern):]
            )[:Constants.binary_length]
            p.binary_string = binary_string

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    binary_string = models.StringField()  # 表示される二進数文字列
    selected_sequence = models.StringField(blank=True)  # プレイヤーが選択した文字列
    sequence_start = models.IntegerField(blank=True)  # 選択開始位置
    is_correct = models.BooleanField(initial=False)  # 正解したかどうか
    earned_points = models.IntegerField(initial=0)  # 獲得ポイント
    
    def check_answer(self):
        pattern = Constants.patterns[self.round_number - 1]
        selected_text = self.binary_string[self.sequence_start:self.sequence_start + 5]
        if selected_text == pattern:
            self.is_correct = True
            self.earned_points = Constants.points_per_task
            if self.round_number == Constants.num_rounds:
                # 最終ラウンドで全ポイントを設定
                self.participant.vars['initial_endowment'] = sum([
                    p.earned_points for p in self.in_all_rounds()
                ])
        return self.is_correct 