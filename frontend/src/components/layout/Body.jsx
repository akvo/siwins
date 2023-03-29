import React from "react";

const Body = ({ children, className = "body", ...props }) => {
  return (
    <div className={className} {...props}>
      {children}
    </div>
  );
};

export default Body;
