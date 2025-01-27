import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import "./total_reciept.css"
import axios from "axios"

const Total_reciept = () => {
  const navigate = useNavigate()
  const [receiptDetails, setReceiptDetails] = useState({
    options: [],
    totalAmount: 0,
  })

  useEffect(() => {
    const fetchOptionDetails = async () => {
      try {
        const savedOptionData = JSON.parse(sessionStorage.getItem("selectedOptionData") || "{}")

        const response = await axios.get("https://backend-wandering-river-6835.fly.dev/user/option-types", {
          params: {
            page: 1,
            page_size: 30, // 최대 30개 아이템 요청
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
            const fullOption = allOptions.find((opt) => opt.optionTypeId === selectedOption.optionTypeId)
            if (!fullOption) return null

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
  const handlePayment = async () => {
    if (window.confirm("결제를 진행하시겠습니까?")) {
      try {
        const token = sessionStorage.getItem("token")
        if (!token) {
          alert("로그인이 필요합니다.")
          return
        }

        // 옵션 데이터 변환
        const selectedOptions = receiptDetails.options.map((option) => ({
          optionTypeId: option.optionTypeId,
          quantity: option.quantity,
        }))

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
          rentStartDate: "2025-01-15T09:00:00",
          rentEndDate: "2025-01-20T18:00:00",
        }

        const response = await axios.post("https://backend-wandering-river-6835.fly.dev/user/rent/rent", rentData, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (response.data.success) {
          alert("결제가 완료되었습니다.")
          sessionStorage.removeItem("selectedOptionData")
          navigate("/")
        }
      } catch (error) {
        console.error("결제 처리 중 오류:", error)
        alert("결제 처리 중 오류가 발생했습니다.")
      }
    }
  }

  const handleGoBack = () => {
    navigate("/rentForm")
  }

  return (
    <div className="receipt-container">
      <div className="receipt">
        <h2 className="receipt-title">렌트카 옵션 영수증</h2>

        <div className="receipt-header">
          <p>주문 일자: {new Date().toLocaleDateString()}</p>
          <p>주문 번호: {Math.random().toString(36).slice(2)}</p>
        </div>

        <div className="receipt-items">
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
              {receiptDetails.options.map((option) => (
                <tr key={option.optionTypeId}>
                  <td>{option.optionTypeName}</td>
                  <td>{option.quantity}</td>
                  <td>{option.optionTypeCost.toLocaleString()}원</td>
                  <td>{option.totalPrice.toLocaleString()}원</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="receipt-total">
          <p>총 결제 금액: {receiptDetails.totalAmount.toLocaleString()}원</p>
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
