import polars
from os import remove
from pathlib import Path


def main():
    '''
    Reads in and clean the data.
    Deletes intermediary files.
    '''
    if not Path('blackjack.parquet').exists():
        csv_to_parquet()
    
    clean_data()
    remove('blackjack.parquet')
    remove('blackjack_simulator.csv')


def csv_to_parquet():
    '''
    Funnels a sampling of rows with a shoe ID less than 50,000 directly to a Parquet file for easier storage. 
    '''
    overrides = {
        'shoe_id': polars.Int32, 
        'cards_remaining': polars.Int16, 
        'dealer_up': polars.Int16, 
        'run_count': polars.Int16, 
        'true_count': polars.Int16, 
        'win': polars.Float32
        }
        
    (polars
        .read_csv('blackjack_simulator.csv', schema_overrides=overrides)
        .filter(polars.col('shoe_id') < 50000)
        .write_parquet('blackjack.parquet'))


def clean_data():
    '''
    Applies various data cleaning methods to further increase usability of the dataset.
    Writes to a TSV file.
    '''
    (polars
        .read_parquet('blackjack.parquet')
        .with_columns([
            polars.col(['actions_taken', 'player_final'])
                .str.head(-1)   # Remove last character
                .str.slice(1),   # Remove first character
            polars.col('dealer_final_value')
                .replace('BJ', 21)
                .cast(polars.Int16),
            polars.col('player_final_value')
                .str.head(-1)
                .str.slice(1)
                .replace('BJ', 21)
                .cast(polars.Int16, strict=False)])
        .drop_nulls()
        .write_csv('processed_blackjack.tsv', separator='\t'))


if __name__ == '__main__':
    main()
