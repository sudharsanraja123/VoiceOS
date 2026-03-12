from llama_cpp import Llama


class StreamingLLM:

    def __init__(self):

        self.llm = Llama(
            model_path="models/mistral.gguf",
            n_ctx=4096
        )

    def stream_response(self, prompt):

        stream = self.llm(
            prompt,
            stream=True
        )

        for token in stream:

            if "choices" in token:

                text = token["choices"][0]["text"]

                yield text