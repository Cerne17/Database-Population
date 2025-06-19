import datetime
import random
from datetime import datetime, timedelta

from googletrans import Translator


async def translate(text):
    translator = Translator()
    translation = await translator.translate(text, dest="pt")
    return translation.text


def generate_cpf(format: bool = False) -> str:
    cpf = [random.randint(0, 9) for _ in range(9)]

    total = sum([(10 - i) * cpf[i] for i in range(9)])
    first_digit = (total * 10 % 11) % 10
    cpf.append(first_digit)

    total = sum([(11 - i) * cpf[i] for i in range(10)])
    second_digit = (total * 10 % 11) % 10
    cpf.append(second_digit)

    if format:
        return "{}{}{}.{}{}{}.{}{}{}-{}{}".format(*cpf)
    else:
        return "".join(map(str, cpf))


def generate_cnpj(format: bool = False) -> str:
    # Generate the first 8 digits (company base)
    cnpj = [random.randint(0, 9) for _ in range(8)]

    # Fixed branch identifier (0001 = headquarters)
    cnpj += [0, 0, 0, 1]

    # First check digit
    weight_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_first = sum([cnpj[i] * weight_first[i] for i in range(12)])
    first_digit = 11 - (sum_first % 11)
    first_digit = first_digit if first_digit < 10 else 0
    cnpj.append(first_digit)

    # Second check digit
    weight_second = [6] + weight_first
    sum_second = sum([cnpj[i] * weight_second[i] for i in range(13)])
    second_digit = 11 - (sum_second % 11)
    second_digit = second_digit if second_digit < 10 else 0
    cnpj.append(second_digit)

    if format:
        return "{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}".format(*cnpj)
    else:
        return "".join(map(str, cnpj))


def generate_random_datetime(
    datetime_inicial: datetime = datetime.datetime(2004, 1, 25, 0, 0, 0),
    datetime_final: datetime = datetime.datetime.now(),
):
    if datetime_inicial >= datetime_final:
        raise ValueError("datetime_inicial must be earlier than datetime_final")

    delta = datetime_final - datetime_inicial
    random_seconds = random.randint(0, int(delta.total_seconds()))
    random_dt = datetime_inicial + timedelta(seconds=random_seconds)

    # MS SQL Format: 'YYYY-MM-DD HH:MM:SS'
    formatted_str = random_dt.strftime("%Y-%m-%d %H:%M:%S")

    return random_dt, formatted_str
