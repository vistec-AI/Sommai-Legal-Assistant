import { fetchWithAuth } from "@/app/utils/services/fetchWithCredential"


const chatRooms = {
  getAllChatRooms: (options: any = {}) => {
    return fetchWithAuth(`/chat-rooms/`, { cache: 'no-store', next: { tags: ['chatRooms'] }, ...options })
  },
  getLatestChatRooms: (options: any = {}) => {
    return fetchWithAuth(`/chat-rooms/latest`, { cache: 'no-store', next: { tags: ['latestChatRooms'] }, ...options })
  },
  geChatRoomsByID: (chatRoomID: string, options: any = {}) => {
    return fetchWithAuth(`/chat-rooms/${chatRoomID}`, { cache: 'no-store', next: { tags: [`chatRooms-${chatRoomID}`] }, ...options })
  },
  createChatRoom: (name: string, options: any = {}) => {
    return fetchWithAuth(`/chat-rooms/`, { method: 'POST', body: JSON.stringify({ name: name }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  },
  renameChatRoom: (id: string, name: string, options: any = {}) => {
    return fetchWithAuth(`/chat-rooms/${id}`, { method: 'PUT', body: JSON.stringify({ name: name }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  },
  deleteChatRoom: (id: string, options: any = {}) => {
    return fetchWithAuth(`/chat-rooms/${id}`, { method: 'DELETE', cache: 'no-store', ...options })
  }
}

export default chatRooms