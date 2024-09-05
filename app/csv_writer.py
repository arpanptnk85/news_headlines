import csv

class CSVWriter():
    def write(filepath: str, data: list[dict[str, str]], headers: list[str]) -> bytes | None:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=',')
            writer.writeheader()
            for row in data:
                writer.writerow(row)