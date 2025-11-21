import pytest
from main import main


def test_cli_unknown_file(tmp_path, capsys):
    # путь к несуществующему файлу
    fake_file = tmp_path / "nope.csv"
    argv = ["--files", str(fake_file), "--report", "performance"]

    with pytest.raises(SystemExit) as excinfo:
        main(argv)

    assert excinfo.value.code == 2  # argparse.error -> код 2
    captured = capsys.readouterr()
    assert "не найден" in captured.err


def test_cli_missing_args():
    # вызов без обязательных аргументов
    with pytest.raises(SystemExit) as excinfo:
        main([])

    assert excinfo.value.code == 2
