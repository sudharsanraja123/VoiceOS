from memory.vector_store import VectorStore
from memory.memory_graph import MemoryGraph
from memory.entity_extractor import EntityExtractor


class MemoryManager:

    def __init__(self):

        self.vector_store = VectorStore()

        self.graph = MemoryGraph()

        self.extractor = EntityExtractor()

    def store(self, text):

        self.vector_store.add_memory(text)

        fact = self.extractor.extract(text)

        if fact:

            self.graph.add_fact(
                fact["entity"],
                fact["relation"],
                fact["value"]
            )

    def retrieve(self, query):

        vector_results = self.vector_store.search(query)

        return vector_results