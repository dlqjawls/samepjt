import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ModuleSetList.css";
import { useNavigate } from "react-router-dom";

function ModuleSetList() {
  const [moduleSets, setModuleSets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const navigate = useNavigate();

  const API_URL = `https://backend-wandering-river-6835.fly.dev/user/module-sets`;

  useEffect(() => {
    fetchModuleSets();
  }, []);

  const fetchModuleSets = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(API_URL);

      if (response.data.resultCode === "SUCCESS") {
        setModuleSets(response.data.data.moduleSets);
        console.log(response)
      } else {
        setError(response.data.message);
        setModuleSets([]);
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again later.");
      setModuleSets([]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectModule = (module) => {
    setSelectedModule(module);
    setCurrentImageIndex(0);
  };

  const handleNextStep = (module) => {
    // 기존 로직 유지: navigate로 state 전달
    navigate("/exist_option", { state: { selectedModule: module } });
  };

  const prepage = () => {
    navigate("/");
  };

  return (
    <div className="module-list-layout">
      {/* 왼쪽: 모듈 세트 목록 */}
      <div className="module-list">
        <h2>모듈 세트 목록</h2>
        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">{error}</div>}
        {!loading &&
          !error &&
          moduleSets.map((moduleSet) => (
            <div
              key={moduleSet.moduleSetId}
              className="module-card"
              onClick={() => handleSelectModule(moduleSet)}
            >
              <div className="module-card-image">
                <img
                  src={moduleSet.imgUrls[0]}
                  alt={moduleSet.moduleSetName}
                />
              </div>
              <div className="module-card-content">
                <h3>{moduleSet.moduleSetName}</h3>
                <p>{moduleSet.description}</p>
              </div>
            </div>
          ))}
      </div>



{/* 오른쪽: 모듈 상세 정보 */}
<div className="module-sliding">
  <button onClick={prepage} className="select-next-button">
    이전페이지로
  </button>
  {selectedModule ? (
    <div className="module-details">
      <div className="module-details-image">
        <img
          src={selectedModule.imgUrls[currentImageIndex]}
          alt={selectedModule.moduleSetName}
        />
      </div>
      <div className="module-details-content">
        <h3>{selectedModule.moduleSetName}</h3>
        <p>{selectedModule.description}</p>
        <h4>포함된 옵션</h4>
        <ul>
          {selectedModule.moduleSetOptionTypes.map((option) => (
            <li key={option.optionTypeId}>
              {option.optionTypeName} (수량: {option.quantity})
            </li>
          ))}
        </ul>
        <p>총 비용: ${selectedModule.basePrice}</p>
        <button
          onClick={() => handleNextStep(selectedModule)}
          className="next-button"
        >
          다음 단계 →
        </button>
      </div>
    </div>
  ) : (
    <p>모듈을 선택하면 상세 정보가 여기에 표시됩니다.</p>
  )}
</div>


    </div>
  );
}

export default ModuleSetList;
