import React from "react"
import "./BatteryStatus.css"

const BatteryStatus = ({ batteryLevel }) => {
  const getBatteryColor = (level) => {
    if (level <= 20) return "#ff4d4d"
    if (level <= 50) return "#ffd700"
    return "#4caf50"
  }

  return (
    <div className="custom-battery-status">
      <h2 className="custom-battery-title">배터리 상태</h2>
      <div className="custom-battery-container">
        <div className="custom-battery-terminal">
          <div className="custom-battery-plus-sign">+</div>
        </div>
        <div className="custom-battery-body">
          <div
            className="custom-battery-liquid"
            style={{
              height: `${batteryLevel}%`,
              backgroundColor: getBatteryColor(batteryLevel),
            }}
          >
            <div className="custom-battery-waves">
              <div className="custom-wave custom-wave1"></div>
              <div className="custom-wave custom-wave2"></div>
              <div className="custom-wave custom-wave3"></div>
            </div>
          </div>
        </div>
      </div>
      <p className="custom-battery-percentage">{batteryLevel}%</p>
    </div>
  )
}

export default BatteryStatus
