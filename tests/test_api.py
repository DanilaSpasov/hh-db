from unittest.mock import Mock
from unittest.mock import patch

from src.api import get_hh_data


@patch("src.api.requests.get")
def test_get_hh_data_loads_all_vacancy_pages(mock_get) -> None:
    """Проверяет загрузку работодателя и всех страниц его вакансий."""
    employer_response = Mock()
    employer_response.json.return_value = {"id": "10", "name": "Company"}

    first_page = Mock()
    first_page.json.return_value = {
        "items": [{"id": "1"}],
        "pages": 2,
    }

    second_page = Mock()
    second_page.json.return_value = {
        "items": [{"id": "2"}],
        "pages": 2,
    }
    mock_get.side_effect = [employer_response, first_page, second_page]

    result = get_hh_data(["10"])

    assert result == [
        {
            "employer": {"id": "10", "name": "Company"},
            "vacancies": [{"id": "1"}, {"id": "2"}],
        }
    ]
    assert mock_get.call_args_list[1].kwargs["params"]["page"] == 0
    assert mock_get.call_args_list[2].kwargs["params"]["page"] == 1
    employer_response.raise_for_status.assert_called_once()
    first_page.raise_for_status.assert_called_once()
    second_page.raise_for_status.assert_called_once()
