from dataclasses import dataclass

PROGRAM_GAIN = 'gain'
PROGRAM_STABLE = 'stable'
PROGRAM_LOSE = 'lose'


@dataclass(frozen=True)
class ProgramConfig:
    title: str
    slug_prefix: str
    description: str
    calorie_multiplier: float
    carbs_ratio: float
    fat_ratio: float
    protein_ratio: float
    lunch_split_threshold: int
    dinner_range: tuple[int, int] = (100, 50)
    carbs_breakfast_share: float = 0.4


PROGRAMS = {
    PROGRAM_GAIN: ProgramConfig(
        title='GainWeight',
        slug_prefix='gain-weight',
        description='Program for gaining weight',
        calorie_multiplier=1.15,
        carbs_ratio=0.50,
        fat_ratio=0.20,
        protein_ratio=0.25,
        lunch_split_threshold=1000,
        carbs_breakfast_share=0.3,
    ),
    PROGRAM_STABLE: ProgramConfig(
        title='StableWeight',
        slug_prefix='stable-weight',
        description='Program for stable weight',
        calorie_multiplier=1.0,
        carbs_ratio=0.55,
        fat_ratio=0.20,
        protein_ratio=0.25,
        lunch_split_threshold=1000,
        dinner_range=(50, 100),
    ),
    PROGRAM_LOSE: ProgramConfig(
        title='LoseWeight',
        slug_prefix='lose-weight',
        description='Program for losing weight',
        calorie_multiplier=0.85,
        carbs_ratio=0.45,
        fat_ratio=0.20,
        protein_ratio=0.35,
        lunch_split_threshold=900,
    ),
}


def calculate_breakfast_calories(value):
    return round(value * 0.25, 1)


def calculate_lunch_calories(value):
    return round(value * 0.45, 1)


def calculate_dinner_calories(value):
    return round(value * 0.20, 1)


def calculate_snack_calories(value):
    return round(value * 0.05, 1)


def build_program_targets(program_kind, base_tdee):
    config = PROGRAMS[program_kind]
    value = base_tdee * config.calorie_multiplier
    breakfast_calories = calculate_breakfast_calories(value)
    lunch_calories = calculate_lunch_calories(value)
    dinner_calories = calculate_dinner_calories(value)
    lunch_calories2 = (
        lunch_calories / 2
        if lunch_calories > config.lunch_split_threshold
        else lunch_calories
    )
    snack_calories = calculate_snack_calories(value)

    amount_of_carbs = (value * config.carbs_ratio) / 4
    amount_of_fat = (value * config.fat_ratio) / 9
    amount_of_protein = (value * config.protein_ratio) / 4

    return {
        'value': round(value, 1),
        'program_kind': program_kind,
        'breakfast_calories': breakfast_calories,
        'lunch_calories': lunch_calories,
        'lunch_calories2': lunch_calories2,
        'divided_lunch_calories': lunch_calories2 if lunch_calories2 != lunch_calories else None,
        'dinner_calories': dinner_calories,
        'snack_calories': snack_calories,
        'snack_calories2': snack_calories,
        'snack2_calories': snack_calories,
        'amount_of_protein_for_breakfast': round(amount_of_protein * 0.3, 1),
        'amount_of_protein_for_lunch': round(amount_of_protein * 0.4, 1),
        'amount_of_protein_for_dinner': round(amount_of_protein * 0.3, 1),
        'amount_of_fat_for_breakfast': round(amount_of_fat * 0.4, 1),
        'amount_of_fat_for_lunch': round(amount_of_fat * 0.4, 1),
        'amount_of_fat_for_dinner': round(amount_of_fat * 0.2, 1),
        'amount_of_carbs_for_breakfast': round(
            amount_of_carbs * config.carbs_breakfast_share,
            1,
        ),
        'amount_of_carbs_for_lunch': round(amount_of_carbs * 0.4, 1),
        'amount_of_carbs_for_dinner': round(amount_of_carbs * 0.2, 1),
    }
