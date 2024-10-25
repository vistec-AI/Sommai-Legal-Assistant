import { fetchWithAuth } from "@/app/utils/services/fetchWithCredential"

const arena = {
  getArenaList: (options: any = {}) => {
    return fetchWithAuth(`/arena/`, { cache: 'no-store', next: { tags: ["arena"] }, ...options })
  },
  createArena: (question: string, options: any = {}) => {
    return fetchWithAuth(`/arena/`, { method: 'POST', body: JSON.stringify({ question: question }), cache: 'no-store', ...options }, { 'Content-Type': 'application/json' })
  },
}

export default arena