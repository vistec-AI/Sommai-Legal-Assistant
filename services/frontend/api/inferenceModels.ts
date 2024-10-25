import { fetchWithAuth } from "@/app/utils/services/fetchWithCredential"

const inferenceModels = {
  getAllInferenceModels: (options: any = {}) => {
    return fetchWithAuth(`/inference-models/`, { next: { tags: ['inferenceModels'] }, ...options })
  }
}

export default inferenceModels