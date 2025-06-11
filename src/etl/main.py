from colorama import Fore
from src.etl.extract import extract
from src.etl.transform import transform
from src.etl.load import init_db, load_dim_time, load_fact

def run_etl():
    print(Fore.CYAN, '* INIT Extraccion', Fore.RESET)
    raw_df = extract()
    print(Fore.GREEN, '* END  Extraccion', Fore.RESET)

    print(Fore.CYAN, '* INIT Transformacion', Fore.RESET)
    dim_df, fact_df = transform(raw_df)
    print(Fore.GREEN, '* END  Transformacion', Fore.RESET)

    print(Fore.CYAN, '* INIT Carga', Fore.RESET)
    init_db()
    load_dim_time(dim_df)
    load_fact(fact_df)
    print(Fore.GREEN, '* END  Carga', Fore.RESET)


if __name__ == '__main__':
    run_etl()
