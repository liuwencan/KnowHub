from dataclasses import dataclass

from konwhub.domain.ports import ChatModelPort, EmbeddingPort, RerankerPort


@dataclass
class FakeChatModel(ChatModelPort):
    response: str = ""

    def complete(self, prompt: str) -> str:
        return self.response


@dataclass
class FakeEmbeddings(EmbeddingPort):
    dimensions: int = 3

    def embed(self, text: str) -> list[float]:
        return [0.0] * self.dimensions


class IdentityReranker(RerankerPort):
    def rerank(self, query: str, documents):
        return list(documents)
