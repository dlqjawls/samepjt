import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ModuleSetList.css";

function ModuleSetList() {
  // 상태 관리
  const [moduleSets, setModuleSets] = useState([]);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 모달 관련 상태
  const [selectedModule, setSelectedModule] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // 페이지 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // API 엔드포인트
  const API_URL = `https://backend-wandering-river-6835.fly.dev/user/module-sets`;

  useEffect(() => {
    fetchModuleSets(currentPage, pageSize);
  }, [currentPage, pageSize]);

  const fetchModuleSets = async (page, size) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(API_URL, {
        params: {
          page: page,
          pageSize: size,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setModuleSets(response.data.data.moduleSets);
        setPagination(response.data.data.pagination);
      } else {
        setError(response.data.message);
        setModuleSets([]);
        setPagination({
          currentPage: 1,
          totalPages: 1,
          totalItems: 0,
          pageSize: size,
        });
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again later.");
      setModuleSets([]);
      setPagination({
        currentPage: 1,
        totalPages: 1,
        totalItems: 0,
        pageSize: size,
      });
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleNextImage = () => {
    if (selectedModule) {
      setCurrentImageIndex((prev) => 
        prev === selectedModule.imgsUrls.length - 1 ? 0 : prev + 1
      );
    }
  };

  const handlePrevImage = () => {
    if (selectedModule) {
      setCurrentImageIndex((prev) => 
        prev === 0 ? selectedModule.imgsUrls.length - 1 : prev - 1
      );
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages) {
      setCurrentPage(newPage);
    }
  };

  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  const handleNextStep = (moduleSet) => {
    // 여기에 다음 단계로 이동하는 로직을 구현하세요
    console.log(selectedModule.suppliedOptions);
    setShowModal(false);
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
                onClick={() => {
                  setSelectedModule(moduleSet);
                  setCurrentImageIndex(0);
                  setShowModal(true);
                }}
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
                  <p className="price">총 비용: ${moduleSet.totalCost}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="pagination-button"
            >
              이전
            </button>
            <span className="page-info">
              {pagination.currentPage} / {pagination.totalPages}
            </span>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === pagination.totalPages}
              className="pagination-button"
            >
              다음
            </button>
            <select
              value={pageSize}
              onChange={handlePageSizeChange}
              className="page-size-select"
            >
              <option value={5}>5개씩</option>
              <option value={10}>10개씩</option>
              <option value={20}>20개씩</option>
            </select>
          </div>
        </>
      )}

      {showModal && selectedModule && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedModule.moduleSetName}</h2>
              <button 
                className="close-button"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="modal-image-container">
                <img
                  src={selectedModule.imgsUrls[currentImageIndex]}
                  alt={`${selectedModule.moduleSetName} - 이미지 ${currentImageIndex + 1}`}
                />
               
              </div>

              <div className="modal-details">
                <div className="description">
                  <h4>상세 설명</h4>
                  <p>{selectedModule.description}</p>
                </div>

                <div className="options">
                  <h4>포함된 옵션</h4>
                  <ul>
                    {selectedModule.suppliedOptions.map((option) => (
                      <li key={option.optionId}>
                        {option.optionName} (수량: {option.quantity})
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="total-cost">
                  <p>총 비용: ${selectedModule.totalCost}</p>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                onClick={() => setShowModal(false)}
                className="cancel-button"
              >
                닫기
              </button>
              <button 
                onClick={() => handleNextStep(selectedModule)}
                className="next-button"
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