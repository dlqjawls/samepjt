import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const OptionSelect = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const selectedOptions = location.state?.selectedModule.moduleSetOptionTypes || [];
  const userdata = location.state;
  console.log(userdata)
  const [options, setOptions] = useState(selectedOptions);

  // 수량 증가
  const handleIncrease = (index) => {
    const updatedOptions = [...options];
    updatedOptions[index].quantity += 1;
    setOptions(updatedOptions);
  };

  // 수량 감소
  const handleDecrease = (index) => {
    const updatedOptions = [...options];
    if (updatedOptions[index].quantity > 0) {
      updatedOptions[index].quantity -= 1;
      setOptions(updatedOptions);
    }
  };

  // 이전 페이지로 이동
  const goToPreviousPage = () => {
    navigate("/exist_option", { state: userdata });
  };

  // 다음 페이지로 이동
  const goToNextPage = () => {
    navigate("/summary", { state: { ...userdata, updatedOptions: options } });
  };

  return (
    <div className="option-select-container">
      <h1>옵션 선택</h1>
      <div className="option-list">
        {options.map((option, index) => (
          <div key={option.optionTypeId} className="option-item">
            <span className="option-name">{option.optionTypeName}</span>
            <div className="quantity-controls">
              <button onClick={() => handleDecrease(index)}>-</button>
              <span>{option.quantity}</span>
              <button onClick={() => handleIncrease(index)}>+</button>
            </div>
          </div>
        ))}
      </div>
      <div className="navigation-buttons">
        <button onClick={goToPreviousPage}>이전</button>
        <button onClick={goToNextPage}>다음</button>
      </div>
    </div>
  );
};

export default OptionSelect;
