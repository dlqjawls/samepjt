import React from "react";
import { FaBell, FaEnvelope } from "react-icons/fa";
import "./Header.css";

function Header() {
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
          <span className="profile-name">Admin</span>
          <img 
            src="/images/profile.png"
            alt="admin-profile"
            className="profile-image"
          />
        </div>
      </div>
    </header>
  );
}

export default Header;
