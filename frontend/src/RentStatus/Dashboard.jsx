import React from "react";
import {
  FaBatteryThreeQuarters,
  FaRoute,
  FaCar,
  FaMapMarkerAlt,
} from "react-icons/fa";
import "./Dashboard.css";
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useNavigate } from "react-router-dom";
function Dashboard() {
  const navigator = useNavigate();
  const rentStatus = JSON.parse(sessionStorage.getItem("rentStatus"));
  const currentRent = JSON.parse(sessionStorage.getItem("rentTime"));
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
  
    
    return `${year}년 ${month}월 ${day}일 ${hours}:${minutes}`;
  };
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
  };
  const refreshToken = async () => {
    try {
      const refresh_token = sessionStorage.getItem("refreshToken");
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/auth/refresh-token`,
        {
          refresh_token: refresh_token,
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        sessionStorage.setItem("token", response.data.data.access_token);
        sessionStorage.setItem(
          "refreshToken",
          response.data.data.refresh_token
        );
        return true;
      }
      return false;
    } catch (error) {
      return false;
    }
  };

  const cancelRent = async () => {
    try {
      const rent_id = sessionStorage.getItem("rent_id");
      let token = sessionStorage.getItem("token");

      console.log("렌트 취소 시작:", { rent_id, token });

      try {
        const response = await axios.delete(
          `${import.meta.env.VITE_API_URL}/user/rent/${rent_id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        console.log("API 응답:", response.data);

        if (response.data.resultCode === "SUCCESS") {
          console.log("렌트 취소 성공");
          toast.success("렌트가 성공적으로 취소되었습니다.");

          console.log("세션 정리 전");
          sessionStorage.removeItem("rentStatus");
          sessionStorage.removeItem("rent_id");
          console.log("세션 정리 후");
          navigator("/");
        }
      } catch (error) {
        console.log("첫 번째 try-catch 에러:", error);

        if (error.response && error.response.status === 401) {
          console.log("토큰 만료 감지, 갱신 시도");
          const isRefreshed = await refreshToken();
          console.log("토큰 갱신 결과:", isRefreshed);

          if (isRefreshed) {
            token = sessionStorage.getItem("token");
            console.log("새 토큰:", token);
            return cancelRent();
          } else {
            console.log("토큰 갱신 실패");
            sessionStorage.clear();
            navigator("/");
            toast.error("세션이 만료되었습니다. 다시 로그인해주세요.");
            return;
          }
        }
        throw error;
      }
    } catch (error) {
      console.log("최종 catch 블록 에러:", error);
      let errorMessage = "렌트 취소 중 오류가 발생했습니다.";

      if (error.response) {
        console.log("에러 응답:", error.response);
        switch (error.response.status) {
          case 403:
            errorMessage = "해당 렌트를 취소할 권한이 없습니다.";
            break;
          case 404:
            errorMessage = "해당 렌트 기록을 찾을 수 없습니다.";
            break;
          case 409:
            errorMessage = "이미 취소되었거나 완료된 렌트입니다.";
            break;
        }
      }

      console.log("표시할 에러 메시지:", errorMessage);
      toast.error(errorMessage);
    }
  };
  const completeRent = async () => {
    try {
      const rent_id = sessionStorage.getItem("rent_id");
      let token = sessionStorage.getItem("token");

      console.log("렌트 완료 시작:", { rent_id, token }); // 초기 값 확인

      try {
        console.log("API 요청 시작");
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/user/rent/${rent_id}/complete`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        console.log("API 응답:", response.data);

        if (response.data.resultCode === "SUCCESS") {
          console.log("렌트 완료 성공");

          console.log("세션 정리 전");
          sessionStorage.removeItem("rentStatus");
          sessionStorage.removeItem("rent_id");
          console.log("세션 정리 후");

          navigator("/");
          toast.success("차량이 성공적으로 반납되었습니다.");
          console.log("네비게이션 및 토스트 완료");
        }
      } catch (error) {
        console.log("첫 번째 try-catch 에러:", error);

        if (error.response && error.response.status === 401) {
          console.log("토큰 만료 감지, 갱신 시도");
          const isRefreshed = await refreshToken();
          console.log("토큰 갱신 결과:", isRefreshed);

          if (isRefreshed) {
            token = sessionStorage.getItem("token");
            console.log("새 토큰:", token);
            return completeRent();
          } else {
            console.log("토큰 갱신 실패");
            sessionStorage.clear();
            navigator("/");
            toast.error("세션이 만료되었습니다. 다시 로그인해주세요.");
            return;
          }
        }
        throw error;
      }
    } catch (error) {
      console.log("최종 catch 블록 에러:", error);
      let errorMessage = "렌트 완료 처리 중 오류가 발생했습니다.";

      if (error.response) {
        console.log("에러 응답:", error.response);
        switch (error.response.status) {
          case 403:
            errorMessage = "해당 렌트를 완료할 권한이 없습니다.";
            break;
          case 404:
            errorMessage = "해당 렌트 기록을 찾을 수 없습니다.";
            break;
          case 409:
            errorMessage = "이미 완료되었거나 취소된 렌트입니다.";
            break;
        }
      }

      console.log("표시할 에러 메시지:", errorMessage);
      toast.error(errorMessage);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="vehicle-card">
        <div className="arrival-status">
          <span className="arrival-badge">
            {rentStatus.isArrive ? "도착완료" : "이동중"}
          </span>
        
          <span className="eta-info">
            
            예상 도착 시간: {formatTime(rentStatus.ETA)}
          </span>
          <div>대여 시작: {currentRent ? formatDate(currentRent.rentStartDate) : "로딩 중..."}</div>
      <div>대여 종료: {currentRent ? formatDate(currentRent.rentEndDate) : "로딩 중..."}</div>
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
          {/* <div className="key-info">
            <span>블루키</span>
            <span>/</span>
            <span>Digital key</span>
          </div> */}
        </div>

        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">
              <FaCar /> 총 주행거리</div>
            <div className="stat-value">
              {(rentStatus.distanceTravelled / 1000).toFixed(3)}km
            </div>
          </div>
          <div className="stat-item">
            <div className="stat-label">
            <FaRoute /> 주행 가능거리</div>
            <div className="stat-value">287km</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">
               <FaBatteryThreeQuarters />배터리 잔량</div>
            <div className="stat-value">
              {rentStatus.status.vehicle.batteryLevel}%
            </div>
          </div>
        </div>

      

        <div className="score-section">
          <div className="score-title">차량 상태</div>
          <div className="score-value">
            <span className="score-number">정상 운행중</span>
            <span className="score-change">안전 운전하세요</span>
          </div>
          <div className="score-ranks">
            <button onClick={cancelRent}>대여취소</button>
            <button onClick={completeRent}>차량반납</button>
            <span>운행 시작: {formatDate(rentStatus.ETA)}</span>
            <span>추가 이용 요금: 측정중..</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
