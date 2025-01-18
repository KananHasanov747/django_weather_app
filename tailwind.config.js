/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      gridTemplateColumns: {
        24: "repeat(24, minmax(0, 1fr))",
      },
      colors: {
        "light-gray": "#202B3B",
        "dark-gray": "#0c131e",
        "light-white": "#d4d4d8",
        "dark-white": "#9097A0",
      },
    },
    //spacing: {
    //  "space-2xs": "clamp(9px, 8.6522px + 0.1087vw, 10px)",
    //  "space-xs": "clamp(14px, 13.6522px + 0.1087vw, 15px)",
    //  "space-s": "clamp(18px, 17.3043px + 0.2174vw, 20px)",
    //  "space-m": "clamp(27px, 25.9565px + 0.3261vw, 30px)",
    //  "space-l": "clamp(36px, 34.6087px + 0.4348vw, 40px)",
    //  "space-xl": "clamp(54px, 51.913px + 0.6522vw, 60px)",
    //  "space-2xl": "clamp(72px, 69.2174px + 0.8696vw, 80px)",
    //  "space-3xl": "clamp(108px, 103.8261px + 1.3043vw, 120px)",
    //
    //  /* One-up pairs */
    //  "space-2xs-xs": "clamp(9px, 6.913px + 0.6522vw, 15px)",
    //  "space-xs-s": "clamp(14px, 11.913px + 0.6522vw, 20px)",
    //  "space-s-m": "clamp(18px, 13.8261px + 1.3043vw, 30px)",
    //  "space-m-l": "clamp(27px, 22.4783px + 1.413vw, 40px)",
    //  "space-l-xl": "clamp(36px, 27.6522px + 2.6087vw, 60px)",
    //  "space-xl-2xl": "clamp(54px, 44.9565px + 2.8261vw, 80px)",
    //  "space-2xl-3xl": "clamp(72px, 55.3043px + 5.2174vw, 120px)",
    //},
  },
};
