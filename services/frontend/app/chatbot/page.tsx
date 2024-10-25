import { ResponseError, InferenceModelType } from "@/app/types";

import ChatLayout from "../components/chatbot/ChatLayout";

import api from "@/api";

const fetchInferenceModelData = async () => {
  try {
    const res = await api.inferenceModels.getAllInferenceModels();
    return res.json();
  } catch (err) {
    if (err instanceof ResponseError) {
    }
  }
};

export default async function ChatbotPage() {
  const inferenceModelList = await fetchInferenceModelData();
  const availableInferenceModels = inferenceModelList?.filter(
    (inferenceModel: InferenceModelType) => inferenceModel.available
  );

  return (
    <main className="flex grow overflow-hidden">
      <ChatLayout inferenceModelList={availableInferenceModels} />
    </main>
  );
}
