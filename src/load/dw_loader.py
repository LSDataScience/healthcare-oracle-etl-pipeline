import os
import logging
from pathlib import Path
import duckdb
import pandas as pd

logger = logging.getLogger(__name__)


class WarehouseLoader:
    """Persiste o modelo dimensional em DuckDB e exporta camada Gold em Parquet."""

    def __init__(
        self,
        dw_path: str = os.getenv("DW_PATH", "data/warehouse/hospital_dw.duckdb"),
        parquet_dir: str = os.getenv("PARQUET_DIR", "data/gold"),
    ) -> None:
        self.dw_path = Path(dw_path)
        self.parquet_dir = Path(parquet_dir)
        self.dw_path.parent.mkdir(parents=True, exist_ok=True)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)

    def load(
        self,
        fato_atendimentos: pd.DataFrame,
        dim_unidade: pd.DataFrame,
        dim_especialidade: pd.DataFrame,
    ) -> None:
        logger.info("Carregando tabelas no Data Warehouse local (%s)...", self.dw_path)
        dim_unidade.columns = [c.lower() for c in dim_unidade.columns]
        dim_especialidade.columns = [c.lower() for c in dim_especialidade.columns]

        with duckdb.connect(str(self.dw_path)) as con:
            con.execute("CREATE OR REPLACE TABLE dim_unidade AS SELECT * FROM dim_unidade")
            con.execute("CREATE OR REPLACE TABLE dim_especialidade AS SELECT * FROM dim_especialidade")
            con.execute("CREATE OR REPLACE TABLE fato_atendimentos AS SELECT * FROM fato_atendimentos")

        fato_atendimentos.to_parquet(self.parquet_dir / "fato_atendimentos.parquet", index=False)
        dim_unidade.to_parquet(self.parquet_dir / "dim_unidade.parquet", index=False)
        dim_especialidade.to_parquet(self.parquet_dir / "dim_especialidade.parquet", index=False)
        logger.info("Carga DW e arquivos Parquet finalizada com sucesso.")