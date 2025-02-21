// src/admin/components/OptionManagement.jsx
import React from "react";
import Option from "./Option";
import OptionType from "./OptionType";
import "./OptionManagement.css";

function OptionManagement() {
  return (
    <div className="option-management">
      <div className="option">
        <Option />
      </div>
      <div className="option-type">
        <OptionType />
      </div>
    </div>
  );
}

export default OptionManagement;
