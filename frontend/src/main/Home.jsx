import React, { useState, useEffect } from "react";
import LoginModal from "../LoginModal";
import { useNavigate } from "react-router-dom";
import "./Home.css";
function Home() {
  const navigate = useNavigate();

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
          onClick={goToRentalPage}
        />
        <div className="headline-content">
          <h2>모두가 원하는차</h2>
          <h3>모두카</h3>
          <p>아 퇴근하고싶다 정말 야근해야하나</p>
        </div>
      </div>
      {/* <button onClick={goToRentalPage}>대여페이지</button> */}

      {/* {isLoggedIn ? <button onClick={handleLogout}>로그아웃</button> : <button onClick={openModal}>로그인</button>}   
      {isModalOpen && <LoginModal onClose={closeModal} onLoginSuccess={handleLoginSuccess} />} */}
      {/* 대여페이지 버튼 */}
    </div>
  );
}

export default Home;
