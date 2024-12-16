import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from io import StringIO

from main import StockManager


class TestStockManager(unittest.TestCase):

    @patch('pandas.read_csv')
    def test_add_data_success(self, mock_read_csv):
        """Test si les fichiers CSV sont correctement chargés."""

        mock_data = pd.DataFrame({
            'category': ['A', 'B', 'A'],
            'quantity': [10, 20, 30],
            'unit_price': [5.0, 10.0, 15.0]
        })
        mock_read_csv.return_value = mock_data

        manager = StockManager()
        manager.data = pd.DataFrame()
        directory = 'fake_directory'


        with patch('os.listdir', return_value=['file1.csv', 'file2.csv']), patch('os.path.isdir', return_value=True):
            manager.do_add_data(directory)


        self.assertFalse(manager.data.empty)
        self.assertEqual(manager.data.shape[0], 6)

    @patch('pandas.read_csv')
    def test_add_data_no_csv(self, mock_read_csv):
        """Test si la fonction renvoie une erreur quand il n'y a pas de fichiers CSV."""
        mock_read_csv.return_value = pd.DataFrame()

        manager = StockManager()
        manager.data = pd.DataFrame()
        directory = 'empty_directory'


        with patch('os.listdir', return_value=[]), patch('os.path.isdir', return_value=True):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                manager.do_add_data(directory)
                output = mock_stdout.getvalue()
                self.assertIn("No CSV files found.", output)

    def test_query(self):
        """Test de la fonctionnalité de recherche dans les données."""
        manager = StockManager()
        manager.data = pd.DataFrame({
            'category': ['A', 'B', 'A'],
            'quantity': [10, 20, 30],
            'unit_price': [5.0, 10.0, 15.0]
        })


        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            manager.do_query('category=A')
            output = mock_stdout.getvalue()
            self.assertIn('A', output)


        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            manager.do_query('category=Z')
            output = mock_stdout.getvalue()
            self.assertIn('No matching results.', output)

    def test_generate_report(self):
        """Test de la génération d'un rapport."""
        manager = StockManager()
        manager.data = pd.DataFrame({
            'category': ['A', 'B', 'A'],
            'quantity': [10, 20, 30],
            'unit_price': [5.0, 10.0, 15.0]
        })

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            manager.do_generate('test_report.csv')
            output = mock_stdout.getvalue()
            self.assertIn('Report saved to test_report.csv',
                          output)
            self.assertTrue(os.path.exists('test_report.csv'))

    def test_show_top(self):
        """Test de la commande pour afficher les premières lignes de données."""
        manager = StockManager()
        manager.data = pd.DataFrame({
            'category': ['A', 'B', 'A'],
            'quantity': [10, 20, 30],
            'unit_price': [5.0, 10.0, 15.0]
        })

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            manager.do_show_top(2)
            output = mock_stdout.getvalue()
            self.assertIn('A', output) 


if __name__ == '__main__':
    unittest.main()
