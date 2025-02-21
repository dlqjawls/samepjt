import React, { useContext, useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FaBell, FaEnvelope } from "react-icons/fa";
import "./Header.css";
import accountCircle from "../assets/account_circle.svg";
import { AdminAuthContext } from "./context/AdminAuthContext";
import { TbDatabaseSearch } from "react-icons/tb";
// 반드시 이 형식으로 라이브러리를 불러와야 한다.
import { jwtDecode } from "jwt-decode";

function Header() {
  const navigate = useNavigate();
  const { admin, logoutAdmin, accessToken, refreshTokens } =
    useContext(AdminAuthContext);
  const [showDropdown, setShowDropdown] = useState(false);
  const profileRef = useRef(null);
  const [timeLeft, setTimeLeft] = useState(null);

  const handleLogout = () => {
    logoutAdmin();
    navigate("/admin/login");
  };

  const toggleDropdown = (e) => {
    e.stopPropagation();
    setShowDropdown((prev) => !prev);
  };

  const calculateTimeLeft = (token) => {
    try {
      const decoded = jwtDecode(token);
      // console.log("디코딩된 토큰:", decoded);
      if (!decoded.exp) {
        console.error("토큰에 exp가 없습니다.");
        return 0;
      }
      const expiryTime = decoded.exp * 1000;
      const currentTime = Date.now();
      const remaining = expiryTime - currentTime;
      return remaining > 0 ? remaining : 0;
    } catch (error) {
      console.error("토큰 디코딩 오류:", error);
      return 0;
    }
  };

  useEffect(() => {
    if (accessToken) {
      const intervalId = setInterval(() => {
        setTimeLeft(calculateTimeLeft(accessToken));
      }, 1000);
      return () => clearInterval(intervalId);
    }
  }, [accessToken]);

  const formatTime = (milliseconds) => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
    const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(
      2,
      "0"
    );
    const seconds = String(totalSeconds % 60).padStart(2, "0");
    return `${minutes}분 ${seconds}초`;
    // return `${hours}시간 ${minutes}분 ${seconds}초`;
  };

  const refreshToken = localStorage.getItem("adminRefreshToken");

  const isRefreshTokenExpired = () => {
    if (!refreshToken) {
      return true;
    }
    try {
      const decoded = jwtDecode(refreshToken);
      if (!decoded.exp) {
        return true;
      }
      const expiryTime = decoded.exp * 1000;
      return expiryTime < Date.now();
    } catch (error) {
      console.log("리프레시 토큰 디코딩 오류:", error);
      return true;
    }
  };

  const handleManualRefresh = async () => {
    try {
      await refreshTokens();
    } catch (error) {
      console.error("수동 토큰 갱신 실패:", error);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <header className="header">
      {/* 검색창 */}
      <div className="header-search">
        {/* <input type="text" placeholder="검색" />
        <button className="total-search-button">
          <TbDatabaseSearch />
        </button> */}
      </div>
      <div className="header-left">
        {accessToken && (
          <button
            className="token-refresh-button"
            onClick={handleManualRefresh}
            disabled={isRefreshTokenExpired()}
          >
            {isRefreshTokenExpired() ? "연장 불가" : "시간 연장"}
          </button>
        )}
        {accessToken && (
          <div className="token-expiry">
            {timeLeft !== null ? formatTime(timeLeft) : ""}
          </div>
        )}
      </div>

      {/* 우측 아이콘/프로필 */}
      <div className="header-right">
        {/* <FaBell className="icon" />
        <FaEnvelope className="icon" /> */}
        <div className="profile" onClick={toggleDropdown} ref={profileRef}>
          <img
            src={accountCircle}
            alt="admin-profile"
            className="profile-image"
          />
          <span className="profile-name">{admin ? admin.id : "관리자"}</span>
          {showDropdown && (
            <div className="profile-dropdown">
              <button className="admin-logout-button" onClick={handleLogout}>
                로그아웃
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
