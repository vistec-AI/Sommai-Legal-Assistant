import { fetchWithAuth } from "@/app/utils/services/fetchWithCredential"
import { Rating } from "@/app/types"

const chats = {
  getChatsByChatRoomID: (chatRoomID: string, options: any = {}) => {
    return fetchWithAuth(`/chats?chat_room_id=${chatRoomID}`, { cache: 'no-store', next: { tags: [chatRoomID] }, ...options })
  },
  askQuestion: (question: string, chatRoomID: string, inferenceModelID: string, options: any = {}) => {
    return fetchWithAuth(`/chats/`, { method: 'POST', body: JSON.stringify({ question: question, chat_room_id: chatRoomID, inference_model_id: inferenceModelID }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  },
  retrieveLawRef: (question: string, chatID: string, inferenceModelID: string, options: any = {}) => {
    return fetchWithAuth(`/chats/retrieval`, { method: 'POST', body: JSON.stringify({ question: question, chat_id: chatID, inference_model_id: inferenceModelID }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  },
  likeChat: (chatID: string, options: any = {}) => {
    return fetchWithAuth(`/chats/${chatID}`, { method: 'PUT', body: JSON.stringify({ rating: Rating.LIKE, feedback: "" }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  },
  dislikeChat: (chatID: string, feedback: string, options: any = {}) => {
    return fetchWithAuth(`/chats/${chatID}`, { method: 'PUT', body: JSON.stringify({ rating: Rating.DISLIKE, feedback: feedback }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  }
}

export default chats