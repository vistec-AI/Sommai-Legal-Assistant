import Image from "next/image";
import VISTECLogo from "@/public/images/logo/vistec.webp";

const AuthLayout = ({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) => {
  return (
    <section className="grow flex flex-col gap-12 justify-between md:p-8 p-6 transition-all">
      {children}
      {/* footer */}
      <footer className="flex flex-col justify-center items-center gap-1 text-center !font-inter">
        <Image
          src={VISTECLogo}
          alt="VISTEC logo"
          className="object-contain"
          width={68}
          height={26}
        />
        <div className="flex flex-col gap-1">
          <div className="text-gray-600 text-base font-semibold px-2">
            Vidyasirimedhi Institute of Science and Technology
          </div>
          <hr className="border-gray-300" />
        </div>
        <p className="text-gray-600 text-xs">
          Information Science and Technology Building, 3rd Floor,
          <br />
          Vidyasirimedhi Institute of Science and Technology (VISTEC) 555 Moo 1
          Payupnai, Wangchan, Rayong 21210 Thailand
        </p>
      </footer>
    </section>
  );
};

export default AuthLayout;
