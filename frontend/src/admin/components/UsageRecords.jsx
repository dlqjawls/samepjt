// src/admin/components/UsageRecords.jsx

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import LoadingSpinner from "./LoadingSpinner";
import "./UsageRecords.css";

const BASE_URL = import.meta.env.VITE_API_URL;

function UsageRecords() {
  const [useLogs, setUseLogs] = useState([]);
  const [expandedRentId, setExpandedRentId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 각 행의 ref들을 저장할 객체
  const rowRefs = useRef({});

  const token = localStorage.getItem("adminToken");

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

  const fetchUseLogs = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/usage-history`, {
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
        setUseLogs(response.data.data.usage_history);
        setPagination(response.data.data.pagination);
        console.log(response.data.data.usage_history);
      } else {
        setError(
          response.data.message || "사용 로그를 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("사용 로그를 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 및 필터 변경 시 대여 로그 목록 조회
  useEffect(() => {
    fetchUseLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const toggleExpanded = (usageId) => {
    setExpandedRentId((prev) => (prev === usageId ? null : usageId));
    // 해당 행으로 스크롤 이동
    setTimeout(() => {
      if (rowRefs.current[usageId]) {
        rowRefs.current[usageId].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  return (
    <div className="usage-container">
      <div className="usage-header">
        <h1>사용 기록 조회</h1>
      </div>

      {/* 대여 로그 목록 테이블 */}
      {error && <p className="error">{error}</p>}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-wrapper">
          <table className="usage-table">
            <thead>
              <tr>
                <th>사용 ID</th>
                <th>대여 ID</th>
                <th>사용된 항목 ID</th>
                <th>항목 유형</th>
                <th>사용 상태</th>
                <th>사용 시작 시간</th>
              </tr>
            </thead>
            <tbody>
              {useLogs.length > 0 ? (
                useLogs.map((log) => (
                  <React.Fragment key={log.rent_id}>
                    <tr
                      ref={(el) => (rowRefs.current[log.usage_id] = el)}
                      className={`main-row ${
                        expandedRentId === log.usage_id
                          ? "expanded-main-row"
                          : ""
                      }`}
                      onClick={() => toggleExpanded(log.usage_id)}
                    >
                      <td>{log.usage_id}</td>
                      <td>
                        <span className="cell-text">{log.rent_id}</span>
                      </td>
                      <td>
                        <span className="cell-text">{log.item_id}</span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {log.item_type_name === "vehicle"
                            ? "차량"
                            : log.item_type_name === "module"
                            ? "모듈"
                            : log.item_type_name === "option"
                            ? "옵션"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {log.usage_status_name === "in_use"
                            ? "사용 중"
                            : log.usage_status_name === "completed"
                            ? "사용 완료"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {new Date(log.created_at).toLocaleString()}
                        </span>
                      </td>
                    </tr>
                    {expandedRentId === log.usage_id && (
                      <tr className="expanded-row">
                        <td colSpan="6">
                          <div className="detail-info-container">
                            <div className="detail-item">
                              <div className="detail-label">사용 ID</div>
                              <div className="detail-value">{log.usage_id}</div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">대여 ID</div>
                              <div className="detail-value">{log.rent_id}</div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">사용된 항목 ID</div>
                              <div className="detail-value">{log.item_id}</div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">항목 유형</div>
                              <div className="detail-value">
                                {log.item_type_name === "vehicle"
                                  ? "차량"
                                  : log.item_type_name === "module"
                                  ? "모듈"
                                  : log.item_type_name === "option"
                                  ? "옵션"
                                  : "알 수 없음"}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">사용 상태</div>
                              <div className="detail-value">
                                {log.usage_status_name === "in_use"
                                  ? "사용 중"
                                  : log.usage_status_name === "completed"
                                  ? "사용 완료"
                                  : "알 수 없음"}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">사용 시작 시간</div>
                              <div className="detail-value">
                                {new Date(log.created_at).toLocaleString()}
                              </div>
                            </div>
                            <div className="detail-item">
                              <div className="detail-label">사용 완료 시간</div>
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
                  <td colSpan="7">조회된 사용 로그가 없습니다.</td>
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
    </div>
  );
}

export default UsageRecords;
