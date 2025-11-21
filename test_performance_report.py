import textwrap
import pytest

from main import read_employees, performance_report, ReportError


def write_csv(path, content: str) -> None:
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def test_performance_report_average(tmp_path):
    file1 = tmp_path / "employees1.csv"
    file2 = tmp_path / "employees2.csv"

    write_csv(
        file1,
        """
        name,position,completed_tasks,performance,skills,team,experience_years
        A,Backend Developer,10,4.8,"",Team,3
        B,Backend Developer,20,5.0,"",Team,4
        C,QA Engineer,5,4.5,"",Team,1
        """,
    )

    write_csv(
        file2,
        """
        name,position,completed_tasks,performance,skills,team,experience_years
        D,Backend Developer,15,4.7,"",Team,2
        E,QA Engineer,12,4.3,"",Team,3
        """,
    )

    employees = read_employees([str(file1), str(file2)])
    result = performance_report(employees)

    # преобразуем в удобный словарь
    data = {row[0]: row[1] for row in result.rows}

    # (4.8 + 5.0 + 4.7) / 3 = 4.8333... -> 4.83
    assert pytest.approx(data["Backend Developer"], rel=1e-3) == 4.83
    # (4.5 + 4.3) / 2 = 4.4
    assert pytest.approx(data["QA Engineer"], rel=1e-3) == 4.40


def test_read_employees_missing_column(tmp_path):
    file1 = tmp_path / "bad.csv"
    write_csv(
        file1,
        """
        name,position,completed_tasks
        A,Backend Developer,10
        """,
    )

    with pytest.raises(ReportError):
        read_employees([str(file1)])