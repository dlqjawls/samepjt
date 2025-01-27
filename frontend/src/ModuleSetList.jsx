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

  return (
    <div className="module-list-layout">
      {/* 왼쪽 슬라이딩 UI */}
      <div className="module-sliding">
        {selectedModule ? (
          <div className="module-details">
            <div className="module-details-image">
              <img
                src={selectedModule.imgsUrls[currentImageIndex]}
                alt={selectedModule.moduleSetName}
              />
            </div>
            <div className="module-details-content">
              <h3>{selectedModule.moduleSetName}</h3>
              <p>{selectedModule.description}</p>
              <p>총 비용: ${selectedModule.basePrice}</p>
            </div>
          </div>
        ) : (
          <p>모듈을 선택하면 상세 정보가 여기에 표시됩니다.</p>
        )}
      </div>

      {/* 오른쪽 모듈 세트 목록 */}
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
                  src={moduleSet.imgsUrls[0]}
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
    </div>
  );
}

export default ModuleSetList;
