"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";
import clsx from "clsx";
import { Z_INDEX, AUTH_PATH_PREFIX, APP_PATH } from "../constants";

import SommaiiLogo from "@/public/images/logo/sommaii.webp";
import MenuIcon from "@/public/icons/menu.svg";
import XCloseIcon from "@/public/icons/x-close.svg";

const Navbar = () => {
  const pathname = usePathname();
  const isAuthPath = pathname.startsWith(AUTH_PATH_PREFIX);
  const isAppPath = APP_PATH.includes(pathname);

  return (
    <>
      {/* navigation */}
      <nav
        style={{ zIndex: Z_INDEX.NAVBAR }}
        className="w-full md:h-[72px] h-[60px] bg-white sticky top-0 !font-inter shrink-0"
      >
        <div
          className={clsx(
            "relative flex items-center md:justify-start justify-between md:px-8 px-6 border-b h-full w-full gap-4",
            isAuthPath ? "border-gray-200" : "border-transparent"
          )}
        >
          <div className="md:hidden w-5"></div>
          <Link href="/" className="shrink-0">
            <Image
              src={SommaiiLogo}
              alt="Sommii logo"
              width={142}
              height={32}
              className="object-contain"
            />
          </Link>
          {!isAppPath && (
            <>
              <ul className={clsx("md:flex hidden items-center gap-1")}>
                {/* <li>
                  <NavbarMenu title="Contact Us" path="/contact-us" />
                </li> */}
              </ul>
              <MobileNavbar className={clsx("md:hidden")} />
            </>
          )}
          {!isAuthPath && <div className="md:hidden w-5"></div>}
        </div>
      </nav>
    </>
  );
};

const MobileNavbar = ({ className }: { className?: string }) => {
  const [showMobileNavbar, setShowMobileNavbar] = useState(false);
  return (
    <div
      tabIndex={0}
      className={clsx("relative", className)}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) {
          setShowMobileNavbar(false);
        }
      }}
    >
      <div className="flex items-center justify-center h-full">
        <button
          type="button"
          aria-label="menu"
          className="text-gray-700 hover:text-gray-700 tablet:hidden flex items-center justify-center w-7 rounded-lg"
          onClick={() => setShowMobileNavbar(!showMobileNavbar)}
        >
          <MenuIcon
            className={clsx(
              "stroke-current transition-all",
              !showMobileNavbar ? "w-6 h-6" : "w-0 h-0"
            )}
          />
          <XCloseIcon
            className={clsx(
              "stroke-current transition-all",
              showMobileNavbar ? "w-6 h-6" : "w-0 h-0"
            )}
          />
        </button>
      </div>
      <div
        className={clsx(
          "fixed max-h-[calc(100dvh_-_80px)] top-20 z-[200] p-3 hide-scrollbar bg-white left-0 tablet:hidden block w-full mobile:max-w-[390px] transition duration-[400ms] overflow-auto rounded-b-xl shadow-lg",
          showMobileNavbar
            ? "scale-y-100 origin-top opacity-100 ease-out"
            : "scale-y-0 h-0 invisible opacity-0 ease-in"
        )}
      >
        <div className="flex flex-col gap-2">
          <NavbarMenu title="Home" path="/" />
          {/* <NavbarMenu title="Open Source" path="/open-source" />
          <NavbarMenu title="Contact Us" path="/contact-us" /> */}
        </div>
      </div>
    </div>
  );
};

type NavbarMenuProps = {
  title: string;
  path: string;
  className?: string;
};

const NavbarMenu = ({ title, path, className }: NavbarMenuProps) => {
  const pathname: string = usePathname();

  return (
    <Link
      href={path}
      className={clsx(
        "px-3 py-2 rounded-md shrink-0 font-semibold text-base",
        className,
        pathname === path
          ? "bg-gray-50 text-gray-800"
          : "bg-white hover:bg-gray-50 text-gray-700"
      )}
    >
      {title}
    </Link>
  );
};

export default Navbar;
