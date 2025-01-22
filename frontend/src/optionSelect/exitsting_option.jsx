import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import "./exitsting_option.css";

const CustomOptionListPage = () => {
  const location = useLocation();
  const selectedOptions = location.state?.selectedModule || [];
  const navigate = useNavigate();
  const goToPreviousPage = () => {
    navigate("/ModuleSetList");
  };
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedOption, setSelectedOption] = useState(null);

  const fetchOptions = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(
        "https://backend-wandering-river-6835.fly.dev/user/options"
      );
      setOptions(response.data.data.options);
    } catch (err) {
      setError("옵션 목록을 가져오는 중 오류가 발생했습니다.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOptions();
  }, []);

  const closeModal = () => setSelectedOption(null);

  return (
    <div className="custom-container">
      <h1 className="custom-title">기본 제공 모듈</h1>

      {loading ? (
        <div className="custom-loading">로딩 중...</div>
      ) : error ? (
        <div className="custom-error">{error}</div>
      ) : (
        <div className="custom-grid">
          {options.map((option) => (
            <div key={option.optionId} className="custom-row">
              <div className="custom-info">
                <img
                  src={option.imgUrls[0]}
                  alt={option.optionName}
                  className="custom-image"
                />
                <div className="custom-details">
                  <h3>{option.optionName}</h3>
                  <p>{option.optionCost}원</p>
                </div>
              </div>
              <div className="custom-actions">
                <button
                  className="custom-info-button"
                  onClick={() => setSelectedOption(option)}
                >
                  i
                </button>
                <span className="custom-status">배치완료</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <button onClick={goToPreviousPage} className="custom-next-button">
      &lt; 이전 
      </button>
      <button className="custom-next-button">다음 &gt;</button>

      {selectedOption && (
        <div className="custom-modal-overlay">
          <div className="custom-modal-content">
            <div className="custom-modal-header">
              <h2>{selectedOption.optionName}</h2>
              <button className="custom-close-button" onClick={closeModal}>
                &times;
              </button>
            </div>
            <div className="custom-modal-body">
              <img
                src={selectedOption.imgUrls[0]}
                alt={selectedOption.optionName}
                className="custom-modal-image"
              />
              <p>{selectedOption.description}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomOptionListPage;
