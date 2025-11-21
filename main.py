import argparse
import csv
from dataclasses import dataclass
from typing import Iterable, List, Dict, Tuple

from tabulate import tabulate


class ReportError(Exception):
    """Ошибки при формировании отчёта."""


@dataclass
class ReportResult:
    """Результат отчёта: заголовки и строки."""
    headers: List[str]
    rows: List[List]

# ======= Работа с данными =======
def read_employees(files: List[str]) -> List[Dict[str, str]]:
    """Читает все переданные csv-файлы и возвращает список строк-словарей."""
    employees: List[Dict[str, str]] = []
    required_columns = {"position", "performance"}

    for path in files:
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise ReportError(f"Файл {path!r} не содержит заголовков.")

                missing = required_columns - set(reader.fieldnames)
                if missing:
                    missing_str = ", ".join(sorted(missing))
                    raise ReportError(
                        f"В файле {path!r} отсутствуют обязательные колонки: {missing_str}"
                    )

                for row in reader:
                    employees.append(row)
        except FileNotFoundError as exc:
            # Преобразуем в нашу ошибку, чтобы одинаково обрабатывать в main()
            raise ReportError(f"Файл {path!r} не найден.") from exc

    if not employees:
        raise ReportError("Во всех файлах нет данных (только заголовки).")

    return employees

# ======= Отчёты =======
def performance_report(employees: Iterable[Dict[str, str]]) -> ReportResult:
    """
    Формирует отчёт по средней эффективности по позициям.

    Среднее считается по колонке 'performance' по всем файлам.
    """
    totals: Dict[str, Tuple[float, int]] = {}

    for row in employees:
        position_raw = row.get("position")
        performance_raw = row.get("performance")

        if position_raw is None or performance_raw is None:
            # формально не должно случиться, но на всякий случай
            continue

        position = position_raw.strip()
        if not position:
            continue

        try:
            performance = float(performance_raw)
        except (TypeError, ValueError):
            # Пропускаем некорректные значения
            continue

        total, count = totals.get(position, (0.0, 0))
        totals[position] = (total + performance, count + 1)

    if not totals:
        raise ReportError("Не удалось вычислить эффективность: нет валидных данных.")

    rows: List[List] = []
    for position, (total, count) in totals.items():
        avg = total / count
        # Округляем до двух знаков, как в примере
        rows.append([position, round(avg, 2)])

    # Сортировка по эффективности (по убыванию), затем по названию позиции
    rows.sort(key=lambda row: (-row[1], row[0]))

    return ReportResult(headers=["position", "performance"], rows=rows)


# Реестр отчётов: ключ -- имя, которое передаём в --report
REPORTS = {
    "performance": performance_report,
    # сюда можно будет добавить новые отчёты
}

# ======= CLI =======
def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Формирование отчётов по данным из csv-файлов сотрудников."
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        metavar="PATH",
        help="пути к csv-файлам с данными сотрудников",
    )
    parser.add_argument(
        "--report",
        required=True,
        choices=sorted(REPORTS.keys()),
        help="название отчёта (например: performance)",
    )
    return parser


def generate_report(args: argparse.Namespace) -> ReportResult:
    employees = read_employees(args.files)
    report_func = REPORTS[args.report]
    return report_func(employees)


def print_report(result: ReportResult) -> None:
    """Печатает отчёт в консоль в виде таблицы."""
    index = range(1, len(result.rows) + 1)
    table = tabulate(
        result.rows,
        headers=result.headers,
        showindex=index,
        tablefmt="simple",
        floatfmt=".2f",
    )
    print(table)


def main(argv: List[str] | None = None) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        result = generate_report(args)
    except ReportError as exc:
        parser.error(str(exc))

    print_report(result)


if __name__ == "__main__":
    main()