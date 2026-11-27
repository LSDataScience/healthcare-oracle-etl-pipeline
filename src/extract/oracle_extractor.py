import os
import logging
from dataclasses import dataclass
import oracledb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OracleConfig:
    user: str = os.getenv("ORACLE_USER", "HOSP_LAB")
    password: str = os.getenv("ORACLE_PASSWORD", "HospLab2026")
    dsn: str = os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1")


class OracleHospitalExtractor:
    """Extrai dados transacionais simulados do ERP hospitalar Oracle."""

    def __init__(self, config: OracleConfig | None = None) -> None:
        self.config = config or OracleConfig()

    def _get_connection(self) -> oracledb.Connection:
        return oracledb.connect(
            user=self.config.user,
            password=self.config.password,
            dsn=self.config.dsn,
        )

    @staticmethod
    def _query_to_df(conn: oracledb.Connection, sql: str, params: dict | None = None) -> pd.DataFrame:
        with conn.cursor() as cursor:
            cursor.arraysize = 10000
            cursor.execute(sql, params or {})
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)

    def extract_dimensions(self) -> dict[str, pd.DataFrame]:
        logger.info("Extraindo dimensões (Unidades e Especialidades) do Oracle...")
        with self._get_connection() as conn:
            df_unidade = self._query_to_df(conn, "SELECT * FROM TB_UNIDADE")
            df_especialidade = self._query_to_df(conn, "SELECT * FROM TB_ESPECIALIDADE")
        return {
            "dim_unidade": df_unidade,
            "dim_especialidade": df_especialidade,
        }

    def extract_atendimentos(self, months_back: int = 12) -> pd.DataFrame:
        logger.info("Extraindo atendimentos dos últimos %s meses...", months_back)
        query = """
            SELECT
                CD_ATENDIMENTO,
                CD_PACIENTE_HASH,
                CD_UNIDADE,
                CD_ESPECIALIDADE,
                TP_ATENDIMENTO,
                CD_CONVENIO,
                DT_ATENDIMENTO,
                DT_ALTA,
                TP_ALTA,
                VL_TOTAL_CONTA,
                STATUS_CONTA
            FROM TB_ATENDIMENTO
            WHERE DT_ATENDIMENTO >= ADD_MONTHS(TRUNC(SYSDATE), -:months_back)
        """
        with self._get_connection() as conn:
            df = self._query_to_df(conn, query, params={"months_back": months_back})
        logger.info("Total de registros extraídos: %s", len(df))
        return df