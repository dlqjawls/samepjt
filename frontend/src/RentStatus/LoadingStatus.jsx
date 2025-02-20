import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./LoadingStatus.css";
import axios from "axios";

const LoadingStatus = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCurrentRent = async () => {
      const token = sessionStorage.getItem("token");
      try {
        const currentRentResponse = await axios.get(
          `${import.meta.env.VITE_API_URL}/user/me/rent/current`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (currentRentResponse.data.resultCode === "SUCCESS") {
          console.log("현재 진행 중인 렌트 정보 조회 완료:", currentRentResponse.data);
          sessionStorage.setItem("rentTime", JSON.stringify(currentRentResponse.data.data));
        }
      } catch (error) {
        if (error.response && error.response.status === 404) {
          console.log("진행 중인 렌트 정보가 없습니다.");
        } else {
          console.error("현재 진행 중인 렌트 정보 조회 중 오류:", error);
        }
      }
    };

    // API 호출 실행
    fetchCurrentRent();
    const timer1 = setTimeout(() => setCurrentStep(2), 13000); 
    const timer2 = setTimeout(() => setCurrentStep(3), 25000); 
    const timer3 = setTimeout(() => navigate("/car_status"), 30000); 

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [navigate]);

  return (
    <div className="loading-container">
      <div className="loading-steps">
        <div className={`step ${currentStep >= 1 ? 'active' : ''}`}>
          <div className="step-circle">1</div>
          <div className="step-label">차량 준비중</div>
          {currentStep === 1 && <div className="loading-animation"></div>}
        </div>
        <div className={`step ${currentStep >= 2 ? 'active' : ''}`}>
          <div className="step-circle">2</div>
          <div className="step-label">출발중</div>
          {currentStep === 2 && <div className="loading-animation"></div>}
        </div>
        <div className={`step ${currentStep >= 3 ? 'active' : ''}`}>
          <div className="step-circle">3</div>
          <div className="step-label">
    {currentStep === 3 ? (
      <span className="arrival-text">차량 도착!</span>
    ) : (
      "차량 도착"
    )}
  </div>
  {currentStep === 3 && <div className="loading-animation"></div>}
</div>
      </div>
    </div>
  );
};

export default LoadingStatus;