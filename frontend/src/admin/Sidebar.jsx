import React from "react";
import { NavLink } from "react-router-dom";
import { FaChartPie, FaCar, FaCogs, FaTools, FaPlusSquare } from "react-icons/fa";
import { MdEventNote } from "react-icons/md";
import { IoSettingsSharp } from "react-icons/io5";
import "./Sidebar.css";
import moducarLogo from "../assets/moducar_logo.svg"

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src={moducarLogo} alt="" />
      </div>

      <nav className="sidebar-menu">
        <ul>
          <li>
            <NavLink to="/admin/index">
              <FaChartPie />
              대시보드
            </NavLink>

          </li>
          <li>
            <NavLink to="/admin/vehicle-management">
              <FaCar />
              차량 관리
            </NavLink>
          </li>
          <li>
            <NavLink to="/admin/module-management">
              <FaCogs />
              모듈 관리
            </NavLink>
          </li>
          <li>
          <NavLink to="/admin/option-management">
            <FaTools />
              옵션 관리
            </NavLink>
          </li>
          <li>
            <NavLink to="/admin/rental-records">
              <FaPlusSquare />
              대여 기록
            </NavLink>
          </li>
          <li>
            <NavLink to="/admin/maintenance-records">
              <MdEventNote />
              정비 기록
            </NavLink>
          </li>
        </ul>
      </nav>

      <div className="sidebar-footer">
      <NavLink to="/admin/setting">
        <IoSettingsSharp />
        설정</NavLink>
      </div>
    </aside>
  );
}

export default Sidebar;
