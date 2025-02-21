// src/admin/components/RentalRecords.jsx

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import LoadingSpinner from "./LoadingSpinner";
import ModuleInstallVideoModal from "./ModuleInstallVideoModal";
import AutonomousVideoModal from "./AutonomousVideoModal";
import "./RentalRecords.css";

const BASE_URL = import.meta.env.VITE_API_URL;

function RentalRecords() {
  const [rentLogs, setRentLogs] = useState([]);
  const [expandedRentId, setExpandedRentId] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 각 행의 ref들을 저장할 객체
  const rowRefs = useRef({});

  const token = localStorage.getItem("adminToken");

  const [isModuleVideoModalOpen, setIsModuleVideoModalOpen] = useState(false);
  const [isAutonomousVideoModalOpen, setIsAutonomousVideoModalOpen] =
    useState(false);

  // 필터 및 페이지네이션 상태 (필요에 따라 확장 가능)
  const [filters, setFilters] = useState({
    userId: "",
    carId: "",
    page: 1,
    pageSize: 10,
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  const fetchRentLogs = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/rent-history`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          page: filters.page,
          pageSize: filters.pageSize,
          user_pk: filters.userId || undefined,
          vehicle_number: filters.carId || undefined,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setRentLogs(response.data.data.rent_history);
        setPagination(response.data.data.pagination);
        console.log(response.data.data.rent_history);
      } else {
        setError(
          response.data.message || "대여 로그를 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("대여 로그를 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 및 필터 변경 시 대여 로그 목록 조회
  useEffect(() => {
    fetchRentLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const toggleExpanded = (rentId) => {
    setExpandedRentId((prev) => (prev === rentId ? null : rentId));
    // 해당 행으로 스크롤 이동
    setTimeout(() => {
      if (rowRefs.current[rentId]) {
        rowRefs.current[rentId].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  const openModuleVideoModal = (rentId) => {
    setSelectedRecord(rentId);
    setIsModuleVideoModalOpen(true);
  };
  const closeModuleVideoModal = () => setIsModuleVideoModalOpen(false);

  const openAutonomousVideoModal = (rentId) => {
    setSelectedRecord(rentId);
    setIsAutonomousVideoModalOpen(true);
  };
  const closeAutonomousVideoModal = () => setIsAutonomousVideoModalOpen(false);

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  return (
    <div className="rental-container">
      <div className="rental-header">
        <h1>대여 기록 조회</h1>
      </div>

      {/* 대여 로그 목록 테이블 */}
      {error && <p className="error">{error}</p>}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-wrapper">
          <table className="rental-table">
            <thead>
              <tr>
                <th>대여 ID</th>
                <th>사용자 ID</th>
                <th>차량 번호</th>
                <th>옵션 타입</th>
                <th>대여 상태</th>
                <th>등록 일자</th>
              </tr>
            </thead>
            <tbody>
              {rentLogs.length > 0 ? (
                rentLogs.map((log) => (
                  <React.Fragment key={log.rent_id}>
                    <tr
                      ref={(el) => (rowRefs.current[log.rent_id] = el)}
                      className={`main-row ${
                        expandedRentId === log.rent_id
                          ? "expanded-main-row"
                          : ""
                      }`}
                      onClick={() => toggleExpanded(log.rent_id)}
                    >
                      <td>{log.rent_id}</td>
                      <td>
                        <span className="cell-text">{log.user_pk}</span>
                      </td>
                      <td>
                        <span className="cell-text">{log.vehicle_number}</span>
                      </td>
                      <td>
                        <span className="cell-text">{log.option_types}</span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {log.rent_status_name === "in_progress"
                            ? "진행 중"
                            : log.rent_status_name === "completed"
                            ? "완료됨"
                            : log.rent_status_name === "canceled"
                            ? "취소됨"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {new Date(log.created_at).toLocaleString()}
                        </span>
                      </td>
                    </tr>
                    {expandedRentId === log.rent_id && (
                      <tr className="expanded-row">
                        <td colSpan="6">
                          <div className="detail-info-container">
                            <div className="detail-item">
                              <div className="detail-label">대여 ID</div>
                              <div className="detail-value">{log.rent_id}</div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">대여한 사용자</div>
                              <div className="detail-value">{log.user_pk}</div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">
                                대여한 차량 정보
                              </div>
                              <div className="detail-value">
                                {log.vehicle_number}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">
                                대여한 옵션 타입 목록
                              </div>
                              <div className="detail-value">
                                {log.option_types}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">영상</div>
                              <div className="detail-value">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    openModuleVideoModal(log.rent_id);
                                  }}
                                  className="open-video-button"
                                >
                                  모듈 설치 영상
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    openAutonomousVideoModal(log.rent_id);
                                  }}
                                  className="open-video-button"
                                >
                                  자율 주행 영상
                                </button>
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">출발 위치</div>
                              <div className="detail-value">
                                {log.departure_location.x},{" "}
                                {log.departure_location.y}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">도착 위치</div>
                              <div className="detail-value">
                                {log.arrival_location.x},{" "}
                                {log.arrival_location.y}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">대여 요금</div>
                              <div className="detail-value">
                                {Number(log.cost).toLocaleString()}원
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">주행 거리</div>
                              <div className="detail-value">
                                {Number(log.mileage).toLocaleString()} km
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">대여 상태</div>
                              <div className="detail-value">
                                {log.rent_status_name === "in_progress"
                                  ? "진행 중"
                                  : log.rent_status_name === "completed"
                                  ? "완료됨"
                                  : log.rent_status_name === "canceled"
                                  ? "취소됨"
                                  : "알 수 없음"}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">대여 시작 시간</div>
                              <div className="detail-value">
                                {new Date(log.created_at).toLocaleString()}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">최종 업데이트</div>
                              <div className="detail-value">
                                {new Date(log.updated_at).toLocaleString()}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan="7">조회된 대여 로그가 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="pagination">
        <button
          onClick={() => handlePageChange(pagination.currentPage - 1)}
          disabled={pagination.currentPage === 1}
        >
          이전
        </button>
        <span>
          {pagination.currentPage} / {pagination.totalPages}
        </span>
        <button
          onClick={() => handlePageChange(pagination.currentPage + 1)}
          disabled={pagination.currentPage === pagination.totalPages}
        >
          다음
        </button>
      </div>

      {isModuleVideoModalOpen && (
        <ModuleInstallVideoModal
          rentId={selectedRecord}
          onClose={closeModuleVideoModal}
        />
      )}

      {isAutonomousVideoModalOpen && (
        <AutonomousVideoModal
          rentId={selectedRecord}
          onClose={closeAutonomousVideoModal}
        />
      )}
    </div>
  );
}

export default RentalRecords;
