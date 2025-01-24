import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";
import "./AdminLayout.css";

function DashboardLayout() {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="main-area">
        <Header />
        <div className="content-area">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

export default DashboardLayout;
