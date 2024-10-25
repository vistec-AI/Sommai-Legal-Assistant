import clsx from "clsx";

const LoadingThreeDots = () => {
  return (
    <div className={clsx("flex items-center gap-2 loading-three-dots")}>
      <div className="rounded-full w-2 h-2 bg-[#E90818] animate-scale animation-delay-[200ms]"></div>
      <div className="rounded-full w-2 h-2 bg-[#FFB2A1] animate-scale animation-delay-[400ms]"></div>
      <div className="rounded-full w-2 h-2 bg-[#7B61FF] animate-scale animation-delay-[600ms]"></div>
    </div>
  );
};

export default LoadingThreeDots;
