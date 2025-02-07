import React from "react"
import "./navigationBar.css"
import LoginButton from "./login"
import { useNavigate } from "react-router-dom"
import { toast } from "react-toastify"
import axios from "axios"
const Navbar = () => {
  const navigate = useNavigate()
  const rent_id = sessionStorage.getItem("rent_id")  // rent_id 상태 확인
  
  const goToHomePage = () => {
    navigate("/")
  }
  
  const goToRentalPage = async () => {
    try {
      const token = sessionStorage.getItem("token")
      if (!token) {
        toast.error("로그인이 필요합니다.")
        return
      }

      const response = await axios.get(`https://backend-wandering-river-6835.fly.dev/user/rent/${rent_id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.data.resultCode === "SUCCESS") {
        sessionStorage.setItem("rentStatus", JSON.stringify(response.data.data))
        navigate("/car_status")
      }
    } catch (error) {
      console.error("차량 상태 조회 중 오류:", error)
      toast.error("차량 상태 조회에 실패했습니다.")
      navigate("/ModuleSetList")
    }
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
          {rent_id && (  // rent_id가 있을 때만 버튼 표시
            <button type="button" className="rent-status-button" onClick={goToRentalPage}>
              대여중인 차량 정보
            </button>
          )}
          <LoginButton />
        </div>
      </div>
    </nav>
  )
}

export default Navbar