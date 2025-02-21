// src/admin/components/OptionManagement.jsx
import React from "react";
import RentalRecords from "./RentalRecords";
import UsageRecords from "./UsageRecords";
import "./RecordManagement.css";

function RecordManagement() {
  return (
    <div className="record-management">
      <div className="rental">
        <RentalRecords />
      </div>
      <div className="usage">
        <UsageRecords />
      </div>
    </div>
  );
}

export default RecordManagement;
