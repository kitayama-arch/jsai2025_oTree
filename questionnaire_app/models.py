from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
)

class Constants(BaseConstants):
    name_in_url = 'questionnaire'
    players_per_group = None
    num_rounds = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    gender = models.StringField(
        label='性別',
        choices=['男性', '女性', 'その他', '回答しない']
    )
    
    age = models.IntegerField(
        label='年齢',
        min=18,
        max=100
    )
    
    ai_satisfaction = models.IntegerField(
        label='AIの予測結果にどの程度満足していますか？',
        choices=[
            [1, '全く満足していない'],
            [2, 'あまり満足していない'],
            [3, 'どちらともいえない'],
            [4, 'やや満足している'],
            [5, '非常に満足している']
        ]
    )
    
    ai_understanding = models.IntegerField(
        label='AIによる意思決定の仕組みをどの程度理解できましたか？',
        choices=[
            [1, '全く理解できなかった'],
            [2, 'あまり理解できなかった'],
            [3, 'どちらともいえない'],
            [4, 'ある程度理解できた'],
            [5, '十分理解できた']
        ]
    )
    
    choice_reason = models.IntegerField(
        label='あなたが選択した配分額を選んだ理由として、以下の項目はどの程度当てはまりますか？',
        choices=[
            [1, '全く当てはまらない'],
            [2, 'あまり当てはまらない'],
            [3, 'どちらともいえない'],
            [4, 'やや当てはまる'],
            [5, '非常に当てはまる']
        ]
    )
    
    choice_reason_detail = models.LongStringField(
        label='その他、選択の理由があれば自由にご記入ください（任意）',
        blank=True
    ) 