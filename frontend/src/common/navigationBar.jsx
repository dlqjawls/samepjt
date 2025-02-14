import React from "react"
import "./navigationBar.css"
import LoginButton from "./login"
import { useNavigate } from "react-router-dom"
import { toast } from "react-toastify"
import axios from "axios"
import Reward from "../main/CreditReward"
const Navbar = () => {
  const navigate = useNavigate()
  const rent_id = sessionStorage.getItem("rent_id") // rent_id 상태 확인
  const token = sessionStorage.getItem("token")
  const goToHomePage = () => {
    navigate("/")
  }
  const refreshAccessToken = async () => {
    try {
      const refreshToken = sessionStorage.getItem("refreshToken")
      if (!refreshToken) {
        throw new Error("리프레시 토큰이 없습니다.")
      }

      const response = await axios.post("https://backend-wandering-river-6835.fly.dev/auth/refresh-token", {
        refresh_token: refreshToken,
      })

      if (response.data.resultCode === "SUCCESS") {
        console.log("토큰 갱신 성공:", response.data)
        const { access_token, refresh_token } = response.data.data
        sessionStorage.setItem("token", access_token)
        sessionStorage.setItem("refreshToken", refresh_token)
        return access_token
      }
      throw new Error("토큰 갱신 실패")
    } catch (error) {
      console.error("토큰 갱신 중 오류:", error)
      toast.error("세션이 만료되었습니다. 다시 로그인해주세요.")
      sessionStorage.clear()
      navigate("/login")
      throw error
    }
  }
  const   goToRentalPage = async () => {
    const fetchRentStatus = async (token) => {
      return await axios.get(`${import.meta.env.VITE_API_URL}/user/rent/${rent_id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
    }

    try {
      let token = sessionStorage.getItem("token")
      if (!token) {
        toast.error("로그인이 필요합니다.")
        return
      }

      try {
        const response = await fetchRentStatus(token)
        if (response.data.resultCode === "SUCCESS") {
          sessionStorage.setItem("rentStatus", JSON.stringify(response.data.data))
          navigate("/car_status")
        }
      } catch (error) {
        if (error.response && error.response.status === 401) {
          // 토큰이 만료된 경우
          try {
            // 토큰 재발급
            token = await refreshAccessToken()
            // 재발급된 토큰으로 다시 요청
            const retryResponse = await fetchRentStatus(token)
            if (retryResponse.data.resultCode === "SUCCESS") {
              sessionStorage.setItem("rentStatus", JSON.stringify(retryResponse.data.data))
              navigate("/car_status")
            }
          } catch (refreshError) {
            console.error("토큰 갱신 실패:", refreshError)
            toast.error("세션이 만료되었습니다. 다시 로그인해주세요.")
            navigate("/login")
          }
        } else {
          console.error("차량 상태 조회 중 오류:", error)
          toast.error("차량 상태 조회에 실패했습니다.")
          navigate("/ModuleSetList")
        }
      }
    } catch (error) {
      console.error("차량 상태 조회 중 오류:", error)
      // toast.error("차량 상태 조회에 실패했습니다.");
      navigate("/ModuleSetList")
    }
  }
  return (
    <>
      <nav className="navbar">
        <div className="navbar-container">
          <button type="button" className="hide-button" onClick={goToHomePage}>
            <div className="navbar-logo">
              <img src="Vector.svg" alt="MODUCAR Logo" className="navbar-icon" />
              <span>MODUCAR</span>
            </div>
          </button>
          <div className="navbar-login">
            {rent_id && ( // rent_id가 있을 때만 버튼 표시
              <button type="button" className="rent-status-button" onClick={goToRentalPage}>
                대여중인 차량 정보
              </button>
            )}
         {token && ( // 토큰이 있을 때만 마이페이지 버튼 표시
              <button type="button" className="my-page-button" onClick={() => navigate("/mypage")}>
                마이페이지
              </button>
            )}
            <LoginButton />
          </div>
        </div>
      </nav>
      <Reward />
    </>
  )
}

export default Navbar
