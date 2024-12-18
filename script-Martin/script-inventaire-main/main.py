"""
This program implements a command-line interface for managing stock
information.
"""
import argparse
import os
import pandas as pd
from cmd import Cmd
from colorama import Fore, Style, init

# Initialize colorama for styled terminal output
init(autoreset=True)


def error_output(message):
    """Display an error message in red."""
    print(Fore.RED + message + Style.RESET_ALL)


def success_output(message):
    """Display a success message in green."""
    print(Fore.GREEN + message + Style.RESET_ALL)


def info_output(message):
    """Display an informational message in blue."""
    print(Fore.BLUE + message + Style.RESET_ALL)


class StockManager(Cmd):
    """
    A command-line tool to manage and manipulate product stock data.
    """
    intro = (
        "\nWelcome to Stock Manager. The following commands are available:\n"
        "1. add_data <directory_path>  - Load CSV files from a directory\n"
        "2. query <column=value>  - Search for stock items by specific "
        "criteria\n"
        "3. generate <output_file_path> - Create a summary report\n"
        "4. show_top <number>  - Display the top N records of the data\n"
        "Type the command with the necessary arguments to begin.\n"
    )
    prompt = "(manager) "

    def __init__(self):
        super().__init__()
        self.data = pd.DataFrame()

    def do_add_data(self, directory):
        """
        Import CSV files from a directory and consolidate them into
        a single dataset.
        Usage: add_data <directory_path>
        """
        directory = directory.strip()
        if not os.path.isdir(directory):
            error_output("Directory not found.")
            return

        files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        if not files:
            error_output("No CSV files found.")
            return

        frames = []
        for file in files:
            file_path = os.path.join(directory, file)
            try:
                df = pd.read_csv(file_path)
                frames.append(df)
                success_output(f"Successfully loaded: {file}")
            except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
                error_output(f"Error loading {file}: {e}")

        if frames:
            self.data = pd.concat(frames, ignore_index=True)
            success_output("All files have been merged.")
        else:
            error_output("No valid data loaded.")

    def do_query(self, condition):
        """
        Search for stock items based on specific conditions.
        Usage: query <column=value>
        """
        if self.data.empty:
            error_output("No data available. Please add data first.")
            return

        try:
            column, value = condition.split('=')
            column, value = column.strip(), value.strip()

            if column not in self.data.columns:
                error_output(f"Column '{column}' not found.")
                return

            result = self.data[
                self.data[column].astype(str).str.contains
                (value, case=False, na=False)
            ]

            if result.empty:
                info_output("No matching results.")
            else:
                info_output(result.to_string())
        except ValueError:
            error_output("Incorrect format. Use 'query <column=value>'.")

    def do_generate(self, output_file):
        """
        Create and export a summary report based on stock data.
        Usage: generate <output_file_path>
        """
        if self.data.empty:
            error_output("No data available. Please add data first.")
            return

        necessary_columns = ['category', 'quantity', 'unit_price']
        if not all(col in self.data.columns for col in necessary_columns):
            error_output("Missing required columns for generating a report.")
            return

        summary = self.data.groupby('category').agg({
            'quantity': 'sum',
            'unit_price': 'mean'
        }).rename(columns={
            'quantity': 'Total Quantity', 'unit_price': 'Average Price'})

        info_output(summary.to_string())
        output_file = output_file.strip() or "summary_report.csv"
        summary.to_csv(output_file)
        success_output(f"Report saved to {output_file}.")

    def do_show_top(self, count):
        """
        Display the first N records from the stock data.
        Usage: show_top <number_of_records>
        """
        if self.data.empty:
            error_output("No data available. Please add data first.")
            return

        try:
            count = int(count) if count else 5  # Remplacer count.strip() par juste int(count)
            info_output(self.data.head(count).to_string())
        except ValueError:
            error_output("Please specify a valid number of records.")


def main():
    """Main function that parses command-line arguments."""

    parser = argparse.ArgumentParser(description="Stock Manager CLI")
    parser.add_argument(
        "--add_data",
        help="Import data from CSV files in a folder."
    )
    parser.add_argument(
        "--query",
        help="Search stock items based on column=value."
    )
    parser.add_argument(
        "--generate",
        help="Generate a summary report and save it."
    )
    parser.add_argument(
        "--show_top",
        type=int,
        help="Show the first N records of the stock data."
    )

    args = parser.parse_args()
    manager = StockManager()

    if args.add_data:
        manager.do_add_data(args.add_data)
    if args.query:
        manager.do_query(args.query)
    if args.generate:
        manager.do_generate(args.generate)
    if args.show_top is not None:
        manager.do_show_top(str(args.show_top))

    if not any(vars(args).values()):
        manager.cmdloop()


if __name__ == "__main__":
    main()
