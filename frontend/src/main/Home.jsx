import React, { useState, useEffect } from "react"
import LoginModal from "../common/LoginModal"
import { Meta, useNavigate } from "react-router-dom"
import axios from "axios"
import { toast } from "react-toastify"
import "./Home.css"

function Home() {
  const navigate = useNavigate()

  const goToRentalPage = async () => {
    const rent_id = sessionStorage.getItem("rent_id")

    if (rent_id) {
      try {
        const token = sessionStorage.getItem("token")
        if (!token) {
          toast.error("로그인이 필요합니다.")
          return
        }

        const response = await axios.get(`${import.meta.env.VITE_API_URL}/user/rent/${rent_id}`, {
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
    } else {
      navigate("/ModuleSetList")
    }
  }

  return (
    <div>
      <div className="image-container">
        <img src="modulecar.jpg" alt="car" className="full-screen-image" onClick={goToRentalPage} />
        {/* <div className="headline-content">
          <h2>모두가 원하는차</h2>
          <h3>모두카</h3>
          <p>아 퇴근하고싶다 정말 야근해야하나</p>
        </div> */}
      </div>
      {/* <button onClick={goToRentalPage}>대여페이지</button> */}

      {/* {isLoggedIn ? <button onClick={handleLogout}>로그아웃</button> : <button onClick={openModal}>로그인</button>}   
      {isModalOpen && <LoginModal onClose={closeModal} onLoginSuccess={handleLoginSuccess} />} */}
      {/* 대여페이지 버튼 */}
    </div>
  )
}

export default Home
