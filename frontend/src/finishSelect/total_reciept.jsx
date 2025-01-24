import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './total_reciept.css';
import axios from 'axios';
const Total_reciept = () => {
    const navigate = useNavigate();
    const body = {
        "selectedOptionTypes": [
          {
            "optionTypeId": 1,
            "quantity": 1
          },
          {
            "optionTypeId": 2,
            "quantity": 1
          }
        ],
        "autonomousArrivalPoint": {
          "x": 12.313,
          "y": 32.3232
        },
        "autonomousDeparturePoint": {
          "x": 11.512,
          "y": 30.4531
        },
        "rentStartDate": "2025-01-15T09:00:00",
        "rentEndDate": "2025-01-20T18:00:00"
      }
    // 세션스토리지에서 데이터 로드
    const [receiptData] = useState(() => {
        const savedOptionData = JSON.parse(sessionStorage.getItem('selectedOptionData') || '{}');
        return {
            // ...기존 데이터...
            selectedOptions: savedOptionData.selectedOptions || []
        };
    });

    const handlePayment = async () => {
        try {
            const token = sessionStorage.getItem('token');
            if (!token) {
                alert('로그인이 필요합니다.');
                return;
            }

            const rentData = {
                selectedOptionTypes: receiptData.selectedOptions,
                autonomousArrivalPoint: {
                    x: 12.313, // 실제 좌표로 변경 필요
                    y: 32.3232
                },
                autonomousDeparturePoint: {
                    x: 11.512,
                    y: 30.4531
                },
                "rentStartDate": "2025-01-15T09:00:00",
  "rentEndDate": "2025-01-20T18:00:00"
            };

            const response = await axios.post(
                'https://backend-wandering-river-6835.fly.dev/user/rent/request',
                rentData,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (response.data.success) {
                alert('결제가 완료되었습니다.');
                sessionStorage.removeItem('selectedOptionData'); // 세션 데이터 삭제
                navigate('/'); // 홈으로 이동
            }
        } catch (error) {
            console.error('결제 처리 중 오류:', error);
            alert('결제 처리 중 오류가 발생했습니다.');
        }
    };
    return (
        // <div className="receipt-container">
        //     <h1 className="receipt-title">최종 명세서</h1>
            
        //     <div className="receipt-section">
        //         <h2>차량 정보</h2>
        //         <p>차량: {receiptData.vehicleInfo.name}</p>
        //         <p>차량번호: {receiptData.vehicleInfo.licensePlate}</p>
        //     </div>

        //     <div className="receipt-section">
        //         <h2>대여 정보</h2>
        //         <p>대여 시작: {receiptData.rentalPeriod.start}</p>
        //         <p>반납 예정: {receiptData.rentalPeriod.end}</p>
        //         <p>픽업 위치: {receiptData.location.pickup}</p>
        //         <p>반납 위치: {receiptData.location.return}</p>
        //     </div>

        //     <div className="receipt-section">
        //         <h2>선택 모듈</h2>
        //         {receiptData.selectedModules.map((module, index) => (
        //             <div key={index} className="item-row">
        //                 <span>{module.name}</span>
        //                 <span>{module.price.toLocaleString()}원</span>
        //             </div>
        //         ))}
        //     </div>

        //     <div className="receipt-section">
        //         <h2>선택 옵션</h2>
        //         {receiptData.selectedOptions.map((option, index) => (
        //             <div key={index} className="item-row">
        //                 <span>{option.name}</span>
        //                 <span>{option.price.toLocaleString()}원</span>
        //             </div>
        //         ))}
        //     </div>

        //     <div className="receipt-section total-section">
        //         <h2>총 결제 금액</h2>
        //         <div className="cost-breakdown">
        //             <p>기본 대여료: {receiptData.costs.baseFee.toLocaleString()}원</p>
        //             <p>모듈 이용료: {receiptData.costs.moduleFee.toLocaleString()}원</p>
        //             <p>옵션 이용료: {receiptData.costs.optionFee.toLocaleString()}원</p>
        //             <p className="total-amount">총 금액: {receiptData.costs.totalAmount.toLocaleString()}원</p>
        //         </div>
        //     </div>

            <div className="button-group">
                <button className="payment-button" onClick={handlePayment}>
                    결제하기
                </button>
            </div>
        // </div>
    );
}

export default Total_reciept;