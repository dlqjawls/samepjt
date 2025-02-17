import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./LoadingStatus.css";

const LoadingStatus = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    // 각 단계별 타이밍 설정
    const timer1 = setTimeout(() => setCurrentStep(2), 2000); // 2초 후 출발 단계
    const timer2 = setTimeout(() => setCurrentStep(3), 4000); // 4초 후 도착 단계
    const timer3 = setTimeout(() => navigate("/dashboard"), 6000); // 6초 후 대시보드로 이동

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
          <div className="step-label">도착</div>
          {currentStep === 3 && <div className="loading-animation"></div>}
        </div>
      </div>
    </div>
  );
};

export default LoadingStatus;