import React, { useState } from "react";
import "./rentForm.css";
import { useNavigate } from "react-router-dom";
const RentForm = () => {
  const [rentStartDate, setRentStartDate] = useState(""); // 렌트 시작일
  const [rentEndDate, setRentEndDate] = useState(""); // 반납일
  const navigate = useNavigate();
  const total = () => {
    navigate("/total_reciept");
  };

  return (
    <div className="rent-form-wrapper">
      {/* 지도 영역 */}
      <div className="map-container">
        <img
          src="../public/map.png" // 실제 이미지 경로로 변경
          alt="지도 이미지"
          className="map-image"
        />
      </div>

      {/* 폼 영역 */}
      <div className="form-container">
        <h3 className="form-title">렌트카 대여 설정</h3>

        {/* 입력 폼 */}
        <form>
          {/* 렌트 시작일 */}
          <div className="form-group">
            <label htmlFor="rentStartDate">렌트 시작일</label>
            <input
              type="datetime-local"
              id="rentStartDate"
              value={rentStartDate}
              onChange={(e) => setRentStartDate(e.target.value)}
              className="form-input"
            />
          </div>

          {/* 반납일 */}
          <div className="form-group">
            <label htmlFor="rentEndDate">반납일</label>
            <input
              type="datetime-local"
              id="rentEndDate"
              value={rentEndDate}
              onChange={(e) => setRentEndDate(e.target.value)}
              className="form-input"
            />
            
          {/* 다시 입력 버튼 */}
          <button type="button" className="reset-button">
            다시 입력
          </button>

          {/* 제출 버튼 */}
          <button type="button"  className="next-button"  onClick={total}>
            다음
          </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RentForm;
