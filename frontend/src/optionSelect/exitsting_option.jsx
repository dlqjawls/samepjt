import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import "./exitsting_option.css";

const ExistOptionsPage = () => {
  const location = useLocation();
  const selectedOptions = location.state?.selectedModule.moduleSetOptionTypes || [];
  
  const userdata=location.state;
  const navigate = useNavigate();
  const goToPreviousPage = () => {
    navigate("/ModuleSetList");
  };
  const goToNextPage = () => {
    navigate("/option_select",{ state: userdata });
  };
  const [options, setOptions] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(30);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedOptionIds = selectedOptions.map((option) => option.optionTypeId);

  const fetchOptions = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(
        "https://backend-wandering-river-6835.fly.dev/user/option-types",
        {
          params: {
            page: currentPage,
            page_size: pageSize,
          },
        }
      );

      const { optionTypes, pagination } = response.data.data;

      const filteredOptions = optionTypes.filter((option) =>
        selectedOptionIds.includes(option.optionTypeId)
      );

      const optionsWithQuantity = filteredOptions.map((option) => {
        const selectedOption = selectedOptions.find(
          (selected) => selected.optionTypeId === option.optionTypeId
        );
        console.log(option)
        return {
          ...option,
          selectedQuantity: selectedOption ? selectedOption.quantity : 0,
        };
      });

      setOptions(optionsWithQuantity);
      setTotalPages(pagination.totalPages);
    } catch (err) {
      setError("옵션 목록을 가져오는 중 오류가 발생했습니다.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOptions();
  }, [currentPage, pageSize]);

  return (
    <div className="custom-container">
      <h1 className="custom-title">선택된 옵션 목록</h1>

      {loading ? (
        <div className="loading">로딩 중...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <div className="custom-grid">
          {options.map((option) => (
            <div key={option.optionTypeId} className="custom-row">
              <div className="custom-info">
                <img
                  src={option.imgUrls[0]}
                  alt={option.optionTypeName}
                  className="custom-image"
                />
                <div className="custom-details">
                  <h3>{option.optionTypeName}</h3>
                  <p>{option.description}</p>
                  <p>크기: {option.optionTypeSize}</p>
                </div>
              </div>
              <div className="custom-actions">
                <span className="custom-status">
                  수량: {option.selectedQuantity}
                </span>
                <span className="custom-status">
                  가격: {option.optionTypeCost}원
                </span>
                <span className="custom-status">
                  재고: {option.stockQuantity}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
      <button
        onClick={goToPreviousPage}
        className="custom-next-button"
      >
        이전 페이지로 돌아가기
      </button>
      <button
        onClick={goToNextPage}        
        className="custom-next-button">
        다음 페이지로 이동하기
      </button>


      
    </div>
  );
};

export default ExistOptionsPage;
