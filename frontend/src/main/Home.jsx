import React, { useState, useEffect } from "react";
import LoginModal from "../LoginModal";
import { useNavigate } from "react-router-dom";
import "./Home.css";
function Home() {
  const navigate = useNavigate();

  // 로그인 상태를 확인하는 함수

  // 대여 페이지 이동
  const goToRentalPage = () => {
    navigate("/ModuleSetList"); // 대여 페이지로 이동
  };

  return (
    <div>
      <div className="image-container">
        <img
          src="../public/PBVCAR.png"
          alt="car"
          className="full-screen-image"
        />
      </div>

      {/* {isLoggedIn ? <button onClick={handleLogout}>로그아웃</button> : <button onClick={openModal}>로그인</button>}

    
      {isModalOpen && <LoginModal onClose={closeModal} onLoginSuccess={handleLoginSuccess} />} */}
      {/* 대여페이지 버튼 */}
      <button onClick={goToRentalPage}>대여페이지</button>
    </div>
  );
}

export default Home;
