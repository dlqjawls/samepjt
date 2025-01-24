// import "./App.css"

import React, { useState } from "react"
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom"
import Home from "./main/Home"
import SignupPage from "./SignupPage"
import RegistrationForm from "./RegistrationForm"
import ModuleSetList from "./ModuleSetList"
import AdminLogin from "./admin/Login"
import AdminLayout from "./admin/AdminLayout"
import MainDashboard from "./admin/MainDashboard"
import OptionsPage from "./optionSelect/option_list"
import ExistOptionsPage from "./optionSelect/option_Select"
import Navbar from "./common/navigationBar"
import VehicleManagement from "./admin/components/VehicleManagement";
import ModuleManagement from "./admin/components/ModuleManagement";
import OptionManagement from "./admin/components/OptionManagement";
import RentalRecords from "./admin/components/RentalRecords";
import MaintenanceRecords from "./admin/components/MaintenanceRecords";
import OptionSelect from "./optionSelect/optionSelect"

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/">
          <Route index element={<Home />} />
          <Route path="signup" element={<SignupPage />} />
          <Route path="RegistrationForm" element={<RegistrationForm />} />
          <Route path="ModuleSetList" element={<ModuleSetList />} />
          <Route path="optionlist" element={<OptionsPage />}></Route>
          <Route path="exist_option" element={<ExistOptionsPage />}></Route>
          <Route path="option_select" element={<OptionSelect />}></Route>

        </Route>
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="index" element={<MainDashboard />} />
          <Route path="vehicle-management" element={<VehicleManagement />} />
          <Route path="module-management" element={<ModuleManagement />} />
          <Route path="option-management" element={<OptionManagement />} />
          <Route path="rental-records" element={<RentalRecords />} />
          <Route path="maintenance-records" element={<MaintenanceRecords />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
