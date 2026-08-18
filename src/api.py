import requests


def get_hh_data(employer_ids: list[str]) -> list[dict]:
    """Получает данные работодателей и их вакансий через API hh.ru."""
    data = []
    headers = {"HH-User-Agent": "hh-db/1.0 (spasov2000@mail.ru)"}

    for employer_id in employer_ids:
        url = f"https://api.hh.ru/employers/{employer_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        employer_data = response.json()

        vacancies_data = []
        page = 0

        while True:
            vacancies_response = requests.get(
                "https://api.hh.ru/vacancies",
                headers=headers,
                params={
                    "employer_id": employer_id,
                    "page": page,
                    "per_page": 100,
                },
            )
            vacancies_response.raise_for_status()
            vacancies_page = vacancies_response.json()
            vacancies_data.extend(vacancies_page["items"])

            page += 1
            if page >= vacancies_page["pages"]:
                break

        data.append({
            "employer": employer_data,
            "vacancies": vacancies_data,
        })

    return data
