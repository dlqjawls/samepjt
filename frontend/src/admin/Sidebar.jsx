import React from "react";
import { Link } from "react-router-dom";
import { FaChartPie, FaCar, FaCogs, FaTools } from "react-icons/fa";
import "./Sidebar.css";
import "../assets/moducar_logo.svg";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src="" alt="" />
      </div>

      <nav className="sidebar-menu">
        <ul>
          <li>
            <Link to="/">
              <FaChartPie />
              대시보드
            </Link>
          </li>
          <li>
            <Link to="/car-management">
              <FaCar />
              차량 관리
            </Link>
          </li>
          <li>
            <Link to="/module-management">
              <FaCogs />
              모듈 관리
            </Link>
          </li>
          <li>
            <Link to="/option-management">
              <FaTools />
              옵션 관리
            </Link>
          </li>
          <li>
            <Link to="/rental-records">대여 기록</Link>
          </li>
          <li>
            <Link to="/maintenance-records">정비 기록</Link>
          </li>
        </ul>
      </nav>

      <div className="sidebar-footer">
        <Link to="/settings">설정</Link>
      </div>
    </aside>
  );
}

export default Sidebar;
