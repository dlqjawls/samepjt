// src/components/ModuleSetList.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './ModuleSetList.css'; // 스타일링을 위한 CSS 파일 (선택 사항)

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

  // 페이지 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // API 엔드포인트 (환경 변수 사용 권장)
  const API_URL = `http://localhost:5000/user/module-set/list`;

  useEffect(() => {
    fetchModuleSets(currentPage, pageSize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, pageSize]);

  // 데이터 fetching 함수
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

      if (response.data.resultCode === 'SUCCESS') {
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
      setError('An unexpected error occurred. Please try again later.');
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

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages) {
      setCurrentPage(newPage);
    }
  };

  // 페이지 크기 변경 핸들러
  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1); // 페이지 크기 변경 시 페이지 번호를 1로 초기화
  };

  return (
    <div className="module-set-list">
      <h2>모듈 세트 목록</h2>

      {/* 로딩 상태 */}
      {loading && <div className="loading">Loading...</div>}

      {/* 에러 메시지 */}
      {error && <div className="error-message">{error}</div>}

      {/* 모듈 세트 목록 */}
      {!loading && !error && (
        <>
          <div className="module-sets">
            {moduleSets.length > 0 ? (
              moduleSets.map((moduleSet) => (
                <div key={moduleSet.moduleSetId} className="module-set">
                  <h3>{moduleSet.moduleSetName}</h3>
                  <img
                    src={moduleSet.imgs[0]} // 첫 번째 이미지 사용
                    alt={moduleSet.moduleSetName}
                    className="module-set-image"
                  />
                  <p>{moduleSet.description}</p>
                  <p>총 비용: ${moduleSet.totalCost}</p>
                  <h4>포함된 옵션:</h4>
                  <ul>
                    {moduleSet.suppliedOptions.map((option) => (
                      <li key={option.optionId}>
                        {option.optionName} (수량: {option.quantity})
                      </li>
                    ))}
                  </ul>
                </div>
              ))
            ) : (
              <div>No module sets available.</div>
            )}
          </div>

          {/* 페이지네이션 컨트롤 */}
          <div className="pagination">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              이전
            </button>
            <span>
              {pagination.currentPage} / {pagination.totalPages}
            </span>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === pagination.totalPages}
            >
              다음
            </button>

            {/* 페이지 크기 선택 */}
            <select value={pageSize} onChange={handlePageSizeChange}>
              <option value={5}>5개씩</option>
              <option value={10}>10개씩</option>
              <option value={20}>20개씩</option>
            </select>
          </div>
        </>
      )}
    </div>
  );
}

export default ModuleSetList;
