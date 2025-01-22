import React, { useState, useEffect } from "react";
import LoginModal from "../LoginModal";
import { useNavigate } from "react-router-dom";

function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false); // 로그인 모달 열기/닫기 상태
  const [isLoggedIn, setIsLoggedIn] = useState(false); // 로그인 여부 상태
  const navigate = useNavigate();

  // 로그인 상태를 확인하는 함수
  const checkLoginStatus = () => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token); // 토큰이 있으면 true, 없으면 false
  };

  // 컴포넌트 마운트 시 로그인 상태 확인
  useEffect(() => {
    checkLoginStatus();  //로그인시 일때만  확인    
  });

  // 로그인 모달 열기
  const openModal = () => setIsModalOpen(true);

  // 로그인 모달 닫기
  const closeModal = () => setIsModalOpen(false);

  // 로그아웃 핸들러
  const handleLogout = () => {
    localStorage.removeItem("token"); // 토큰 삭제
    setIsLoggedIn(false); // 로그인 상태 업데이트
    alert("로그아웃 되었습니다.");
    navigate("/"); // 홈으로 리디렉션
  };

  // 로그인 성공 시 호출
  const handleLoginSuccess = () => {
    localStorage.setItem("token", "sample_token"); // 예시로 토큰 저장
    setIsLoggedIn(true); // 로그인 상태 즉시 업데이트
    setIsModalOpen(false); // 모달 닫기
    alert("로그인 성공!");
    checkLoginStatus(); // 상태 업데이트 (함수 호출 시 괄호 추가)
  };

  // 대여 페이지 이동
  const goToRentalPage = () => {
    navigate("/ModuleSetList"); // 대여 페이지로 이동
  };

  return (
    <div>
      <h1>Home Page</h1>

      {/* 로그인 여부에 따라 버튼 렌더링 */}
      {isLoggedIn ? (
        <button onClick={handleLogout}>로그아웃</button>
      ) : (
        <button onClick={openModal}>로그인</button>
      )}

      {/* 로그인 모달 */}
      {isModalOpen && (
        <LoginModal
          onClose={closeModal}
          onLoginSuccess={handleLoginSuccess}
        />
      )}

      {/* 대여페이지 버튼 */}
      <button onClick={goToRentalPage}>대여페이지</button>
    </div>
  );
}

export default Home;
