from otree.api import Page
from .models import Constants

class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return {
            'total_rounds': Constants.num_rounds,
            'points_per_task': Constants.points_per_task,
            'total_points': Constants.initial_points,
        }

class Task(Page):
    form_model = 'player'
    form_fields = ['sequence_start']

    def vars_for_template(self):
        return {
            'binary_string': self.player.binary_string,
            'round_number': self.round_number,
            'total_rounds': Constants.num_rounds,
            'pattern_to_find': Constants.patterns[self.round_number - 1],
            'points_per_task': Constants.points_per_task,
            'pattern_length': 5,
        }

    def error_message(self, values):
        if values['sequence_start'] is None:
            return '開始位置を選択してください。'
        selected_text = self.player.binary_string[values['sequence_start']:values['sequence_start'] + 5]
        pattern = Constants.patterns[self.round_number - 1]
        if selected_text != pattern:
            return 'このパターンは正しくありません。別の位置を試してください。'

    def before_next_page(self):
        self.player.check_answer()

class Results(Page):
    def vars_for_template(self):
        return {
            'round_number': self.round_number,
            'total_rounds': Constants.num_rounds,
            'is_correct': self.player.is_correct,
            'earned_points': self.player.earned_points,
            'total_points': sum([p.earned_points for p in self.player.in_all_rounds()]),
            'is_final_round': self.round_number == Constants.num_rounds,
        }

page_sequence = [Introduction, Task, Results] 