import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class HealthcareTransformer:
    """Aplica regras de Data Quality e modela Star Schema hospitalar."""

    TIPO_ATENDIMENTO_MAP = {
        "I": "Internação",
        "U": "Urgência / Emergência",
        "A": "Ambulatório",
    }

    def transform_atendimentos(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Iniciando transformação e validação de qualidade (Data Quality)...")
        data = df.copy()
        data.columns = [c.lower() for c in data.columns]

        # 1. Garante tipagem de datas
        data["dt_atendimento"] = pd.to_datetime(data["dt_atendimento"])
        data["dt_alta"] = pd.to_datetime(data["dt_alta"])

        # 2. Regra de Data Quality: remove datas de alta inconsistentes (< atendimento)
        inconsistentes = (data["dt_alta"].notna()) & (data["dt_alta"] < data["dt_atendimento"])
        if inconsistentes.any():
            logger.warning("Descartando %s registros com DT_ALTA < DT_ATENDIMENTO", inconsistentes.sum())
            data = data.loc[~inconsistentes].copy()

        # 3. Enriquecimento de regras de negócio hospitalar
        data["ds_tipo_atendimento"] = data["tp_atendimento"].map(self.TIPO_ATENDIMENTO_MAP).fillna("Outros")
        data["fonte_pagadora"] = np.where(data["cd_convenio"] == 1, "SUS", "Saúde Suplementar / Convênios")
        data["sn_internado_ativo"] = np.where(data["dt_alta"].isna(), "S", "N")

        # Tempo de permanência em dias (para altas concluídas)
        data["dias_permanencia"] = np.where(
            data["dt_alta"].notna(),
            (data["dt_alta"] - data["dt_atendimento"]).dt.total_seconds() / 86400.0,
            np.nan,
        ).round(2)

        # Chaves temporais para análise dimensional
        data["ano_mes"] = data["dt_atendimento"].dt.to_period("M").astype(str)
        data["dt_referencia"] = data["dt_atendimento"].dt.date

        logger.info("Transformação concluída com %s registros válidos.", len(data))
        return data