import React from "react"
import "./MiniMap.css"

const MiniMap = ({ location, destination }) => {
  return (
    <div className="mini-map">
      <h2>현재 위치</h2>
      <div className="map-coordinates">
        <p>위도: {location.x}</p>
        <p>경도: {location.y}</p>
      </div>
      <h3>목적지</h3>
      <div className="map-coordinates">
        <p>위도: {destination.x}</p>
        <p>경도: {destination.y}</p>
      </div>
    </div>
  )
}

export default MiniMap
