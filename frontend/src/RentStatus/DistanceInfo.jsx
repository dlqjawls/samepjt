import React from "react"
import "./DistanceInfo.css"

const DistanceInfo = ({ distance }) => {
  const kilometers = (distance / 1000).toFixed(2)

  return (
    <div className="distance-info">
      <h2>주행 거리</h2>
      <p>{kilometers} km</p>
    </div>
  )
}

export default DistanceInfo
