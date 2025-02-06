import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import LoginModal from "../LoginModal"
import { toast } from "react-toastify";
import axios from "axios";
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

  const handleLoginSuccess = async (response) => {
    const token = response.data.token; // 백엔드 응답에서 토큰 추출
    sessionStorage.setItem("token", token); // 토큰 저장
    setIsLoggedIn(true);
    setIsModalOpen(false);
  }

  const handleLogout = async () => {
    try {
      const token = sessionStorage.getItem("token");
      const response = await axios.post(
        "https://backend-wandering-river-6835.fly.dev/auth/logout",
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
           
          }
        }
      );
  
      if (response.data.resultCode === 'SUCCESS') {
        sessionStorage.clear();
        setIsLoggedIn(false);
        toast.info("로그아웃 되었습니다.");
        navigate("/");
      } else {
        toast.error("로그아웃 처리 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error("로그아웃 오류:", error);
      // 에러가 발생하더라도 클라이언트 측 토큰은 제거
      sessionStorage.removeItem("token");
      setIsLoggedIn(false);
      navigate("/");
    }
  };
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
