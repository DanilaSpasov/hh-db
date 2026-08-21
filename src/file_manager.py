import json


def load_hh_data(filename: str) -> list[dict]:
    """Загружает вакансии из JSON-файла и группирует их по работодателям."""
    with open(filename, encoding="utf-8") as file:
        vacancies = json.load(file)["items"]

    employers = {}

    for vacancy in vacancies:
        employer = vacancy["employer"]
        employer_id = employer["id"]

        if employer_id not in employers:
            employers[employer_id] = {
                "employer": employer,
                "vacancies": [],
            }

        employers[employer_id]["vacancies"].append(vacancy)

    return list(employers.values())
