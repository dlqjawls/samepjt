// import "./App.css"

import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Home from "./main/Home";
import SignupPage from "./SignupPage";
import RegistrationForm from "./RegistrationForm";
import ModuleSetList from "./ModuleSetList";
import AdminLogin from "./admin/Login";
import AdminLayout from "./admin/AdminLayout";
import MainDashboard from "./admin/MainDashboard";
import OptionsPage from "./optionSelect/option_list";
import ExistOptionsPage from "./optionSelect/option_Select";
import Navbar from "./common/navigationBar";
import VehicleManagement from "./admin/components/VehicleManagement";
import ModuleManagement from "./admin/components/ModuleManagement";
import OptionManagement from "./admin/components/OptionManagement";
import RentalRecords from "./admin/components/RentalRecords";
import MaintenanceRecords from "./admin/components/MaintenanceRecords";
import OptionSelect from "./optionSelect/optionSelect";
import RentForm from "./rentForm/rentForm";
import Total_reciept from "./finishSelect/total_reciept";
import UserLayout from "./user/userLayout";

function App() {
  return (
    <Router>
      <Routes>
        {/* 사용자 페이지 */}
        <Route path="/" element={<UserLayout />}>
          <Route index element={<Home />} />
          <Route path="signup" element={<SignupPage />} />
          <Route path="RegistrationForm" element={<RegistrationForm />} />
          <Route path="ModuleSetList" element={<ModuleSetList />} />
          <Route path="optionlist" element={<OptionsPage />}></Route>
          <Route path="exist_option" element={<ExistOptionsPage />}></Route>
          <Route path="option_select" element={<OptionSelect />}></Route>
          <Route path="rentForm" element={<RentForm />}></Route>
          <Route path="total_reciept" element={<Total_reciept />}></Route>
        </Route>

        {/* 관리자 로그인 */}
        <Route path="/admin/login" element={<AdminLogin />} />
        {/* 관리자 페이지 */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="index" element={<MainDashboard />} />
          <Route path="vehicle-management" element={<VehicleManagement />} />
          <Route path="module-management" element={<ModuleManagement />} />
          <Route path="option-management" element={<OptionManagement />} />
          <Route path="rental-records" element={<RentalRecords />} />
          <Route path="maintenance-records" element={<MaintenanceRecords />} />
        </Route>

        {/* 기타 라우트 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
