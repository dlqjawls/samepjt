// src/admin/components/RentalRecords.jsx

import React, { useState, useEffect } from "react";
import axios from "axios";
import Modal from "./Modal";
import "./RentalRecords.css";
import { MdVideoLibrary, MdSearch, MdVideocam } from "react-icons/md";

function RentalRecords() {
  /**
   * 초기 더미 데이터 설정
   */
  const initialDummyRentLogs = [
    {
      rent_id: 101,
      user_pk: 3,
      vehicle_number: "PBV-1234",
      option_types: "1,2,3",
      departure_location: { x: 12.313, y: 32.3232 },
      arrival_location: { x: 12.313, y: 32.3232 },
      cost: 150.0,
      mileage: 450.5,
      status: "Completed",
      created_at: "2025-02-01T10:00:00Z",
      updated_at: "2025-02-01T15:00:00Z",
    },
    {
      rent_id: 102,
      user_pk: 5,
      vehicle_number: "PBV-5678",
      option_types: "2,3",
      departure_location: { x: 11.111, y: 33.3333 },
      arrival_location: { x: 11.111, y: 33.3333 },
      cost: 200.0,
      mileage: 500.0,
      status: "In-progress",
      created_at: "2025-02-05T09:00:00Z",
      updated_at: "2025-02-05T12:00:00Z",
    },
  ];

  // 대여 로그 상태: 초기 더미 데이터로 설정 (API 연동 시 제거)
  const [rentLogs, setRentLogs] = useState(initialDummyRentLogs);

  // 모달 관리 상태
  const [modalType, setModalType] = useState(null); // 'detail', 'autonomousVideo', 'moduleVideo'
  const [selectedRentLog, setSelectedRentLog] = useState(null); // 선택된 대여 로그

  // 필터 상태
  const [filters, setFilters] = useState({
    userId: "",
    carId: "",
    startDate: "",
    endDate: "",
    page: 1,
    pageSize: 10,
  });

  // 페이지네이션 상태
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  // 로딩 및 오류 상태
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 관리자 인증 토큰
  const token = localStorage.getItem("adminToken");

  // console.log(token);

  // API 베이스 URL 설정
  const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

  /**
   * 대여 로그 목록 조회 함수
   * 현재는 더미 데이터를 사용하지만, 추후 API 연동 시 수정 필요.
   */
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
        setRentLogs(initialDummyRentLogs);
      }
    } catch (err) {
      console.error(err);
      setError("대여 로그를 불러오는 중 오류가 발생했습니다.");
      setRentLogs(initialDummyRentLogs);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 및 필터 변경 시 대여 로그 목록 조회
  useEffect(() => {
    fetchRentLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 필터 변경 핸들러
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      // 필터가 변경될 때 페이지 번호를 1로 초기화
      ...(["userId", "carId", "startDate", "endDate"].includes(name)
        ? { page: 1 }
        : {}),
    }));
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  // 모달 열기 함수
  const openModal = (type, rentLog = null) => {
    setModalType(type);
    setSelectedRentLog(rentLog);
  };

  // 모달 닫기 함수
  const closeModal = () => {
    setModalType(null);
    setSelectedRentLog(null);
    setError("");
  };

  return (
    <div className="rental-container">
      <div className="rental-header">
        <h1>대여 로그 조회</h1>
      </div>

      {/* 필터링 섹션 */}
      {/* <div className="filters">
        <label>
          사용자 ID
          <input
            type="text"
            name="userId"
            value={filters.userId}
            onChange={handleFilterChange}
            placeholder="사용자 ID 입력"
          />
        </label>
        <label>
          차량 ID/번호
          <input
            type="text"
            name="carId"
            value={filters.carId}
            onChange={handleFilterChange}
            placeholder="차량 ID 또는 번호 입력"
          />
        </label>
        <label>
          시작 날짜
          <input
            type="date"
            name="startDate"
            value={filters.startDate}
            onChange={handleFilterChange}
          />
        </label>
        <label>
          종료 날짜
          <input
            type="date"
            name="endDate"
            value={filters.endDate}
            onChange={handleFilterChange}
          />
        </label>
        <button onClick={fetchRentLogs}>검색</button>
      </div> */}

      {/* 대여 로그 목록 테이블 */}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <>
          {error && <p className="error">{error}</p>}
          <div className="rental-wrapper">
            <table className="rental-table">
              <thead>
                <tr>
                  <th>대여 ID</th>
                  <th>사용자 ID</th>
                  <th>차량 번호</th>
                  <th>옵션 타입</th>
                  <th>출발 위치 (x, y)</th>
                  <th>도착 위치 (x, y)</th>
                  <th>대여 비용 (원)</th>
                  <th>주행 거리 (km)</th>
                  <th>대여 상태</th>
                  <th>등록 일자</th>
                  <th>상세 보기</th>
                </tr>
              </thead>
              <tbody>
                {rentLogs.length > 0 ? (
                  rentLogs.map((log) => (
                    <tr key={log.rent_id}>
                      <td>{log.rent_id}</td>
                      <td>{log.user_pk}</td>
                      <td>{log.vehicle_number}</td>
                      <td>{log.option_types}</td>
                      <td>
                        {log.departure_location.x}, {log.departure_location.y}
                      </td>
                      <td>
                        {log.arrival_location.x}, {log.arrival_location.y}
                      </td>
                      <td>{Number(log.cost).toLocaleString()}원</td>
                      <td>{Number(log.mileage).toLocaleString()} km</td>
                      <td>
                        <span
                          className={`status-badge ${
                            log.status === "in_progress"
                              ? "status-in-progress"
                              : log.status === "completed"
                              ? "status-completed"
                              : log.status === "canceled"
                              ? "status-canceled"
                              : "status-unknown"
                          }`}
                        >
                          {log.status === "in_progress"
                            ? "진행 중"
                            : log.status === "completed"
                            ? "완료됨"
                            : log.status === "canceled"
                            ? "취소됨"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>{new Date(log.created_at).toLocaleString()}</td>
                      <td>
                        <button
                          className="detail-button"
                          onClick={() => openModal("detail", log)}
                        >
                          <MdSearch />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="11">조회된 대여 로그가 없습니다.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* 페이지네이션 */}
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
        </>
      )}

      {/* 모달 */}
      <Modal isOpen={modalType !== null} onClose={closeModal}>
        {/* 상세 정보 모달 */}
        {modalType === "detail" && selectedRentLog && (
          <div className="detail-content">
            <h2>대여 로그 상세 정보</h2>
            <p>
              <strong>대여 ID:</strong> {selectedRentLog.rent_id}
            </p>
            <p>
              <strong>사용자 ID:</strong> {selectedRentLog.user_pk}
            </p>
            <p>
              <strong>차량 번호:</strong> {selectedRentLog.vehicle_number}
            </p>
            <p>
              <strong>옵션 타입:</strong> {selectedRentLog.option_types}
            </p>
            <p>
              <strong>출발 위치:</strong> {selectedRentLog.departure_location.x}
              , {selectedRentLog.departure_location.y}
            </p>
            <p>
              <strong>도착 위치:</strong> {selectedRentLog.arrival_location.x},{" "}
              {selectedRentLog.arrival_location.y}
            </p>
            <p>
              <strong>대여 비용:</strong>{" "}
              {Number(selectedRentLog.cost).toLocaleString()}원
            </p>
            <p>
              <strong>주행 거리:</strong>{" "}
              {Number(selectedRentLog.mileage).toLocaleString()} km
            </p>
            <p>
              <strong>대여 상태:</strong>{" "}
              {selectedRentLog.status === "in_progress"
                ? "진행 중"
                : selectedRentLog.status === "completed"
                ? "완료됨"
                : selectedRentLog.status === "canceled"
                ? "취소됨"
                : "알 수 없음"}
            </p>
            <p>
              <strong>등록 일자:</strong>{" "}
              {new Date(selectedRentLog.created_at).toLocaleString()}
            </p>
            <p>
              <strong>최종 업데이트:</strong>{" "}
              {new Date(selectedRentLog.updated_at).toLocaleString()}
            </p>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default RentalRecords;
