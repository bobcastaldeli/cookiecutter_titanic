from modelo_titanic.data.make_dataset import make_dataset
from modelo_titanic.features.build_features import build_features
from modelo_titanic.models.evaluate import evaluate_model
from modelo_titanic.models.train import train_model


def run_pipeline() -> None:
    print("Etapa 1/4 - Processando dataset")
    make_dataset()

    print("Etapa 2/4 - Construindo features")
    build_features()

    print("Etapa 3/4 - Treinando modelo")
    train_model()

    print("Etapa 4/4 - Avaliando modelo")
    evaluate_model()

    print("Pipeline finalizado com sucesso.")


if __name__ == "__main__":
    run_pipeline()