import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "react-toastify"
import "react-toastify/dist/ReactToastify.css"
import "./total_reciept.css"
import axios from "axios"
import { showConfirmModal } from "./ConfirmModal"

const Total_reciept = () => {
  const navigate = useNavigate()
  const [receiptDetails, setReceiptDetails] = useState({
    options: [],
    totalAmount: 0,
  })
  const [isExpanded, setIsExpanded] = useState(false)
  const [visibleOptions, setVisibleOptions] = useState(5) // 초기에 보여줄 옵션 수
  const toggleShowMore = () => {
    if (isExpanded) {
      setVisibleOptions(5)
    } else {
      setVisibleOptions(receiptDetails.options.length)
    }
    setIsExpanded(!isExpanded)
  }

  useEffect(() => {
    const fetchOptionDetails = async () => {
      try {
        const savedOptionData = JSON.parse(sessionStorage.getItem("selectedOptionData") || "{}")

        const response = await axios.get(`${import.meta.env.VITE_API_URL}/user/option-types`, {
          params: {
            page: 1,
            page_size: 100, // 최대 30개 아이템 요청
          },
        })

        const allOptions = response.data.data.optionTypes
        console.log("전체 옵션:", allOptions)

        if (!savedOptionData.selectedOptions) {
          console.log("선택된 옵션이 없습니다.")
          return
        }

        const matchedOptions = savedOptionData.selectedOptions
          .map((selectedOption) => {
            console.log("현재 처리중인 selectedOption:", selectedOption) // 선택된 옵션 로깅

            const fullOption = allOptions.find((opt) => opt.optionTypeId === selectedOption.optionTypeId)
            console.log("찾은 fullOption:", fullOption) // 매칭된 전체 옵션 로깅

            if (!fullOption) {
              console.log("매칭되지 않은 optionTypeId:", selectedOption.optionTypeId)
              return null
            }

            return {
              ...fullOption,
              quantity: selectedOption.quantity || 1,
              totalPrice: fullOption.optionTypeCost * (selectedOption.quantity || 1),
            }
          })
          .filter(Boolean)

        const total = matchedOptions.reduce((sum, option) => sum + option.totalPrice, 0)

        setReceiptDetails({
          options: matchedOptions,
          totalAmount: total,
        })
      } catch (error) {
        console.error("옵션 정보 조회 중 오류:", error)
        setReceiptDetails({ options: [], totalAmount: 0 })
      }
    }

    fetchOptionDetails()
  }, [])

  const refreshAccessToken = async () => {
    try {
      const refreshToken = sessionStorage.getItem("refreshToken")
      if (!refreshToken) {
        throw new Error("리프레시 토큰이 없습니다.")
      }

      const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh-token`, {
        refresh_token: refreshToken,
      })

      if (response.data.resultCode === "SUCCESS") {
        console.log("토큰 갱신 성공:", response.data)
        const { access_token, refresh_token } = response.data.data
        sessionStorage.setItem("token", access_token)
        sessionStorage.setItem("refreshToken", refresh_token)
        return access_token
      }
      throw new Error("토큰 갱신 실패")
    } catch (error) {
      console.error("토큰 갱신 중 오류:", error)
      toast.error("세션이 만료되었습니다. 다시 로그인해주세요.")
      sessionStorage.clear()
      navigate("/login")
      throw error
    }
  }
  const handlePayment = async () => {
    const confirmPayment = await showConfirmModal()
    if (confirmPayment) {
      try {
        let token = sessionStorage.getItem("token")
        if (!token) {
          toast.error("로그인이 필요합니다.")
          return
        }

        const moduleTypeId = JSON.parse(sessionStorage.getItem("ModuleSet"))
        const selectedOptions = receiptDetails.options.map((option) => ({
          optionTypeId: option.optionTypeId,
          quantity: option.quantity,
        }))

        // 비용 계산을 정확하게 수행
        const module_type_cost = Number(moduleTypeId.moduleTypeCost)
        const option_cost = Number(receiptDetails.totalAmount)
        const date_cost = Number(sessionStorage.getItem("date_Cost"))

        // 서버에서 기대하는 형식으로 total_cost 계산
        const total_cost = module_type_cost + option_cost + date_cost

        const rentData = {
          selectedOptionTypes: selectedOptions,
          autonomousArrivalPoint: {
            x: 12.313,
            y: 32.3232,
          },
          autonomousDeparturePoint: {
            x: 11.512,
            y: 30.4531,
          },
          moduleTypeId: moduleTypeId.moduleTypeId,
          cost: total_cost,
          rentStartDate: JSON.parse(sessionStorage.getItem("rentDates")).startDate,
          rentEndDate: JSON.parse(sessionStorage.getItem("rentDates")).endDate,
        }

        console.log(rentData)
        try {
          const response = await axios.post(`${import.meta.env.VITE_API_URL}/user/rent`, rentData, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })
          if (response.data.resultCode === "SUCCESS") {
            const { rent_id, vehicle_number } = response.data.data
            console.log("예약 완료:", response.data)
            toast.success(`예약이 완료되었습니다!\n예약 번호: ${rent_id}\n차량 번호: ${vehicle_number}`)
            // sessionStorage.removeItem("selectedOptionData");
            sessionStorage.setItem("rent_id", rent_id)

            try {
              const rentresponse = await axios.get(`${import.meta.env.VITE_API_URL}/user/rent/${rent_id}`, {
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              })

              if (rentresponse.data.resultCode === "SUCCESS") {
                console.log("차량 상태 조회 완료:", rentresponse.data)
                sessionStorage.setItem("rentStatus", JSON.stringify(rentresponse.data.data))
                // navigate("/car_status")
                navigate("/loading-status")
              }
            } catch (error) {
              console.error("차량 상태 조회 중 오류:", error)
              toast.error("차량 상태 조회에 실패했습니다.")
            }
          }
        } catch (error) {
          if (error.response && error.response.status === 401) {
            // 토큰이 만료된 경우, 토큰 갱신 시도
            token = await refreshAccessToken()
            // 갱신된 토큰으로 다시 요청
            const response = await axios.post(`${import.meta.env.VITE_API_URL}/user/rent`, rentData, {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            })

            if (response.data.resultCode === "SUCCESS") {
              const { rent_id, vehicle_number } = response.data.data
              toast.success(`예약이 완료되었습니다!\n예약 번호: ${rent_id}\n차량 번호: ${vehicle_number}`)
              sessionStorage.setItem("rent_id", rent_id)

              // 토큰 갱신 후 rentStatus 조회 추가
              try {
                const rentresponse = await axios.get(`${import.meta.env.VITE_API_URL}/user/rent/${rent_id}`, {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                })

                if (rentresponse.data.resultCode === "SUCCESS") {
                  console.log("차량 상태 조회 완료:", rentresponse.data)
                  sessionStorage.setItem("rentStatus", JSON.stringify(rentresponse.data.data))
                  // navigate("/car_status")
                  navigate("/loading-status")
                }
              } catch (error) {
                console.error("차량 상태 조회 중 오류:", error)
                toast.error("차량 상태 조회에 실패했습니다.")
              }
            }
          } else {
            throw error
          }
        }
      } catch (error) {
        console.error("결제 처리 중 오류:", error)
        
        navigate("/loading-status")
        toast.error("차량이 모두 예약중입니다. 다른 시간대를 선택해주세요.")
      }
    }
  }
  const handleGoBack = () => {
    navigate("/rentForm")
  }

  return (
    <div className="receipt-container">
      <div className="receipt">
        <h2 className="receipt-title">모듀카 옵션 영수증</h2>
        <div className="receipt-header">
          <p>
            <span>주문 일자:</span>
            <span>{new Date().toLocaleString()}</span>
          </p>
          <p>
            <span>주문 번호:</span>
            <span>{Math.random().toString(36).slice(2)}</span>
          </p>
          <p>
            <span>시작 기간:</span>
            <span>{new Date(JSON.parse(sessionStorage.getItem("rentDates")).startDate).toLocaleString()}</span>
          </p>
          <p>
            <span>반납 기간:</span>
            <span>{new Date(JSON.parse(sessionStorage.getItem("rentDates")).endDate).toLocaleString()}</span>
          </p>
        </div>

        <div className={`receipt-items ${isExpanded ? "expanded" : ""}`}>
          <table>
            <thead>
              <tr>
                <th>옵션명</th>
                <th>수량</th>
                <th>단가</th>
                <th>금액</th>
              </tr>
            </thead>
            <tbody>
              {receiptDetails.options.slice(0, visibleOptions).map((option) => (
                <tr key={option.optionTypeId}>
                  <td>{option.optionTypeName}</td>
                  <td>{option.quantity}</td>
                  <td>{option.optionTypeCost.toLocaleString()}원</td>
                  <td>{option.totalPrice.toLocaleString()}원</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="receipt-items-gradient"></div>
          {receiptDetails.options.length > 5 && (
            <button className="show-more-button" onClick={toggleShowMore}>
              {isExpanded ? "접기" : "더보기"}({visibleOptions}/{receiptDetails.options.length})
            </button>
          )}
        </div>

        <div className="receipt-total">
          <p>
            <span>차량 금액</span>
            <span>{JSON.parse(sessionStorage.getItem("ModuleSet"))?.moduleTypeCost.toLocaleString()}원</span>
          </p>
          <p>
            <span>옵션 금액</span>
            <span>{receiptDetails.totalAmount.toLocaleString()}원</span>
          </p>
          <p>
            <span>대여 기간 금액</span>
            <span>{Number(sessionStorage.getItem("date_Cost")).toLocaleString()}원</span>
          </p>
          <p>
            <span>총 결제 금액</span>
            <span>{(Number(JSON.parse(sessionStorage.getItem("ModuleSet"))?.moduleTypeCost) + receiptDetails.totalAmount + Number(sessionStorage.getItem("date_Cost"))).toLocaleString()}원</span>
          </p>
        </div>

        <div className="button-group">
          <button className="back-button" onClick={handleGoBack}>
            이전으로
          </button>
          <button className="payment-button" onClick={handlePayment}>
            결제하기
          </button>
        </div>
      </div>
    </div>
  )
}

export default Total_reciept
