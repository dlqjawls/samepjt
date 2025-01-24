import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  FaChartPie,
  FaCar,
  FaCogs,
  FaTools,
  FaPlusSquare,
} from "react-icons/fa";
import { MdEventNote } from "react-icons/md";
import { IoSettingsSharp } from "react-icons/io5";
import "./Sidebar.css";
import moducarLogo from "../assets/moducar_logo.svg";
import SettingsModal from "./SettingsModal"; // SettingsModal 컴포넌트 임포트

function Sidebar() {
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

  const openSettingsModal = () => {
    setIsSettingsModalOpen(true);
  };

  const closeSettingsModal = () => {
    setIsSettingsModalOpen(false);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src={moducarLogo} alt="Moducar Logo" />
      </div>

      <nav className="sidebar-menu">
        <ul>
          <li>
            <NavLink
              to="/admin/index"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <FaChartPie className="nav-icon" />
              대시보드
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/vehicle-management"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <FaCar className="nav-icon" />
              차량 관리
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/module-management"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <FaCogs className="nav-icon" />
              모듈 관리
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/option-management"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <FaTools className="nav-icon" />
              옵션 관리
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/rental-records"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <FaPlusSquare className="nav-icon" />
              대여 기록
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/maintenance-records"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <MdEventNote className="nav-icon" />
              정비 기록
            </NavLink>
          </li>
        </ul>
      </nav>

      <div className="sidebar-footer">
        <button
          className="nav-link settings-button"
          onClick={openSettingsModal}
        >
          <IoSettingsSharp className="nav-icon" />
          설정
        </button>
      </div>

      {/* 설정 모달 */}
      {isSettingsModalOpen && <SettingsModal onClose={closeSettingsModal} />}
    </aside>
  );
}

export default Sidebar;
