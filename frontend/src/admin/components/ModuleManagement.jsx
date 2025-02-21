// src/admin/components/ModuleManagement.jsx
import React from "react";
import ModuleSetManagement from "./ModuleSetManagement";
import ModuleListManagement from "./ModuleListManagement";
import "./ModuleManagement.css";

function ModuleManagement() {
  return (
    <div className="module-management">
      <div className="module-set-management">
        <ModuleSetManagement />
      </div>
      <div className="module-list-management">
        <ModuleListManagement />
      </div>
    </div>
  );
}

export default ModuleManagement;
