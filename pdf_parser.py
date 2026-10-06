"""
pdf_parser.py

Extracts text and transactions from PDF bank statements.

Requirements:
    pypdf>=6,<7
"""

import re
from typing import List, Dict
from pypdf import PdfReader


class PDFParser:
    """
    Parses PDF bank statements and extracts text and transactions.
    """

    def __init__(self):
        pass

    def extract_text(self, pdf_file) -> str:
        """
        Extract all text from uploaded PDF.

        Parameters
        ----------
        pdf_file : UploadedFile or file object

        Returns
        -------
        str
        """

        reader = PdfReader(pdf_file)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    def split_lines(self, text: str) -> List[str]:
        """
        Split extracted text into clean lines.
        """

        lines = []

        for line in text.split("\n"):
            line = line.strip()

            if line != "":
                lines.append(line)

        return lines

    def extract_transactions(self, text: str) -> List[Dict]:
        """
        Extract transactions using regex.

        Expected example:

        01/01/2025 AMAZON -1500.50
        02/01/2025 SALARY 45000

        Returns list of dictionaries.
        """

        transactions = []

        lines = self.split_lines(text)

        pattern = re.compile(
            r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(-?\d+(?:,\d{3})*(?:\.\d{2})?)'
        )

        for line in lines:

            match = pattern.search(line)

            if match:

                date = match.group(1)

                description = match.group(2).strip()

                amount = float(
                    match.group(3).replace(",", "")
                )

                transaction = {
                    "date": date,
                    "description": description,
                    "amount": amount
                }

                transactions.append(transaction)

        return transactions

    def parse_pdf(self, pdf_file) -> Dict:
        """
        Complete parsing pipeline.

        Returns dictionary containing:
        - raw_text
        - lines
        - transactions
        """

        raw_text = self.extract_text(pdf_file)

        lines = self.split_lines(raw_text)

        transactions = self.extract_transactions(raw_text)

        return {
            "raw_text": raw_text,
            "lines": lines,
            "transactions": transactions
        }