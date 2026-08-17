import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import median


DEFAULT_CSV_PATH = Path(__file__).with_name("coffee_log.csv")
REQUIRED_COLUMNS = {"date", "coffee", "country", "price", "rating"}


def load_valid_records(path: Path) -> tuple[list[dict[str, object]], int]:
    """CSV에서 정상 행만 반환하고 잘못된 행은 경고 후 건너뛴다."""
    valid_records: list[dict[str, object]] = []
    invalid_count = 0

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - fieldnames
        if missing_columns:
            raise ValueError(
                f"필수 CSV 열이 빠졌습니다: {', '.join(sorted(missing_columns))}"
            )

        for line_number, row in enumerate(reader, start=2):
            try:
                coffee = row["coffee"].strip()
                country = row["country"].strip()
                if not coffee or not country:
                    raise ValueError("coffee와 country는 비어 있을 수 없습니다")

                price = float(row["price"])
                if not math.isfinite(price) or price < 0:
                    raise ValueError("price는 유한한 0 이상의 숫자여야 합니다")

                rating = float(row["rating"])
                if not math.isfinite(rating) or not 1 <= rating <= 5:
                    raise ValueError("rating은 유한한 1~5 범위의 숫자여야 합니다")
            except (AttributeError, TypeError, ValueError) as error:
                invalid_count += 1
                print(f"경고: {line_number}행을 건너뜁니다 ({error}).")
                continue

            valid_records.append(
                {
                    **row,
                    "coffee": coffee,
                    "country": country,
                    "price": price,
                    "rating": rating,
                }
            )

    return valid_records, invalid_count


def calculate_analysis(records: list[dict[str, object]]) -> dict[str, object]:
    average_price = sum(float(row["price"]) for row in records) / len(records)
    median_price = median(float(row["price"]) for row in records)
    average_rating = sum(float(row["rating"]) for row in records) / len(records)
    highest_rating = max(float(row["rating"]) for row in records)
    highest_rated = [
        row for row in records if float(row["rating"]) == highest_rating
    ]

    ratings_by_country: dict[str, list[float]] = defaultdict(list)
    for row in records:
        ratings_by_country[str(row["country"])].append(float(row["rating"]))
    country_averages = {
        country: sum(ratings) / len(ratings)
        for country, ratings in sorted(ratings_by_country.items())
    }

    return {
        "average_price": average_price,
        "median_price": median_price,
        "average_rating": average_rating,
        "highest_rated": highest_rated,
        "country_averages": country_averages,
    }


def print_analysis(records: list[dict[str, object]], invalid_count: int) -> None:
    if not records:
        print("분석 가능한 정상 데이터가 없습니다.")
        print(f"건너뛴 잘못된 행: {invalid_count}개")
        return

    analysis = calculate_analysis(records)

    print(f"평균 가격: {float(analysis['average_price']):,.0f}원")
    print(f"중앙값 가격: {float(analysis['median_price']):,.0f}원")
    print(f"평균 평점: {float(analysis['average_rating']):.2f}")
    print("가장 평점 높은 커피:")
    for row in analysis["highest_rated"]:
        print(f"  {row['coffee']} ({float(row['rating']):.1f})")
    print("국가별 평균 평점:")
    for country, average in analysis["country_averages"].items():
        print(f"  {country}: {average:.2f}")
    print(f"건너뛴 잘못된 행: {invalid_count}개")


def save_analysis_csv(records: list[dict[str, object]], path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["metric", "name", "value"])
        if not records:
            return

        analysis = calculate_analysis(records)
        writer.writerow(["average_price", "", f"{analysis['average_price']:.2f}"])
        writer.writerow(["median_price", "", f"{analysis['median_price']:.2f}"])
        writer.writerow(["average_rating", "", f"{analysis['average_rating']:.2f}"])
        for row in analysis["highest_rated"]:
            writer.writerow(
                ["highest_rated_coffee", row["coffee"], f"{row['rating']:.2f}"]
            )
        for country, average in analysis["country_averages"].items():
            writer.writerow(["country_average_rating", country, f"{average:.2f}"])


def main() -> None:
    parser = argparse.ArgumentParser(description="커피 기록 CSV 분석")
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help="분석할 CSV 경로 (기본값: coffee_log.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="분석 결과를 저장할 CSV 경로",
    )
    args = parser.parse_args()

    try:
        records, invalid_count = load_valid_records(args.csv_path)
        print_analysis(records, invalid_count)
        if args.output:
            save_analysis_csv(records, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"오류: {error}\n")


if __name__ == "__main__":
    main()
