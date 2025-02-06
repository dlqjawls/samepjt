import React from "react"
import "./navigationBar.css"
import LoginButton from "./login"
import { useNavigate } from "react-router-dom"

const Navbar = () => {
  const navigate = useNavigate()
  const goToHomePage = () => {
    navigate("/")
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <button type="button" className="hide-button" onClick={goToHomePage}>
          <div className="navbar-logo">
            <img src="Vector.svg" alt="MODUCAR Logo" className="navbar-icon" />
            <span>MODUCAR</span>
          </div>
          
        </button>
        <div className="navbar-login">
          <LoginButton />
        </div>

      </div>
    </nav>
  )
}

export default Navbar
