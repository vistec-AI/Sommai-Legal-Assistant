"use server";

import { revalidateTag } from "next/cache";
import { cookies } from "next/headers";

export async function revalidate(tag: string) {
  revalidateTag(tag);
}

export async function actionSetCookie(key: string, value: string) {
  cookies().set(key, value, {
    path: "/",
    expires: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
  });
}
