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
  const refreshAccessToken = async () => {
    try {
      const refreshToken = sessionStorage.getItem("refreshToken");
      if (!refreshToken) {
        throw new Error("리프레시 토큰이 없습니다.");
      }

      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/auth/refresh-token`,
        {
          refresh_token: refreshToken
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        console.log("토큰 갱신 성공:", response.data);
        const { access_token, refresh_token } = response.data.data;
        sessionStorage.setItem("token", access_token);
        sessionStorage.setItem("refreshToken", refresh_token);
        return access_token;
      }
      throw new Error("토큰 갱신 실패");
    } catch (error) {
      console.error("토큰 갱신 중 오류:", error);
      toast.error("세션이 만료되었습니다. 다시 로그인해주세요.");
      sessionStorage.clear();
      navigate("/login");
      throw error;
    }
  };
  const handleLogout = async () => {
    const makeLogoutRequest = async (token) => {
      return await axios.post(
        `${import.meta.env.VITE_API_URL}/auth/logout`,
        {},  // request body
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
    };
  
    try {
      let token = sessionStorage.getItem("token");
      if (!token) {
        throw new Error("토큰이 없습니다.");
      }
  
      try {
        const response = await makeLogoutRequest(token);
        if (response.data.resultCode === 'SUCCESS') {
          sessionStorage.clear();
          setIsLoggedIn(false);
          toast.info("로그아웃 되었습니다.");
          navigate("/");
        }
      } catch (error) {
        if (error.response && error.response.status === 401) {
          // 토큰이 만료된 경우
          try {
            // 토큰 재발급
            token = await refreshAccessToken();
            // 재발급된 토큰으로 다시 로그아웃 요청
            const retryResponse = await makeLogoutRequest(token);
            if (retryResponse.data.resultCode === 'SUCCESS') {
              sessionStorage.clear();
              setIsLoggedIn(false);
              toast.info("로그아웃 되었습니다.");
              navigate("/");
            }
          } catch (refreshError) {
            console.error("토큰 갱신 실패:", refreshError);
            // 토큰 갱신 실패 시 강제 로그아웃
            sessionStorage.clear();
            setIsLoggedIn(false);
            navigate("/");
          }
        } else {
          throw error;
        }
      }
    } catch (error) {
      console.error("로그아웃 오류:", error);
      toast.error("로그아웃 처리 중 오류가 발생했습니다.");
      // 에러가 발생하더라도 클라이언트 측 토큰은 제거
      sessionStorage.clear();
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
