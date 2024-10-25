import { Rating } from "@/app/types"
import { fetchWithAuth } from "@/app/utils/services/fetchWithCredential"

const arenaModelResponse = {
  getArenaModelResponse: (arenaID: string, options: any = {}) => {
    return fetchWithAuth(`/arena-model-responses?arena_id=${arenaID}`, { cache: 'no-store', next: { tags: [arenaID] }, ...options })
  },
  likeArenaModelResponse: (arenaModelResponseID: string, options: any = {}) => {
    return fetchWithAuth(`/arena-model-responses/${arenaModelResponseID}`, { method: 'PUT', body: JSON.stringify({ rating: Rating.LIKE }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  },
  dislikeArenaModelResponse: (arenaModelResponseID: string, options: any = {}) => {
    return fetchWithAuth(`/arena-model-responses/${arenaModelResponseID}`, { method: 'PUT', body: JSON.stringify({ rating: Rating.DISLIKE }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  },
  askQuestionByInferenceModelID: (body: { question: string, inference_model_id: string, arena_id: string, alias: string }, options: any = {}) => {
    return fetchWithAuth(`/arena-model-responses/question`, { method: 'POST', body: JSON.stringify(body), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  }
}

export default arenaModelResponse