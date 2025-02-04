import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { FaBell, FaEnvelope } from "react-icons/fa";
import "./Header.css";
import accountCircle from "../assets/account_circle.svg";
import { AdminAuthContext } from "./context/AdminAuthContext";

function Header() {
  const navigate = useNavigate();
  const { admin, logoutAdmin } = useContext(AdminAuthContext);

  const handleLogout = () => {
    logoutAdmin();
    navigate("/admin/login");
  };

  return (
    <header className="header">
      {/* 검색창 */}
      <div className="header-search">
        <input type="text" placeholder="검색" />
      </div>

      {/* 우측 아이콘/프로필 */}
      <div className="header-right">
        <FaBell className="icon" />
        <FaEnvelope className="icon" />
        <div className="profile">
          <img
            src={accountCircle}
            alt="admin-profile"
            className="profile-image"
          />
          <span className="profile-name">{admin ? admin.id : "관리자"}</span>
        </div>
        <button className="admin-logout-button" onClick={handleLogout}>
          로그아웃
        </button>
      </div>
    </header>
  );
}

export default Header;
