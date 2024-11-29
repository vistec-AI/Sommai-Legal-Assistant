// "use server"

// import { cookies } from 'next/headers'

import { redirect } from 'next/navigation';
import { ResponseError } from "@/app/types";
import { HTTP_401_UNAUTHORIZED, HTTP_RESPONSE_CODE } from "@/app/constants/httpResponse";
import { getTokens, TOKEN, SECURE_OPTION, setUserTokens } from '../auth';

const BACKEND_URL = process.env["NEXT_PUBLIC_BACKEND_API"];
const isServer = typeof window === 'undefined';

// define the main function for making authenticated requests
export async function fetchWithAuth(
  path: string,
  options?: any,
  headers?: any
) {
  let token = null
  if (isServer) {
    const { cookies } = await import('next/headers');
    try {
      const tokenCookies = cookies().get(TOKEN)?.value
      token = tokenCookies ? JSON.parse(tokenCookies) : null
    } catch (e) { }
  } else {
    token = getTokens()
  }
  if (token) {
    const accessToken = token?.['access_token']
    const refreshToken = token?.['refresh_token']

    return makeFetch(path, options, headers, accessToken, refreshToken);
  }
  redirect("/auth/login")
}

// Function to create a fetch function with the specified credentials
async function makeFetch(
  path: string,
  options: any | undefined = {},
  headers: any | undefined,
  accessToken?: string,
  refreshToken?: string
) {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      ...headers
    },
    ...options
  });

  if (!response.ok) {
    const errorData = await response?.json();
    if (errorData.detail.code === HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED].TOKEN_EXPIRED && refreshToken) {

      const refreshResponse = await fetch(
        `${BACKEND_URL}/auth/refresh`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        }
      );
      if (!refreshResponse.ok) {
        redirect("/auth/login")
      }
      const refreshData = await refreshResponse?.json()
      if (isServer) {
        const { cookies } = await import('next/headers');
        const expireDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        try {
          cookies().set(TOKEN, JSON.stringify(refreshData), { path: '/', expires: expireDate, ...SECURE_OPTION })
        } catch (e) { }
      } else {
        setUserTokens(refreshData)
      }
      return makeFetch(path, options, headers, refreshData['access_token'], refreshData['refresh_token'])
    }
    throw new ResponseError("Failed to fetch data", {
      status: response.status,
      code: errorData?.detail?.code,
      description: errorData?.detail?.description
    });
  }
  return response;

}