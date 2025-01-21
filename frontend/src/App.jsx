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
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/">
          <Route index element={<Home />} />
          <Route path="signup" element={<SignupPage />} />
          <Route path="RegistrationForm" element={<RegistrationForm />} />
          <Route path="ModuleSetList" element={<ModuleSetList />} />
          <Route path="optionlist" element={<OptionsPage />}></Route>
        </Route>
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="index" element={<MainDashboard />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
