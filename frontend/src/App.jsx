// import "./App.css"

import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./Home";
import SignupPage from "./SignupPage";
import RegistrationForm from "./RegistrationForm";
import ModuleSetList from "./ModuleSetList";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/RegistrationForm" element={<RegistrationForm />} />
        <Route path="/ModuleSetList" element={<ModuleSetList/>}/>
      </Routes>
    </Router>
  );
}

export default App;