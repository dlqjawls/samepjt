import React from "react"
import { FaBatteryThreeQuarters, FaRoute, FaCar, FaMapMarkerAlt } from "react-icons/fa"
import "./Dashboard.css"

function Dashboard() {
  const rentStatus = JSON.parse(sessionStorage.getItem("rentStatus"))

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, "0")}`
  }

  return (
    <div className="dashboard-container">
      <div className="vehicle-card">
        <div className="arrival-status">
          <span className="arrival-badge">{rentStatus.isArrive ? "도착완료" : "이동중"}</span>
          <span className="eta-info">예상 도착 시간: {formatDate(rentStatus.ETA)}</span>
        </div>

        <div className="map-preview">
          <div className="coordinates">
            <div>
              <FaMapMarkerAlt /> 현재 위치:
              <div>위도: {rentStatus.location.x}</div>
              <div>경도: {rentStatus.location.y}</div>
            </div>
            <div>
              <FaMapMarkerAlt /> 목적지:
              <div>위도: {rentStatus.destination.x}</div>
              <div>경도: {rentStatus.destination.y}</div>
            </div>
          </div>
        </div>

        <div className="vehicle-header">
          <div className="vehicle-title">
            <h1 className="vehicle-name">PBV 모듀카</h1>
            <span className="vehicle-number">123가4589</span>
          </div>
          <div className="key-info">
            <span>블루키</span>
            <span>/</span>
            <span>Digital key</span>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">총 주행거리</div>
            <div className="stat-value">{(rentStatus.distanceTravelled / 1000).toFixed(3)}km</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">주행 가능거리</div>
            <div className="stat-value">287km</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">배터리 잔량</div>
            <div className="stat-value">{rentStatus.status.vehicle.batteryLevel}%</div>
          </div>
        </div>

        <div className="icon-row">
          <FaBatteryThreeQuarters size={24} color="#FF4444" />
          <FaRoute size={24} color="#FFB800" />
          <FaCar size={24} color="#CCCCCC" />
        </div>

        <div className="score-section">
          <div className="score-title">흠</div>
          <div className="score-value">
            <span className="score-number">뭘로채우지</span>
            <span className="score-change">아무거나나</span>
          </div>
          <div className="score-ranks">
            <span>정말</span>
            <span>모르겠군</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
