import logging
from src.extract.oracle_extractor import OracleHospitalExtractor
from src.transform.star_schema_transformer import HealthcareTransformer
from src.load.dw_loader import WarehouseLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def run_etl() -> None:
    extractor = OracleHospitalExtractor()
    transformer = HealthcareTransformer()
    loader = WarehouseLoader()

    dims = extractor.extract_dimensions()
    raw_atendimentos = extractor.extract_atendimentos(months_back=12)
    fato_atendimentos = transformer.transform_atendimentos(raw_atendimentos)

    loader.load(
        fato_atendimentos=fato_atendimentos,
        dim_unidade=dims["dim_unidade"],
        dim_especialidade=dims["dim_especialidade"],
    )


if __name__ == "__main__":
    run_etl()