// import "./App.css"

import React, { useState } from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import Home from "./main/Home"
import MyPage from "./common/myPage"
import RegistrationForm from "./signup/RegistrationForm"
import ModuleSetList from "./moduleSelect/ModuleSetList"
import AdminLogin from "./admin/Login"
import AdminLayout from "./admin/AdminLayout"
import MainDashboard from "./admin/MainDashboard"
import ExistOptionsPage from "./optionSelect/option_Select"
import Navbar from "./common/navigationBar"
import VehicleManagement from "./admin/components/VehicleManagement"
import ModuleManagement from "./admin/components/ModuleManagement"
import OptionManagement from "./admin/components/OptionManagement"
import RecordManagement from "./admin/components/RecordManagement"
import MaintenanceRecords from "./admin/components/MaintenanceRecords"
import RentForm from "./rentForm/rentForm"
import Total_reciept from "./finishSelect/total_reciept"
import UserLayout from "./user/UserLayout"
import Dashboard from "./RentStatus/Dashboard"
import { ToastContainer } from "react-toastify"
import { AdminAuthProvider } from "./admin/context/AdminAuthProvider"
import LoadingStatus from "./RentStatus/LoadingStatus"
function App() {
  return (
    <Router>
      <Routes>
        {/* 사용자 페이지 */}
        <Route path="/" element={<UserLayout />}>
          <Route index element={<Home />} />
          <Route path="myPage" element={<MyPage />} />
          
          <Route path="RegistrationForm" element={<RegistrationForm />} />
          <Route path="ModuleSetList" element={<ModuleSetList />} />
          <Route path="option_select" element={<ExistOptionsPage />}></Route>
          <Route path="rentForm" element={<RentForm />}></Route>
          <Route path="total_reciept" element={<Total_reciept />}></Route>
          <Route path="car_status" element={<Dashboard />}></Route>
          <Route path="/loading-status" element={<LoadingStatus />} />
        </Route>

        {/* 관리자 로그인 */}
        <Route
          path="/admin/login"
          element={
            <AdminAuthProvider>
              <AdminLogin />
            </AdminAuthProvider>
          }
        />
        {/* 관리자 페이지 */}
        <Route
          path="/admin/*"
          element={
            <AdminAuthProvider>
              <AdminLayout />
            </AdminAuthProvider>
          }
        >
          <Route path="index" element={<MainDashboard />} />
          <Route path="vehicle-management" element={<VehicleManagement />} />
          <Route path="module-management" element={<ModuleManagement />} />
          <Route path="option-management" element={<OptionManagement />} />
          <Route path="record-management" element={<RecordManagement />} />
          <Route path="maintenance-records" element={<MaintenanceRecords />} />
          <Route path="*" element={<Navigate to="/admin/index" replace />} />
        </Route>

        {/* 기타 라우트 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* ToastContainer - 앱 전역에서 생성된 토스트 알림들이 이 컨테이너에서 렌더링된다. */}
      <ToastContainer position="bottom-right" autoClose={3000} hideProgressBar={false} newestOnTop={false} closeOnClick pauseOnFocusLoss draggable pauseOnHover={false} />
    </Router>
  )
}

export default App
