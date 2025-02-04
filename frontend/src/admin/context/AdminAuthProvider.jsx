import React, { useState, useEffect } from "react";
import { AdminAuthContext } from "./AdminAuthContext";

export const AdminAuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(() => {
    const storedAdmin = localStorage.getItem("adminInfo");
    return storedAdmin ? JSON.parse(storedAdmin) : null;
  });

  const loginAdmin = (adminData) => {
    setAdmin(adminData);
    localStorage.setItem("adminInfo", JSON.stringify(adminData));
  };

  const logoutAdmin = () => {
    setAdmin(null);
    localStorage.removeItem("adminInfo");
    localStorage.removeItem("adminToken");
  };

  return (
    <AdminAuthContext.Provider value={{ admin, loginAdmin, logoutAdmin }}>
      {children}
    </AdminAuthContext.Provider>
  );
};
