class LlamaServicePort:
    def retrieve_documents(self, request):
        raise NotImplementedError

    def generate_response(self, request):
        raise NotImplementedError