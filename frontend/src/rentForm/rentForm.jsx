import React, { useState } from "react"
import "./rentForm.css"
import { useNavigate } from "react-router-dom"

const RentForm = () => {
  const [rentStartDate, setRentStartDate] = useState("")
  const [rentEndDate, setRentEndDate] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  const validateDates = () => {
    const start = new Date(rentStartDate)
    const end = new Date(rentEndDate)
    const now = new Date()

    if (!rentStartDate || !rentEndDate) {
      setError("대여 시작일과 반납일을 모두 선택해주세요.")
      return false
    }

    if (start < now) {
      setError("대여 시작일은 현재 시간 이후여야 합니다.")
      return false
    }

    if (end <= start) {
      setError("반납일은 대여 시작일 이후여야 합니다.")
      return false
    }

    setError("")
    return true
  }

  const handleNext = () => {
    if (validateDates()) {
      sessionStorage.setItem(
        "rentDates",
        JSON.stringify({
          startDate: rentStartDate,
          endDate: rentEndDate,
        })
      )
      navigate("/total_reciept")
    }
  }

  const handleReset = () => {
    setRentStartDate("")
    setRentEndDate("")
    setError("")
  }

  return (
    <div className="rent-form-wrapper">
      {/* 지도 영역 */}
      <div className="map-container">
        <img src="./public/map.png" alt="지도 이미지" className="map-image" />
      </div>

      {/* 폼 영역 */}
      <div className="form-container">
        <div className="form-content">
          <h3 className="form-title">렌트카 대여 설정</h3>
          {error && <div className="error-message">{error}</div>}

          <form>
            <div className="form-group">
              <label htmlFor="rentStartDate">대여 시작일시</label>
              <input
                type="datetime-local"
                id="rentStartDate"
                value={rentStartDate}
                onChange={(e) => setRentStartDate(e.target.value)}
                className="form-input"
                min={new Date().toISOString().slice(0, 16)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="rentEndDate">반납 일시</label>
              <input type="datetime-local" id="rentEndDate" value={rentEndDate} onChange={(e) => setRentEndDate(e.target.value)} className="form-input" min={rentStartDate} />
            </div>
          </form>
        </div>

        <div className="button-group">
          <button type="button" className="reset-button" onClick={handleReset}>
            다시 입력
          </button>
          <button type="button" className="next-button" onClick={handleNext}>
            다음
          </button>
        </div>
      </div>
    </div>
  )
}

export default RentForm
