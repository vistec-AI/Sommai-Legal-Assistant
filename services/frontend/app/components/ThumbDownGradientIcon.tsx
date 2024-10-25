import React from "react";

const ThumbDownGradientIcon = ({ width = 20, height = 20, className = "" }) => {
  const uniqueId = React.useId();
  const gradientId = `paint0_linear_${uniqueId}`;

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M14.1665 1.66675V10.8334M18.3332 8.16675V4.33341C18.3332 3.39999 18.3332 2.93328 18.1516 2.57676C17.9918 2.26316 17.7368 2.00819 17.4232 1.8484C17.0667 1.66675 16.6 1.66675 15.6665 1.66675H6.76489C5.54699 1.66675 4.93804 1.66675 4.4462 1.88961C4.01271 2.08603 3.6443 2.4021 3.38425 2.80068C3.08919 3.25291 2.99659 3.85478 2.8114 5.05852L2.37551 7.89185C2.13125 9.47951 2.00912 10.2733 2.24472 10.891C2.4515 11.4332 2.84042 11.8865 3.34482 12.1733C3.91949 12.5001 4.72266 12.5001 6.32899 12.5001H6.99988C7.46659 12.5001 7.69995 12.5001 7.87821 12.5909C8.03501 12.6708 8.16249 12.7983 8.24239 12.9551C8.33321 13.1333 8.33321 13.3667 8.33321 13.8334V16.2785C8.33321 17.4134 9.25321 18.3334 10.3881 18.3334C10.6588 18.3334 10.9041 18.174 11.014 17.9266L13.8146 11.6252C13.942 11.3386 14.0057 11.1953 14.1064 11.0902C14.1954 10.9974 14.3047 10.9263 14.4257 10.8827C14.5626 10.8334 14.7194 10.8334 15.033 10.8334H15.6665C16.6 10.8334 17.0667 10.8334 17.4232 10.6518C17.7368 10.492 17.9918 10.237 18.1516 9.9234C18.3332 9.56688 18.3332 9.10017 18.3332 8.16675Z"
        stroke={`url(#${gradientId})`}
        strokeWidth="1.66667"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M14.1665 1.66675V10.8334M18.3332 8.16675V4.33341C18.3332 3.39999 18.3332 2.93328 18.1516 2.57676C17.9918 2.26316 17.7368 2.00819 17.4232 1.8484C17.0667 1.66675 16.6 1.66675 15.6665 1.66675H6.76489C5.54699 1.66675 4.93804 1.66675 4.4462 1.88961C4.01271 2.08603 3.6443 2.4021 3.38425 2.80068C3.08919 3.25291 2.99659 3.85478 2.8114 5.05852L2.37551 7.89185C2.13125 9.47951 2.00912 10.2733 2.24472 10.891C2.4515 11.4332 2.84042 11.8865 3.34482 12.1733C3.91949 12.5001 4.72266 12.5001 6.32899 12.5001H6.99988C7.46659 12.5001 7.69995 12.5001 7.87821 12.5909C8.03501 12.6708 8.16249 12.7983 8.24239 12.9551C8.33321 13.1333 8.33321 13.3667 8.33321 13.8334V16.2785C8.33321 17.4134 9.25321 18.3334 10.3881 18.3334C10.6588 18.3334 10.9041 18.174 11.014 17.9266L13.8146 11.6252C13.942 11.3386 14.0057 11.1953 14.1064 11.0902C14.1954 10.9974 14.3047 10.9263 14.4257 10.8827C14.5626 10.8334 14.7194 10.8334 15.033 10.8334H15.6665C16.6 10.8334 17.0667 10.8334 17.4232 10.6518C17.7368 10.492 17.9918 10.237 18.1516 9.9234C18.3332 9.56688 18.3332 9.10017 18.3332 8.16675Z"
        stroke="white"
        strokeOpacity="0.3"
        strokeWidth="1.66667"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <defs>
        <linearGradient
          id={gradientId}
          x1="2.11816"
          y1="18.3334"
          x2="18.3332"
          y2="18.3334"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#7873F5" />
          <stop offset="1" stopColor="#E9465A" />
        </linearGradient>
      </defs>
    </svg>
  );
};

export default ThumbDownGradientIcon;
