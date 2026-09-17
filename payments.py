from telegram import LabeledPrice


EXTRA_ANALYSIS_STARS = 20
FULL_ANALYSIS_STARS = 100


def extra_analysis_price():

    return [
        LabeledPrice(
            label="Дополнительный анализ",
            amount=EXTRA_ANALYSIS_STARS
        )
    ]


def full_analysis_price():

    return [
        LabeledPrice(
            label="Полный эстетический анализ",
            amount=FULL_ANALYSIS_STARS
        )
    ]
