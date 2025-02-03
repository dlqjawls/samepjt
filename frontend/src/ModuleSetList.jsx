import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import "./ModuleSetList.css";
import { useNavigate } from "react-router-dom";

function ModuleSetList() {
  const [moduleSets, setModuleSets] = useState([]);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const navigate = useNavigate();
  const API_URL = `https://backend-wandering-river-6835.fly.dev/user/module-sets`;

  const fetchModuleSets = useCallback(
    async (page, size) => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get(API_URL, {
          params: { page, page_size: size },
        });

        if (response.data.resultCode === "SUCCESS") {
          setModuleSets(response.data.data.moduleSets);
          setPagination(response.data.data.pagination);
        } else {
          setError(response.data.message);
          setModuleSets([]);
        }
      } catch (err) {
        setError("An unexpected error occurred. Please try again later.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    },
    [API_URL]
  );

  useEffect(() => {
    fetchModuleSets(pagination.currentPage, pagination.pageSize);
  }, [fetchModuleSets, pagination.currentPage, pagination.pageSize]);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages) {
      setPagination((prev) => ({ ...prev, currentPage: newPage }));
    }
  };

  const handleSelectModule = (module) => {
    setSelectedModule(module);
    setCurrentImageIndex(0);
    setShowModal(true);
  };

  const handleNextStep = () => {
    navigate("/option_select", { state: { selectedModule } });
  };

  return (
    <div className="module-list-container">
      <h2>모듈 세트 목록</h2>

      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">{error}</div>}

      {!loading && !error && (
        <>
          <div className="module-grid">
            {moduleSets.map((moduleSet) => (
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
                  <p className="price">총 비용: ${moduleSet.basePrice}</p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {showModal && selectedModule && (
        <div
          className="module-set-card-modal-overlay"
          onClick={() => setShowModal(false)}
        >
          <div
            className="module-set-card-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="module-set-modal-header">
              <h2>{selectedModule.moduleSetName}</h2>
              <button
                className="modal-close-button "
                onClick={() => setShowModal(false)}
              >
                X 닫기
              </button>
            </div>

            <div className="module-set-modal-body">
              <div className="module-set-modal-image-container">
                <img
                  src={selectedModule.imgUrls[0]}
                  alt={`${selectedModule.moduleSetName} - 이미지 ${
                    currentImageIndex + 1
                  }`}
                />
              </div>

              <div className="modal-details">
                <div className="modal-description">
                  <h4>상세 설명</h4>
                  <p>{selectedModule.description}</p>
                </div>

                <div className="modal-module-options">
                  <h4>포함된 옵션</h4>
                  <ul>
                    {selectedModule.moduleSetOptionTypes.map((option) => (
                      <li key={option.optionTypeId}>
                        {option.optionTypeName} (수량: {option.quantity})
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="modal-total-cost">
                  <h4>총 비용: ${selectedModule.basePrice}</h4>
                </div>
              </div>
            </div>

            <div className="module-set-modal-footer">
              <button
                onClick={handleNextStep}
                className="module-set-next-button"
              >
                다음 단계 →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ModuleSetList;
