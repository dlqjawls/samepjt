import React, { useContext, useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FaBell, FaEnvelope } from "react-icons/fa";
import "./Header.css";
import accountCircle from "../assets/account_circle.svg";
import { AdminAuthContext } from "./context/AdminAuthContext";
import { TbDatabaseSearch } from "react-icons/tb";

function Header() {
  const navigate = useNavigate();
  const { admin, logoutAdmin } = useContext(AdminAuthContext);
  const [showDropdown, setShowDropdown] = useState(false);
  const profileRef = useRef(null);

  const handleLogout = () => {
    logoutAdmin();
    navigate("/admin/login");
  };

  const toggleDropdown = (e) => {
    e.stopPropagation();
    setShowDropdown((prev) => !prev);
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
