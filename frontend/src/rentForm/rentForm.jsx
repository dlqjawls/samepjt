import React, { useState, useEffect } from "react"
import "./rentForm.css"
import { useNavigate } from "react-router-dom"
import axios from "axios"

const RentForm = () => {
  const [rentStartDate, setRentStartDate] = useState("")
  const [rentEndDate, setRentEndDate] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  // 날짜 포맷팅 함수
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, "0")
    const day = String(date.getDate()).padStart(2, "0")
    const hours = String(date.getHours()).padStart(2, "0")
    const minutes = String(date.getMinutes()).padStart(2, "0")
    return `${year}-${month}-${day}T${hours}:${minutes}:00`
  }

  // 초기 시간 설정 (현재 시간 + 5분)
  const setInitialDates = () => {
    const now = new Date()
    now.setMinutes(now.getMinutes() + 5)
    const formattedStartDate = formatDate(now)
    setRentStartDate(formattedStartDate)

    // 반납 시간 설정 (시작 시간 + 6시간)
    const endDate = new Date(now)
    endDate.setHours(endDate.getHours() + 6)
    const formattedEndDate = formatDate(endDate)
    setRentEndDate(formattedEndDate)
  }

  useEffect(() => {
    setInitialDates()
  }, [])

  const validateDates = () => {
    const start = new Date(rentStartDate)
    const end = new Date(rentEndDate)
    const now = new Date()
    const minEndTime = new Date(start)
    minEndTime.setHours(minEndTime.getHours() + 6)

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

    if (end < minEndTime) {
      setError("최소 대여 시간은 6시간입니다.")
      return false
    }

    setError("")
    return true
  }

  const handleStartDateChange = (e) => {
    const startDate = new Date(e.target.value)
    setRentStartDate(formatDate(startDate))
    
    // 시작 시간 변경 시 반납 시간도 자동으로 +6시간 설정
    const endDate = new Date(startDate)
    endDate.setHours(endDate.getHours() + 6)
    setRentEndDate(formatDate(endDate))
  }

  const handleEndDateChange = (e) => {
    const endDate = new Date(e.target.value)
    const startDate = new Date(rentStartDate)
    const minEndTime = new Date(startDate)
    minEndTime.setHours(minEndTime.getHours() + 6)

    if (endDate < minEndTime) {
      setError("최소 대여 시간은 6시간입니다.")
      return
    }
    setRentEndDate(formatDate(endDate))
    setError("")
  }

  const handleNext = async () => {
    if (validateDates()) {
      try {
        const response = await axios.post('https://backend-wandering-river-6835.fly.dev/user/rent/calculate-duration-cost', {
          rentStartDate: rentStartDate,
          rentEndDate: rentEndDate
        });
  
        if (response.data.resultCode === 'SUCCESS') {
          sessionStorage.setItem(
            "rentDates",
            JSON.stringify({
              startDate: rentStartDate,
              endDate: rentEndDate,
            })
          );
          sessionStorage.setItem("date_Cost", response.data.data.cost);
          navigate("/total_reciept");
        } else {
          setError('비용 계산 중 오류가 발생했습니다.');
        }
      } catch (error) {
        console.error('API 호출 중 오류:', error);
        setError('비용 계산 중 오류가 발생했습니다. 다시 시도해주세요.');
      }
    }
  }

  const preview = () => {
    const selectedOptionData = JSON.parse(sessionStorage.getItem("selectedOptionData") || "{}")
    navigate("/option_select", {
      state: {
        existingOptions: selectedOptionData.selectedOptions || [],
      },
    })
  }

  const handleReset = () => {
    setInitialDates() // 현재 시간 기준으로 초기화
    setError("")
  }

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
                onChange={handleStartDateChange} 
                className="form-input-unique" 
              />
            </div>

            <div className="form-group-unique">
              <label htmlFor="rentEndDate">반납 일시</label>
              <input
                type="datetime-local"
                id="rentEndDate"
                value={rentEndDate}
                onChange={handleEndDateChange}
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
  )
}

export default RentForm