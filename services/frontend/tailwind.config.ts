import type { Config } from "tailwindcss";
const plugin = require('tailwindcss/plugin')

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ["var(--font-inter)"],
        sukhumvit: ["var(--font-sukhumvit)"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "gradient-primary": "linear-gradient(90deg, #7873F5 0%, #E9465A 100%)",
        "gradient-primary-dark": "linear-gradient(0deg, rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.2)), linear-gradient(90deg, #7873F5 0%, #E9465A 100%)"
      },
      colors: {
        default: "#212529",
        gray: {
          25: "#FCFCFD",
          50: "#F9FAFB",
          100: "#F2F4F7",
          200: "#EAECF0",
          300: "#D0D5DD",
          400: "#98A2B3",
          500: "#667085",
          600: "#475467",
          700: "#344054",
          800: "#182230",
          900: "#101828",
          950: "#0C111D",
        },
        primary: {
          25: "#FCFAFF",
          50: "#F9F5FF",
          100: "#D9D0ED",
          200: "#B2A1DB",
          300: "#8C71CA",
          400: "#795AC1",
          500: "#522BAF",
          600: "#3F13A6",
          700: "#320F85",
          800: "#260B64",
          900: "#190842",
          950: "#130632",
          shadow: "#9E77ED3D"
        },
        error: {
          25: "#FFFBFA",
          50: "#FEF3F2",
          100: "#FEE4E2",
          200: "#FECDCA",
          300: "#FDA29B",
          400: "#F97066",
          500: "#F04438",
          600: "#D92D20",
          700: "#B42318",
          800: "#912018",
          900: "#7A271A",
          950: "#55160C",
          shadow: "#F044383D"
        },
        success: {
          25: "#F6FEF9",
          50: "#ECFDF3",
          100: "#DCFAE6",
          200: "#ABEFC6",
          300: "#75E0A7",
          400: "#47CD89",
          500: "#17B26A",
          600: "#079455",
          700: "#067647",
          800: "#085D3A",
          900: "#074D31",
          950: "#053321",
        },
        blue: {
          25: "#F5FAFF",
          50: "#EFF8FF",
          100: "#D1E9FF",
          200: "#B2DDFF",
          300: "#84CAFF",
          400: "#53B1FD",
          500: "#2E90FA",
          600: "#1570EF",
          700: "#175CD3",
          800: "#1849A9",
          900: "#194185",
          950: "#102A56",
        },
        warning: {
          25: "#FFFCF5",
          50: "#FFFAEB",
          100: "#FEF0C7",
          200: "#FEDF89",
          300: "#FEC84B",
          400: "#FDB022",
          500: "#F79009",
          600: "#DC6803",
          700: "#B54708",
          800: "#93370D",
          900: "#7A2E0E",
        },
      },
      animation: {
        'text-slide': 'text-slide 7.5s cubic-bezier(0.83, 0, 0.17, 1) infinite',
        'slide-from-bottom': 'from-bottom 0.5s ease-out',
        'slide-from-top': 'from-top 0.3s ease-out',
        'slide-from-left': 'from-left 0.4s ease-out',
        'scale': 'element-scale 1.2s ease-in-out infinite',
        'text-fill': 'text-fill 2s linear',
        'fade-in': 'fade-in 0.3s ease-in'
      },
      keyframes: {
        'text-slide': {
          '0%, 26.66%': {
            transform: 'translateY(0%)',
          },
          '33.33%, 60%': {
            transform: 'translateY(-25%)',
          },
          '66.66%, 93.33%': {
            transform: 'translateY(-50%)',
          },
          '100%': {
            transform: 'translateY(-75%)',
          },
        },
        'text-fill': {
          '0%': { backgroundSize: "0% 100%" },
          '100%': { backgroundSize: '100% 100%' },
        },
        'from-bottom': {
          '0%': { transform: 'translateY(100%)', opacity: "0" },
          '100%': { transform: 'translateY(0)', opacity: "1" },
        },
        'from-left': {
          '0%': { transform: 'translateX(-100%)', opacity: "0" },
          '100%': { transform: 'translateX(0)', opacity: "1" },
        },
        'from-top': {
          '0%': { transform: 'translateY(0)', opacity: "0" },
          '80%': { transform: 'translateY(106%)', opacity: "1" },
          '100%': { transform: 'translateY(100%)', opacity: "1" },
        },
        'element-scale': {
          '0%': { scale: '1', opacity: "1" },
          '50%': { scale: '1.3', opacity: "1" },
          '70%': { scale: '1', opacity: "0.6" },
          '100%': { opacity: "0.6" },
        },
        'fade-in': {
          '0%': { opacity: "0" },
          // '50%': { scale: '1.3', opacity: "1" },
          // '70%': { scale: '1', opacity: "0.6" },
          '100%': { opacity: "1" },
        }
      },
    },
  },
  plugins: [
    plugin(({ matchUtilities, theme }: any) => {
      matchUtilities(
        {
          "animation-delay": (value: any) => {
            return {
              "animation-delay": value,
            };
          },
        },
        {
          values: theme("transitionDelay"),
        }
      );
    }),
  ],
};
export default config;
