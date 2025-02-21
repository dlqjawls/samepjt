import React, { useState, useEffect, useRef } from "react"
import "./rentForm.css"
import { useNavigate } from "react-router-dom"
import axios from "axios"

const RentForm = () => {
  const [rentStartDate, setRentStartDate] = useState("")
  const [rentEndDate, setRentEndDate] = useState("")
  const [error, setError] = useState("")
  const [startLocation, setStartLocation] = useState(null)
  const [endLocation, setEndLocation] = useState(null)
  const [startAddress, setStartAddress] = useState("")
  const [endAddress, setEndAddress] = useState("")

  const mapRef = useRef(null)
  const kakaoMap = useRef(null)
  const navigate = useNavigate()
  const geocoder = useRef(null)
  const endMarkerRef = useRef(null)

  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, "0")
    const day = String(date.getDate()).padStart(2, "0")
    const hours = String(date.getHours()).padStart(2, "0")
    const minutes = String(date.getMinutes()).padStart(2, "0")
    return `${year}-${month}-${day}T${hours}:${minutes}:00`
  }

  const setInitialDates = () => {
    const now = new Date()
    now.setMinutes(now.getMinutes() + 5)
    const formattedStartDate = formatDate(now)
    setRentStartDate(formattedStartDate)

    const endDate = new Date(now)
    endDate.setHours(endDate.getHours() + 6)
    const formattedEndDate = formatDate(endDate)
    setRentEndDate(formattedEndDate)
  }

  useEffect(() => {
    const container = mapRef.current
    const options = {
      center: new window.kakao.maps.LatLng(35.20531681938283, 126.81157398442527),
      level: 3,
    }

    const map = new window.kakao.maps.Map(container, options)
    kakaoMap.current = map
    geocoder.current = new window.kakao.maps.services.Geocoder()

    // 마커 이미지 설정
    const startMarkerImage = new window.kakao.maps.MarkerImage("https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/red_b.png", new window.kakao.maps.Size(50, 45), {
      offset: new window.kakao.maps.Point(15, 43),
    })

    const endMarkerImage = new window.kakao.maps.MarkerImage("https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/blue_b.png", new window.kakao.maps.Size(50, 45), {
      offset: new window.kakao.maps.Point(15, 43),
    })

    // 출발지 마커 생성
    const startMarker = new window.kakao.maps.Marker({
      position: options.center,
      map: map,
      image: startMarkerImage,
      title: "출발지",
    })

    // 도착지 마커 생성
    const endMarker = new window.kakao.maps.Marker({
      image: endMarkerImage,
    })
    endMarkerRef.current = endMarker

    // 출발지 정보 설정
    geocoder.current.coord2Address(options.center.getLng(), options.center.getLat(), (result, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        setStartAddress(result[0].address.address_name)
        setStartLocation({ marker: startMarker, latlng: options.center })
      }
    })
    let clickListener = null
    // 지도 클릭 이벤트
    const handleMapClick = (mouseEvent) => {
      const latlng = mouseEvent.latLng

      endMarker.setPosition(latlng)
      endMarker.setMap(map)

      geocoder.current.coord2Address(latlng.getLng(), latlng.getLat(), (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          const addr = result[0].address.address_name
          setEndAddress(addr)
          setEndLocation({ marker: endMarker, latlng })
        }
      })
    }

    if (map && window.kakao && window.kakao.maps) {
      clickListener = window.kakao.maps.event.addListener(map, "click", handleMapClick)
    }

    setInitialDates()

    return () => {
      try {
        if (clickListener) {
          window.kakao.maps.event.removeListener(clickListener)
        }
        if (startMarker) {
          startMarker.setMap(null)
        }
        if (endMarkerRef.current) {
          endMarkerRef.current.setMap(null)
        }
      } catch (error) {
        console.error("Cleanup error:", error)
      }
    }
  }, [])
  // 날짜 유효성 검사
  const validateDates = () => {
    if (!endLocation) {
      setError("도착 위치를 선택해주세요.")
      return false
    }

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
  const preview = () => {
    const selectedOptionData = JSON.parse(sessionStorage.getItem("selectedOptionData") || "{}")
    navigate("/option_select", {
      state: {
        existingOptions: selectedOptionData.selectedOptions || [],
      },
    })
  }
  const handleStartDateChange = (e) => {
    const startDate = new Date(e.target.value)
    setRentStartDate(formatDate(startDate))

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
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/user/rent/calculate-duration-cost`, {
          rentStartDate: rentStartDate,
          rentEndDate: rentEndDate,
        })

        if (response.data.resultCode === "SUCCESS") {
          sessionStorage.setItem(
            "rentDates",
            JSON.stringify({
              startDate: rentStartDate,
              endDate: rentEndDate,
            })
          )
          console.log("Saved rent dates:", JSON.parse(sessionStorage.getItem("rentDates")))

          sessionStorage.setItem("date_Cost", response.data.data.cost)
          navigate("/total_reciept")
        } else {
          setError("비용 계산 중 오류가 발생했습니다.")
        }
      } catch (error) {
        console.error("API 호출 중 오류:", error)
        setError("비용 계산 중 오류가 발생했습니다. 다시 시도해주세요.")
      }
    }
  }

  const handleReset = () => {
    if (endLocation && endLocation.marker) {
      endLocation.marker.setMap(null)
      setEndLocation(null)
    }
    setInitialDates()
    setError("")
  }

  return (
    <div className="rent-form-wrapper-unique">
      <div className="map-container-unique">
        <div ref={mapRef} style={{ width: "100%", height: "400px" }} />
      </div>

      <div className="form-container-unique">
        <div className="form-content-unique">
          <h3 className="form-title-unique">렌트카 대여 설정</h3>
          {error && <div className="error-message-unique">{error}</div>}

          <form>
            <div className="form-group-unique location-group">
              <h4>선택된 위치</h4>
              {startLocation && (
                <div className="location-info-form start">
                  <span>📍 출발지:</span>
                  <p>{startAddress}</p>
                  {/* <p>
                    {startLocation.latlng.getLat().toFixed(6)}, {startLocation.latlng.getLng().toFixed(6)}
                  </p> */}
                </div>
              )}
              {endLocation ? (
                <div className="location-info-form end">
                  <span>🏁 도착지:</span>
                  <p>{endAddress}</p>
                  {/* <p>
                    {endLocation.latlng.getLat().toFixed(6)}, {endLocation.latlng.getLng().toFixed(6)}
                  </p> */}
                </div>
              ) : (
                <p className="location-warning">도착 위치를 지도에서 선택해주세요</p>
              )}
            </div>

            <div className="form-group-unique">
              <label htmlFor="rentStartDate">대여 시작일시</label>
              <input type="datetime-local" id="rentStartDate" value={rentStartDate} onChange={handleStartDateChange} className="form-input-unique" />
            </div>

            <div className="form-group-unique">
              <label htmlFor="rentEndDate">반납 일시</label>
              <input type="datetime-local" id="rentEndDate" value={rentEndDate} onChange={handleEndDateChange} className="form-input-unique" min={rentStartDate} />
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
