import React from "react";
import "./DashboardCard.css";

function DashboardCard({ title, value }) {
  return (
    <div className="dashboard-card">
      <p className="dashboard-card-title">{title}</p>
      <h2 className="dashboard-card-value">{value}</h2>
    </div>
  );
}

export default DashboardCard;
