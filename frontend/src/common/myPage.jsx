import React, { useState, useEffect } from "react"
import axios from "axios"
import "./myPage.css"
import { useNavigate } from "react-router-dom"
import { toast } from "react-toastify"
import { FaMapMarkerAlt, FaBatteryThreeQuarters, FaRoute, FaCar } from "react-icons/fa"

const MyPage = () => {
  const navigate = useNavigate()
  const [userInfo, setUserInfo] = useState(null)
  const [activeTab, setActiveTab] = useState("dashboard")
  const [isLoading, setIsLoading] = useState(false)
  const [rentStatus, setRentStatus] = useState(null)
  const [rentHistory, setRentHistory] = useState([])
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
  const fetchRentHistory = async () => {
    try {
      let token = sessionStorage.getItem("token")
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/user/me/rent/history`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.data.resultCode === "SUCCESS") {
        setRentHistory(response.data.data)
      }
    } catch (error) {
      if (error.response?.status === 401) {
        const isRefreshed = await refreshToken()
        if (isRefreshed) {
          return fetchRentHistory()
        }
      }
      console.error("렌트 기록 조회 실패:", error)
    }
  }
  const refreshToken = async () => {
    try {
      const refresh_token = sessionStorage.getItem("refreshToken")
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh-token`, { refresh_token })

      if (response.data.resultCode === "SUCCESS") {
        sessionStorage.setItem("token", response.data.data.access_token)
        sessionStorage.setItem("refreshToken", response.data.data.refresh_token)
        return true
      }
      return false
    } catch (error) {
      console.error("토큰 갱신 실패:", error)
      return false
    }
  }

  const fetchRentStatus = async (token) => {
    const rent_id = sessionStorage.getItem("rent_id")
    if (!rent_id) return

    try {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/user/rent/${rent_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.data.resultCode === "SUCCESS") {
        setRentStatus(response.data.data)
        sessionStorage.setItem("rentStatus", JSON.stringify(response.data.data))
      }
    } catch (error) {
      if (error.response?.status === 401) {
        const isRefreshed = await refreshToken()
        if (isRefreshed) {
          const newToken = sessionStorage.getItem("token")
          return fetchRentStatus(newToken)
        }
      }
      console.error("렌트 상태 조회 실패:", error)
    }
  }

  const fetchUserInfo = async () => {
    try {
      let token = sessionStorage.getItem("token")
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/user/info`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.data.resultCode === "SUCCESS") {
        setUserInfo(response.data.data)
      }
    } catch (error) {
      if (error.response?.status === 401) {
        const isRefreshed = await refreshToken()
        if (isRefreshed) {
          return fetchUserInfo()
        } else {
          toast.error("세션이 만료되었습니다. 다시 로그인해주세요.")
          navigate("/login")
        }
      }
      console.error("사용자 정보 조회 실패:", error)
    }
  }

  const handleCancelRent = async () => {
    try {
      const rent_id = sessionStorage.getItem("rent_id")
      let token = sessionStorage.getItem("token")

      const response = await axios.delete(`${import.meta.env.VITE_API_URL}/user/rent/${rent_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.data.resultCode === "SUCCESS") {
        toast.success("렌트가 성공적으로 취소되었습니다.")
        sessionStorage.removeItem("rentStatus")
        sessionStorage.removeItem("rent_id")
        setRentStatus(null)
        navigate("/")
      }
    } catch (error) {
      toast.error("렌트 취소에 실패했습니다.")
      console.error("렌트 취소 실패:", error)
    }
  }

  const handleCompleteRent = async () => {
    try {
      const rent_id = sessionStorage.getItem("rent_id")
      let token = sessionStorage.getItem("token")

      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/user/rent/${rent_id}/complete`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )

      if (response.data.resultCode === "SUCCESS") {
        toast.success("렌트가 성공적으로 완료되었습니다.")
        sessionStorage.removeItem("rentStatus")
        sessionStorage.removeItem("rent_id")
        setRentStatus(null)
        navigate("/")
      }
    } catch (error) {
      toast.error("렌트 완료에 실패했습니다.")
      console.error("렌트 완료 실패:", error)
    }
  }

  useEffect(() => {
    const token = sessionStorage.getItem("token")
    if (token) {
      // fetchUserInfo()
      fetchRentStatus(token)
      fetchRentHistory()
    }
  }, [])
  const handleProfileUpdate = async (updatedInfo) => {
    try {
      setIsLoading(true)
      let token = sessionStorage.getItem("token")

      const response = await axios.put(`${import.meta.env.VITE_API_URL}/user/info`, updatedInfo, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.data.resultCode === "SUCCESS") {
        toast.success("프로필이 성공적으로 업데이트되었습니다.")
        fetchUserInfo() // 업데이트된 정보 다시 불러오기
      }
    } catch (error) {
      if (error.response?.status === 401) {
        const isRefreshed = await refreshToken()
        if (isRefreshed) {
          return handleProfileUpdate(updatedInfo)
        }
      }
      toast.error("프로필 업데이트에 실패했습니다.")
      console.error("프로필 업데이트 실패:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mypage-container">
      <div className="mypage-header">
        <h1>마이페이지</h1>
        <div className="tab-navigation">
          <button className={`tab-button ${activeTab === "dashboard" ? "active" : ""}`} onClick={() => setActiveTab("dashboard")}>
            대여 기록
          </button>
          <button className={`tab-button ${activeTab === "profile" ? "active" : ""}`} onClick={() => setActiveTab("profile")}>
            프로필 설정
          </button>
        </div>
      </div>

      <div className="mypage-content">
        {isLoading ? (
          <div className="loading">로딩중...</div>
        ) : (
          <>
            {activeTab === "dashboard" && (
              <div className="dashboard-section">
                <h2>현재 대여 현황</h2>
                {rentStatus ? (
                  <div className="vehicle-card">
                    <div className="arrival-status">
                      <span className="arrival-badge">{rentStatus.isArrive ? "도착완료" : "이동중"}</span>
                      <span className="eta-info">예상 도착 시간: {formatTime(rentStatus.ETA)}</span>
                    <div>대여 시작: {currentRent ? formatDate(currentRent.rentStartDate) : "로딩 중..."}</div>
                    <div>대여 종료: {currentRent ? formatDate(currentRent.rentEndDate) : "로딩 중..."}</div>
                    </div>
                    <div className="map-preview">
                      <div className="coordinates">

                        <div>
                          <FaMapMarkerAlt /> 현재 위치:
                          <div>위도: {rentStatus.location?.x}</div>
                          <div>경도: {rentStatus.location?.y}</div>
                        </div>
                        <div>
                          <FaMapMarkerAlt /> 목적지:
                          <div>위도: {rentStatus.destination?.x}</div>
                          <div>경도: {rentStatus.destination?.y}</div>
                        </div>
                      </div>
                    </div>

                    <div className="stats-grid">
                      <div className="stat-item">
                        <div className="stat-label">
                          <FaRoute /> 총 주행거리
                        </div>
                        <div className="stat-value">{(rentStatus.distanceTravelled / 1000).toFixed(3)}km</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-label">
                          <FaBatteryThreeQuarters /> 배터리
                        </div>
                        <div className="stat-value">{rentStatus.status?.vehicle?.batteryLevel}%</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-label">
                          <FaCar /> 추가 이용 요금
                        </div>
                        <div className="stat-value">측정중..</div>
                        {/* <div className="stat-value">{rentStatus.cost?.toLocaleString()}원</div> */}
                      </div>
                    </div>

                    <div className="rental-actions">
                      <button onClick={handleCancelRent} className="cancel-btn">
                        대여 취소
                      </button>
                      <button onClick={handleCompleteRent} className="complete-btn">
                        반납하기
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="no-rental">현재 대여 중인 모듈이 없습니다.</p>
                )}
              </div>
            )}
            {activeTab === "dashboard" && (
              <div className="rental-history-section">
                <h2>대여 이력</h2>
                {rentHistory && rentHistory.length > 0 ? (
                  <div className="history-list">
                    {rentHistory.map((history, index) => (
                      <div key={index} className="history-card">
                        <div className="history-header">
                          <div className="history-number">대여 #{rentHistory.length - index}</div>
                          <span className="history-date">
                            {new Date(history.rentStartDate).toLocaleDateString()}
                            <span className="history-time">
                              {new Date(history.rentStartDate).toLocaleTimeString()} ~{new Date(history.rentEndDate).toLocaleTimeString()}
                            </span>
                          </span>
                        </div>
                        <div className="history-details">
                          <div className="history-item">
                            <FaCar /> 대여 ID: {history.rent_id}
                          </div>
                          <div className="history-item">
                            <FaCar /> 이용 요금: {history.cost?.toLocaleString()}원
                          </div>
                          <div className="history-duration">이용 시간: {Math.round((new Date(history.rentEndDate) - new Date(history.rentStartDate)) / (1000 * 60))}분</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-history">대여 이력이 없습니다.</p>
                )}
              </div>
            )}
            {activeTab === "profile" && (
              <div className="profile-section">
                <h2>프로필 설정</h2>
                {userInfo && (
                  <form
                    className="profile-form"
                  //   onSubmit={(e) => {
                  //     e.preventDefault()
                  //     handleProfileUpdate({
                  //       name: e.target.name.value,
                  //       email: e.target.email.value,
                  //       phone: e.target.phone.value,
                  //     })
                  //   }
                  // }
                  >
                    <div className="form-group">
                      <label>이름</label>
                      <input type="text" name="name" defaultValue={userInfo.name} required />
                    </div>
                    <div className="form-group">
                      <label>이메일</label>
                      <input type="email" name="email" defaultValue={userInfo.email} required />
                    </div>
                    <div className="form-group">
                      <label>전화번호</label>
                      <input type="tel" name="phone" defaultValue={userInfo.phone} required />
                    </div>
                    <button type="submit" className="update-profile-btn" disabled={isLoading}>
                      {isLoading ? "업데이트 중..." : "정보 수정"}
                    </button>
                  </form>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default MyPage
