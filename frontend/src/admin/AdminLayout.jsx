import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";
import "./AdminLayout.css";
import { AdminAuthContext } from "./context/AdminAuthContext";
import { Navigate } from "react-router-dom";
import { useContext } from "react";

function DashboardLayout() {
  const { admin } = useContext(AdminAuthContext);

  if (!admin) {
    return <Navigate to="/admin/login" replace />;
  }

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
