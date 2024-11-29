const BACKEND_URL = process.env["NEXT_PUBLIC_BACKEND_API"];
import { ResponseError } from "@/app/types";

export default async function fetchWithoutAuth(
  path: string,
  options?: any,
  headers?: any
) {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    headers: {
      ...headers
    },
    ...options,
  });
  if (!response.ok) {
    let errorData: any = {}
    try {
      errorData = await response.json();
    } catch (error) {
      errorData = { detail: { code: 'UNKNOWN_ERROR', description: 'An unknown error occurred.' } };
    }
    throw new ResponseError("Failed to fetch data", {
      status: response.status,
      code: errorData?.detail?.code,
      description: errorData?.detail?.description
    });
  }
  return response;
}
