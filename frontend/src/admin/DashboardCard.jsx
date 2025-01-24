import React from "react";
import "./DashboardCard.css";

function DashboardCard({ title, value }) {
  return (
    <div className="dashboard-card">
      <p>{title}</p>
      <h2>{value}</h2>
    </div>
  );
}

export default DashboardCard;
