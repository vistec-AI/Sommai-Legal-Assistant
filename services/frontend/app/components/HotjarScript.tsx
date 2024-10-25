"use client";

import { useEffect } from "react";

interface HotjarScriptProps {
  hjid: string | number;
}

declare global {
  interface Window {
    hj: any;
    _hjSettings: any;
  }
}

export default function HotjarScript({ hjid }: HotjarScriptProps): null {
  useEffect(() => {
    const addHotjarScript = () => {
      const script = document.createElement("script");
      script.innerHTML = `
        (function(h,o,t,j,a,r){
          h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
          h._hjSettings={hjid:${hjid},hjsv:6};
          a=o.getElementsByTagName('head')[0];
          r=o.createElement('script');r.async=1;
          r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
          a.appendChild(r);
        })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
      `;
      document.head.appendChild(script);
    };

    if (typeof window !== "undefined") {
      addHotjarScript();
    }
  }, [hjid]);

  return null;
}
