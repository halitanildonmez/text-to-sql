import duckdb
import pandas as pd

_db_instance = None

def create_db():
    con = duckdb.connect()
    con.execute("INSTALL tpch")
    con.execute("LOAD tpch")
    con.execute("CALL dbgen(sf=0.1)")
    return con

class Database:

    def __init__(self):
        global _db_instance
        if _db_instance is None:
            _db_instance = create_db()
        self.cur_con = _db_instance

    def get_all_tables(self) -> list[str]:
        return self.cur_con.execute("SHOW ALL TABLES").df()['name'].tolist()

    def run_query(self, query) -> pd.DataFrame:
        return self.cur_con.execute(query).df()

    def get_table_information(self) -> str:
        result = []
        table_names = self.get_all_tables()
        for table_name in table_names:
            cur_df = self.run_query(f"DESC {table_name}")[["column_name", "column_type"]]
            cols = ", ".join(f"{row['column_name']} ({row['column_type']})" for _, row in cur_df.iterrows())
            cur_df["table_name"] = table_name
            result.append(f"{table_name} : {cols}")
        return "\n".join(result)