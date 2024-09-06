import csv
from abc import ABC, abstractmethod

class CSVWriter(ABC):
    default_delimeter = ','

    @abstractmethod
    def write(self, filepath: str, data: list[dict[str, str]], headers: list[str]) -> None:
        pass

class DictCSVWriter(CSVWriter):

    def write(self, filepath: str, data: list[dict[str, str]], headers: list[str]) -> bytes | None:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=self.default_delimeter)
            writer.writeheader()
            for row in data:
                writer.writerow(row)