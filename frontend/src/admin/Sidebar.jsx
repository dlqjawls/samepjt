// admin/Sidebar.jsx
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
import blueCar from "../assets/blue_car.svg";
import SettingsModal from "./SettingsModal";

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
      <div className="sidebar-logo"></div>

      <nav className="sidebar-menu">
        <ul>
          <li>
            <NavLink
              to="/admin/index"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              aria-label="대시보드"
            >
              <FaChartPie className="nav-icon" />
              <p className="nav-text">대시보드</p>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/vehicle-management"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              aria-label="차량 관리"
            >
              <FaCar className="nav-icon" />
              <p className="nav-text">차량 관리</p>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/module-management"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              aria-label="모듈 관리"
            >
              <FaCogs className="nav-icon" />
              <p className="nav-text">모듈 관리</p>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/option-management"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              aria-label="옵션 관리"
            >
              <FaTools className="nav-icon" />
              <p className="nav-text">옵션 관리</p>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/record-management"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              aria-label="대여 기록"
            >
              <FaPlusSquare className="nav-icon" />
              <p className="nav-text">기록 조회</p>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/admin/maintenance-records"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              aria-label="정비 기록"
            >
              <MdEventNote className="nav-icon" />
              <p className="nav-text">정비 기록</p>
            </NavLink>
          </li>
        </ul>
      </nav>

      {/* <div className="sidebar-footer">
        <button
          className="settings-button"
          onClick={openSettingsModal}
          aria-label="설정"
        >
          <IoSettingsSharp className="nav-icon" />
          <span className="nav-text">설정</span>
        </button>
      </div> */}

      {/* 설정 모달 */}
      {isSettingsModalOpen && <SettingsModal onClose={closeSettingsModal} />}
    </aside>
  );
}

export default Sidebar;
