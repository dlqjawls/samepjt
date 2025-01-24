import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import LoginModal from "../LoginModal"

const LoginButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false) // 모달 상태
  const [isLoggedIn, setIsLoggedIn] = useState(false) // 로그인 상태
  const navigate = useNavigate()

  // 로그인 상태 확인
  useEffect(() => {
    const token = sessionStorage.getItem("token")
    setIsLoggedIn(!!token)
  })

  const openModal = () => setIsModalOpen(true)
  const closeModal = () => setIsModalOpen(false)

  const handleLoginSuccess = () => {
    sessionStorage.setItem("token") // 임시 토큰 저장
    setIsLoggedIn(true)
    setIsModalOpen(false)
    alert("로그인 성공!")
  }

  const handleLogout = () => {
    sessionStorage.removeItem("token")
    setIsLoggedIn(false)
    alert("로그아웃되었습니다.")
    navigate("/") // 홈으로 리디렉션
  }

  return (
    <>
      {isLoggedIn ? (
        <button onClick={handleLogout} className="login-button">
          로그아웃
        </button>
      ) : (
        <button onClick={openModal} className="login-button">
          로그인
        </button>
      )}
      {isModalOpen && <LoginModal onClose={closeModal} onLoginSuccess={handleLoginSuccess} />}
    </>
  )
}

export default LoginButton
