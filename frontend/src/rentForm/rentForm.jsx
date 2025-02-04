import React, { useState, useEffect } from "react";
import "./rentForm.css";
import { useNavigate } from "react-router-dom";

const RentForm = () => {
  const [rentStartDate, setRentStartDate] = useState("");
  const [rentEndDate, setRentEndDate] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 15); // 현재 시간에 15분 추가
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}`;
    setRentStartDate(formattedDate);
  }, []);

  const validateDates = () => {
    const start = new Date(rentStartDate);
    const end = new Date(rentEndDate);
    const now = new Date();

    if (!rentStartDate || !rentEndDate) {
      setError("대여 시작일과 반납일을 모두 선택해주세요.");
      return false;
    }

    if (start <= now) {
      setError("대여 시작일은 현재 시간 이후여야 합니다.");
      return false;
    }

    if (end <= start) {
      setError("반납일은 대여 시작일 이후여야 합니다.");
      return false;
    }

    setError("");
    return true;
  };

  const handleNext = () => {
    if (validateDates()) {
      sessionStorage.setItem(
        "rentDates",
        JSON.stringify({
          startDate: rentStartDate,
          endDate: rentEndDate,
        })
      );
      navigate("/total_reciept");
    }
  };

  const preview = () => {
    const selectedOptionData = JSON.parse(sessionStorage.getItem("selectedOptionData") || "{}");
    navigate("/option_select", {
      state: {
        existingOptions: selectedOptionData.selectedOptions || [],
      },
    });
  };

  const handleReset = () => {
    setRentStartDate("");
    setRentEndDate("");
    setError("");
  };

  return (
    <div className="rent-form-wrapper-unique">
      <div className="map-container-unique">
        <img src="./public/map.png" alt="지도 이미지" className="map-image-unique" />
      </div>

      <div className="form-container-unique">
        <div className="form-content-unique">
          <h3 className="form-title-unique">렌트카 대여 설정</h3>
          {error && <div className="error-message-unique">{error}</div>}

          <form>
            <div className="form-group-unique">
              <label htmlFor="rentStartDate">대여 시작일시</label>
              <input
                type="datetime-local"
                id="rentStartDate"
                value={rentStartDate}
                onChange={(e) => setRentStartDate(e.target.value)}
                className="form-input-unique"
              />
            </div>

            <div className="form-group-unique">
              <label htmlFor="rentEndDate">반납 일시</label>
              <input
                type="datetime-local"
                id="rentEndDate"
                value={rentEndDate}
                onChange={(e) => setRentEndDate(e.target.value)}
                className="form-input-unique"
                min={rentStartDate}
              />
            </div>
          </form>
        </div>

        <div className="button-group-unique">
          <button type="button" onClick={preview} className="reset-button-unique">
            이전으로
          </button>
          <button type="button" className="reset-button-unique" onClick={handleReset}>
            다시 입력
          </button>
          <button type="button" className="next-button-unique" onClick={handleNext}>
            다음
          </button>
        </div>
      </div>
    </div>
  );
};

export default RentForm;