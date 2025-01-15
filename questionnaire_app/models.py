from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, widgets
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
        choices=[
            [1, '男性'], 
            [2, '女性'], 
            [3, 'その他'], 
            [4, '回答しない']
        ],
        widget=widgets.RadioSelect
    )
    
    age = models.IntegerField(
        label='年齢',
        min=18,
        max=100,
    )
    
    gakubu = models.IntegerField(
        initial=None,
        choices=[
            [1, '商学部'], 
            [2, '経済学部'],
            [3, '法学部'], 
            [4, '文学部'],
            [5, '政策学部'],
            [6, '神学部'],
            [7, '社会学部'],
            [8, '理工学部'], 
            [9, '文化情報学部'],
            [10, 'スポーツ健康科学部'],
            [11, '生命医科学部'], 
            [12, '心理学部'], 
            [13, 'GC学部'], 
            [14, 'GR学部'], 
            [15, 'ビジネス研究科'], 
            [16, '司法研究科'], 
            [17, '脳科学研究科'],
            [18, 'GS研究科'], 
            [19, 'その他']
        ],
        label='<b>あなたの学部(院生の方は所属学科と関連する学部を選択)</b>'
    )

    gakunen = models.IntegerField(
        initial=None,
        choices=[
            [1, '学部1年次生'], 
            [2, '学部2年次生'],
            [3, '学部3年次生'],
            [4, '学部4年次生'], 
            [5, '学部5年次生以上'], 
            [6, '大学院博士前期課程'], 
            [7, '大学院博士後期課程']
        ],
        label='<b>あなたの学年</b>',
        widget=widgets.RadioSelect
    )
    
    ai_satisfaction = models.IntegerField(
        label='AIの予測結果に対する総合的な満足度はどの程度ですか？（予測の正確さだけでなく、予測が示されるタイミングや方法なども含めて）',
        choices=[
            [1, '全く満足していない'],
            [2, 'あまり満足していない'],
            [3, 'やや満足していない'],
            [4, 'どちらともいえない'],
            [5, 'やや満足している'],
            [6, 'かなり満足している'],
            [7, '非常に満足している']
        ]
    )
    
    ai_understanding = models.IntegerField(
        label='AIによる意思決定の仕組みをどの程度理解できましたか？（AIがどのようにしてあなたの意思決定を学習し、予測を行っていたのかについて）',
        choices=[
            [1, '全く理解できなかった'],
            [2, 'あまり理解できなかった'],
            [3, 'やや理解できなかった'],
            [4, 'どちらともいえない'],
            [5, 'やや理解できた'],
            [6, 'かなり理解できた'],
            [7, '十分理解できた']
        ]
    )
    
    # 選好に関する質問
    selfish_preference = models.IntegerField(
        label='利己的選好：独裁者の報酬を最大化することをどの程度重視しましたか？',
        choices=[
            [1, '全く重視しなかった'],
            [2, 'あまり重視しなかった'],
            [3, 'やや重視しなかった'],
            [4, 'どちらともいえない'],
            [5, 'やや重視した'],
            [6, 'かなり重視した'],
            [7, '非常に重視した']
        ]
    )

    equality_preference = models.IntegerField(
        label='平等選好：不平等の最小化をどの程度重視しましたか？',
        choices=[
            [1, '全く重視しなかった'],
            [2, 'あまり重視しなかった'],
            [3, 'やや重視しなかった'],
            [4, 'どちらともいえない'],
            [5, 'やや重視した'],
            [6, 'かなり重視した'],
            [7, '非常に重視した']
        ]
    )

    efficiency_preference = models.IntegerField(
        label='効率性選好：合計報酬の最大化をどの程度重視しましたか？',
        choices=[
            [1, '全く重視しなかった'],
            [2, 'あまり重視しなかった'],
            [3, 'やや重視しなかった'],
            [4, 'どちらともいえない'],
            [5, 'やや重視した'],
            [6, 'かなり重視した'],
            [7, '非常に重視した']
        ]
    )

    competitive_preference = models.IntegerField(
        label='競争的選好：独裁者が受け手よりも高い報酬を得ることをどの程度重視しましたか？',
        choices=[
            [1, '全く重視しなかった'],
            [2, 'あまり重視しなかった'],
            [3, 'やや重視しなかった'],
            [4, 'どちらともいえない'],
            [5, 'やや重視した'],
            [6, 'かなり重視した'],
            [7, '非常に重視した']
        ]
    )

    # AIと機械学習に関する質問
    tech_trust = models.IntegerField(
        label='テクノロジーに対する信頼度はどの程度ですか？（一般的に、AIなどのテクノロジーをどの程度信頼できると考えているか）',
        choices=[
            [1, '全く信頼していない'],
            [2, 'あまり信頼していない'],
            [3, 'やや信頼していない'],
            [4, 'どちらともいえない'],
            [5, 'やや信頼している'],
            [6, 'かなり信頼している'],
            [7, '非常に信頼している']
        ]
    )

    prediction_accuracy = models.IntegerField(
        label='AI予測はあなたの意図した配分をどの程度正確に予測できていましたか？（予測額が実際にあなたが配分しようと考えていた金額とどの程度一致していたか）',
        choices=[
            [1, '全く一致していなかった'],
            [2, 'あまり一致していなかった'],
            [3, 'やや一致していなかった'],
            [4, 'どちらともいえない'],
            [5, 'やや一致していた'],
            [6, 'かなり一致していた'],
            [7, '完全に一致していた']
        ]
    )

    rf_understanding = models.IntegerField(
        label='ランダムフォレストアルゴリズムの仕組みをどの程度理解できましたか？（実験で使用した機械学習アルゴリズムの基本的な仕組みについて）',
        choices=[
            [1, '全く理解できなかった'],
            [2, 'あまり理解できなかった'],
            [3, 'やや理解できなかった'],
            [4, 'どちらともいえない'],
            [5, 'やや理解できた'],
            [6, 'かなり理解できた'],
            [7, '十分理解できた']
        ]
    ) 