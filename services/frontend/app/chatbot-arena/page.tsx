import api from "@/api";
import { ResponseError, InferenceModelType } from "@/app/types";

import ChatbotArenaSection from "../components/chatArena/ChatbotArenaSection";

const fetchInferenceModelData = async () => {
  try {
    const res = await api.inferenceModels.getAllInferenceModels();
    return res.json();
  } catch (err) {
    if (err instanceof ResponseError) {
    }
  }
};

export default async function ChatbotArenaPage() {
  const inferenceModelList = await fetchInferenceModelData();
  const availableInferenceModelList = inferenceModelList?.filter(
    (inferenceModel: InferenceModelType) => inferenceModel.available
  );

  return (
    <main className="flex flex-col grow overflow-hidden">
      <ChatbotArenaSection
        inferenceModelList={availableInferenceModelList}
        allInferenceModelList={inferenceModelList}
      />
    </main>
  );
}
