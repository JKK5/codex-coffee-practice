import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from analyze_coffee import load_valid_records, print_analysis


BASE_DIR = Path(__file__).parent


class AnalyzeCoffeeTest(unittest.TestCase):
    def analyze_output(self, csv_path: Path) -> tuple[list[dict[str, object]], int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            records, invalid_count = load_valid_records(csv_path)
            print_analysis(records, invalid_count)
        return records, invalid_count, output.getvalue()

    def test_normal_csv_results(self) -> None:
        records, invalid_count, output = self.analyze_output(
            BASE_DIR / "coffee_log.csv"
        )

        self.assertEqual(len(records), 4)
        self.assertEqual(invalid_count, 0)
        self.assertIn("평균 가격: 6,750원", output)
        self.assertIn("평균 평점: 4.25", output)
        self.assertIn("Ethiopia Sidama (5.0)", output)
        self.assertIn("Ethiopia: 4.50", output)

    def test_invalid_csv_skips_bad_rows_and_strips_text(self) -> None:
        records, invalid_count, output = self.analyze_output(
            BASE_DIR / "coffee_log_invalid_test.csv"
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(invalid_count, 5)
        self.assertEqual(records[0]["coffee"], "Brazil Santos")
        self.assertEqual(records[0]["country"], "Brazil")
        self.assertIn("평균 가격: 6,000원", output)
        self.assertIn("평균 평점: 4.50", output)
        self.assertIn("Kenya Peaberry (5.0)", output)
        self.assertIn("Brazil: 4.00", output)
        self.assertIn("Kenya: 5.00", output)
        self.assertIn("건너뛴 잘못된 행: 5개", output)

    def test_column_order_is_flexible(self) -> None:
        csv_text = (
            "rating,country,coffee,date,price,notes\n"
            "4.0,Brazil,Brazil Santos,2026-08-01,5000,extra\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reordered.csv"
            path.write_text(csv_text, encoding="utf-8")
            records, invalid_count = load_valid_records(path)

        self.assertEqual(len(records), 1)
        self.assertEqual(invalid_count, 0)

    def test_missing_required_column_is_an_error(self) -> None:
        csv_text = "date,coffee,country,price\n2026-08-01,Test,Brazil,5000\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            path.write_text(csv_text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "rating"):
                load_valid_records(path)


if __name__ == "__main__":
    unittest.main()
