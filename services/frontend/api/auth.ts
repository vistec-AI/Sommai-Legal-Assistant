import { fetchWithAuth } from "@/app/utils/services/fetchWithCredential";
import fetchWithoutAuth from "@/app/utils/services/fetchWithoutAuth";
import { TOKEN } from "@/app/utils/auth";

const auth = {
  login: (body: { email: string, password: string }, options: any = {}) => {
    return fetchWithoutAuth(`/auth/login`, { method: 'POST', body: JSON.stringify(body), ...options }, { 'Content-Type': 'application/json' })
  },
  register: (body: { email: string, password: string }, options: any = {}) => {
    return fetchWithoutAuth(`/auth/register`, { method: 'POST', body: JSON.stringify(body), ...options }, { 'Content-Type': 'application/json' })
  },
  refresh: (body: { refresh_token: string }, options: any = {}) => {
    return fetchWithoutAuth(`/auth/refresh`, { method: 'POST', body: JSON.stringify(body), ...options }, { 'Content-Type': 'application/json' })
  },
  logout: (body: { refresh_token: string }, options: any = {}) => {
    return fetchWithoutAuth(`/auth/logout`, { method: 'POST', body: JSON.stringify(body), ...options }, { 'Content-Type': 'application/json' })
  },
  resetPassword: (body: { email: string, token: string, new_password: string }, options: any = {}) => {
    return fetchWithoutAuth(`/auth/reset-password`, { method: 'POST', body: JSON.stringify(body), ...options }, { 'Content-Type': 'application/json' })
  },
  getUserEmail: (options: any = {}) => {
    return fetchWithAuth(`/auth/user/email`, { ...options })
  },
  isUserAcceptedTerms: (email: string, options: any = {}) => {
    return fetchWithoutAuth(`/auth/user/is-accepted-terms?email=${email}`, { ...options })
  },
  acceptTerms: (email: string, options: any = {}) => {
    return fetchWithoutAuth(`/auth/user/accept-terms`, { method: 'POST', body: JSON.stringify({ email }), ...options }, { 'Content-Type': 'application/json' })
  },
}

export default auth