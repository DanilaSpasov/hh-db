import json

from src.file_manager import load_hh_data


def test_load_hh_data_groups_vacancies_by_employer(tmp_path) -> None:
    """Проверяет группировку вакансий по работодателям из JSON-файла."""
    filename = tmp_path / "vacancies.json"
    filename.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "id": "1",
                        "employer": {"id": "10", "name": "First"},
                    },
                    {
                        "id": "2",
                        "employer": {"id": "10", "name": "First"},
                    },
                    {
                        "id": "3",
                        "employer": {"id": "20", "name": "Second"},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = load_hh_data(str(filename))

    assert [group["employer"]["id"] for group in result] == ["10", "20"]
    assert [vacancy["id"] for vacancy in result[0]["vacancies"]] == [
        "1",
        "2",
    ]
    assert [vacancy["id"] for vacancy in result[1]["vacancies"]] == ["3"]
