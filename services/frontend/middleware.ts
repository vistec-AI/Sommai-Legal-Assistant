import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { TOKEN, USER } from './app/utils/auth';
import { AUTH_PATH_PREFIX, APP_PATH } from './app/constants';
import { HTTP_RESPONSE_CODE, HTTP_401_UNAUTHORIZED } from './app/constants/httpResponse';

const BACKEND_URL = process.env["NEXT_PUBLIC_BACKEND_API"];

export async function middleware(request: NextRequest) {
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-pathname", request.nextUrl.pathname);

  const redirectToLoginPage = (query?: string) => {
    const response = NextResponse.redirect(new URL(`/auth/login${query ? `?${query}` : ""}`, request.url))
    response.cookies.delete(TOKEN);
    response.cookies.delete(USER);
    return response
  }
  const pathRequiredAuth = APP_PATH.includes(request.nextUrl.pathname)
  const errorQuery = "authError=true"
  const expireDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)

  if (pathRequiredAuth) {
    const token = request.cookies.get(TOKEN)
    const tokenValue = token?.value

    if (tokenValue) {
      try {
        const tokenJson = JSON.parse(tokenValue);
        const accessToken = tokenJson?.["access_token"]
        const refreshToken = tokenJson?.["refresh_token"]
        let response = NextResponse.next({
          request: {
            headers: requestHeaders,
          },
        });
        let responseRedirect = NextResponse.redirect(new URL('/chatbot', request.url))
        if (!accessToken || !refreshToken) {
          return redirectToLoginPage()
        } else {
          try {
            // Get user email
            const getEmailResponse = await fetch(
              `${BACKEND_URL}/auth/user/email`,
              {
                method: "GET",
                headers: {
                  Authorization: `Bearer ${accessToken}`,
                },

              }
            );

            // Email error
            if (!getEmailResponse.ok) {
              const errorData = await getEmailResponse?.json();

              // In case token expired
              if (errorData?.detail?.code === "token_expired") {

                try {
                  // Refresh new token
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
                    return redirectToLoginPage();
                  }
                  const refreshData = await refreshResponse?.json()

                  if (refreshData?.access_token) {
                    // Set new token
                    response.cookies.set({ name: TOKEN, value: JSON.stringify(refreshData), path: '/', expires: expireDate })
                    responseRedirect.cookies.set({ name: TOKEN, value: JSON.stringify(refreshData), path: '/', expires: expireDate })
                    // Get user email
                    const getEmailResponseFromRefresh = await fetch(
                      `${BACKEND_URL}/auth/user/email`,
                      {
                        method: "GET",
                        headers: {
                          Authorization: `Bearer ${refreshData?.access_token}`,
                        },

                      }
                    );
                    if (getEmailResponseFromRefresh.ok) {
                      const emailDataFromRefresh = await getEmailResponseFromRefresh?.json()
                      // Set user email
                      response.cookies.set({ name: USER, value: JSON.stringify(emailDataFromRefresh), path: '/', expires: expireDate })
                      responseRedirect.cookies.set({ name: USER, value: JSON.stringify(emailDataFromRefresh), path: '/', expires: expireDate })
                    } else {
                      return redirectToLoginPage()
                    }
                    if (request.nextUrl.pathname === "/") {
                      return responseRedirect
                    }
                    return response

                  } else {
                    return redirectToLoginPage()
                  }

                } catch (e) {
                  return redirectToLoginPage()
                }
              } else {
                if (errorData?.detail?.code === HTTP_RESPONSE_CODE[HTTP_401_UNAUTHORIZED].EMAIL_NOT_EXISTS) {
                  return redirectToLoginPage(errorQuery);
                }
                return redirectToLoginPage();
              }

            }

            const emailResponse = await getEmailResponse.json()

            response.cookies.set({ name: USER, value: JSON.stringify(emailResponse), path: '/', expires: expireDate })
            responseRedirect.cookies.set({ name: USER, value: JSON.stringify(emailResponse), path: '/', expires: expireDate })
            if (request.nextUrl.pathname === "/") {
              return NextResponse.redirect(new URL('/chatbot', request.url))
            }
            if (request.nextUrl.pathname === "/") {
              return responseRedirect
            }

            return response

          } catch (e) {
            return redirectToLoginPage();
          }
        }
      } catch (e) {
        return redirectToLoginPage()
      }
    } else {
      return redirectToLoginPage()
    }
  }


  if (request.nextUrl.pathname === "/") {
    return NextResponse.redirect(new URL('/chatbot', request.url))
  }


  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

// only applies this middleware to files in the app directory
export const config = {
  matcher: "/((?!api|images|ws|static|.*\\..*|_next).*)",
};
