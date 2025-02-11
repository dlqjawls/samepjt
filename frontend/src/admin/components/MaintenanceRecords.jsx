// src/admin/components/MaintenanceRecords.jsx
import React, { useState, useEffect } from "react";
import Modal from "./Modal";
import axios from "axios";
import { MdEdit, MdDelete, MdSearch } from "react-icons/md";
import "./MaintenanceRecords.css";

// (만약 필요하다면, 정비 상태 id와 이름의 매핑을 정의)
const STATUS_MAP = {
  1: "pending",
  2: "in_progress",
  3: "completed",
};

function MaintenanceRecords() {
  // 정비 기록 목록 상태 (API로부터 받아옴)
  const [maintenanceRecords, setMaintenanceRecords] = useState([]);
  // 원본 전체 데이터를 보관 (추가 필터 적용을 위해)
  const [allRecords, setAllRecords] = useState([]);
  // 모달 및 선택된 정비 기록 상태
  const [modalType, setModalType] = useState(null); // 'detail', 'edit', 'delete', 'add'
  const [selectedRecord, setSelectedRecord] = useState(null);
  // 로딩 및 오류 상태
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  // 관리자 인증 토큰
  const token = localStorage.getItem("adminToken");
  // API 베이스 URL
  const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

  // 필터 상태 (API로 전달할 item_type 및 item_id, 나머지는 클라이언트 필터링)
  const [filters, setFilters] = useState({
    // API 전송용: item_type과 item_id
    item_type: "", // 예: "vehicle", "module", "option"
    item_id: "", // 문자열로 입력 (후에 Number 변환 가능)
    // 클라이언트 필터용 추가 필드
    status: "", // "pending", "in_progress", "completed"
    startDate: "",
    endDate: "",
    page: 1,
    pageSize: 10,
  });
  // API에서 전달받은 페이지네이션 정보
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });
  // 폼 데이터 (정비 기록 등록/수정)
  const [formData, setFormData] = useState({
    // 등록 시: item_type, item_id, issue, maintenanceDate, cost, status 등
    item_type: "vehicle", // 기본값
    item_id: "",
    issue: "",
    maintenanceDate: "", // ISO 문자열 (YYYY-MM-DDTHH:mm:ss)
    cost: "",
    status: "pending",
    scheduled_at: "", // 정비 예정 날짜 (등록 시 기본값은 now() 또는 사용자가 입력)
    completed_at: "", // 완료 날짜 (선택)
    // 추가 필드: notes 등 (필요 시)
    notes: "",
  });

  // API 호출: 정비 기록 조회 (GET /admin/maintenance-history)
  // API 명세에 따라 item_type, item_id, page, pageSize 전달
  const fetchMaintenanceRecords = async () => {
    setLoading(true);
    setError("");
    try {
      const params = {
        // API에서는 item_type과 item_id를 필터로 사용
        item_type: filters.item_type || undefined,
        item_id: filters.item_id || undefined,
        page: filters.page,
        pageSize: filters.pageSize,
      };
      const response = await axios.get(
        `${BASE_URL}/admin/maintenance-history`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
          params,
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        // 응답 명세에 따르면 maintenance_history와 pagination이 제공됨
        const records = response.data.data.maintenance_history;
        setAllRecords(records);
        // 클라이언트 단 추가 필터 적용
        applyClientSideFilters(records);
        setPagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "정비 기록을 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록을 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 클라이언트 필터: status, startDate, endDate 적용
  const applyClientSideFilters = (records) => {
    let filtered = [...records];
    if (filters.status) {
      filtered = filtered.filter(
        (record) =>
          STATUS_MAP[record.maintenance_status_id]?.toLowerCase() ===
          filters.status.toLowerCase()
      );
    }
    if (filters.startDate) {
      filtered = filtered.filter(
        (record) => new Date(record.scheduled_at) >= new Date(filters.startDate)
      );
    }
    if (filters.endDate) {
      filtered = filtered.filter(
        (record) => new Date(record.scheduled_at) <= new Date(filters.endDate)
      );
    }
    setMaintenanceRecords(filtered);
  };

  useEffect(() => {
    // 매번 필터 변경 시 전체 데이터에서 클라이언트 필터 적용
    applyClientSideFilters(allRecords);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.status, filters.startDate, filters.endDate]);

  // 필터 변경 핸들러 (입력 필드)
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    // item_type과 item_id는 API 전송용 필터
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      page: 1,
    }));
  };

  // 페이지 변경 핸들러 (백엔드 페이지네이션)
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
      page: newPage,
    }));
  };

  // 폼 데이터 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // 모달 열기 함수들
  const openModal = (type, record = null) => {
    setModalType(type);
    setSelectedRecord(record);
    if (record && type === "detail") {
      // 단순 상세 보기 모달은 별도 폼 데이터 설정 없이 record를 보여줌
    } else if (record && type === "edit") {
      // 수정 모달: API 명세에 따라 수정 가능한 필드는
      // maintenance_status_id (여기서는 status), cost, scheduled_at, completed_at, issue
      setFormData({
        // 기존 데이터에서 필요한 필드 설정 (예시로 issue, cost, scheduled_at, completed_at, status)
        issue: record.issue || "",
        cost: record.cost || "",
        scheduled_at: record.scheduled_at
          ? record.scheduled_at.substring(0, 16)
          : "",
        completed_at: record.completed_at
          ? record.completed_at.substring(0, 16)
          : "",
        status:
          STATUS_MAP[record.maintenance_status_id] ||
          record.status ||
          "pending",
      });
    } else if (type === "add") {
      // 신규 등록 모달: 초기 폼 데이터
      setFormData({
        item_type: "vehicle",
        item_id: "",
        issue: "",
        maintenanceDate: "",
        cost: "",
        status: "pending",
        scheduled_at: "",
        completed_at: "",
        notes: "",
      });
    }
  };

  const closeModal = () => {
    setModalType(null);
    setSelectedRecord(null);
    setFormData({
      item_type: "vehicle",
      item_id: "",
      issue: "",
      maintenanceDate: "",
      cost: "",
      status: "pending",
      scheduled_at: "",
      completed_at: "",
      notes: "",
    });
    setError("");
  };

  // 신규 정비 기록 등록 API 호출 (POST /admin/maintenance-history)
  const handleSaveAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        item_type_name: formData.item_type,
        item_id: Number(formData.item_id),
        issue: formData.issue,
        cost: Number(formData.cost),
        scheduled_at: formData.scheduled_at || new Date().toISOString(),
        completed_at: formData.completed_at || null,
        // status는 기본이 pending (API 명세에서)
      };
      const response = await axios.post(
        `${BASE_URL}/admin/maintenance-history`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchMaintenanceRecords();
        closeModal();
      } else {
        setError(response.data.message || "정비 기록 등록에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록을 등록하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 정비 기록 수정 API 호출 (PATCH /admin/maintenance-history/{maintenance_id})
  const handleSaveEdit = async () => {
    if (!selectedRecord) return;
    // 완료된 정비 기록은 수정 불가 (API 명세에 따라)
    if (STATUS_MAP[selectedRecord.maintenance_status_id] === "completed") {
      alert("완료된 정비 기록은 수정할 수 없습니다.");
      closeModal();
      return;
    }
    setLoading(true);
    setError("");
    try {
      const payload = {
        maintenance_status_id:
          formData.status === "pending"
            ? 1
            : formData.status === "in_progress"
            ? 2
            : formData.status === "completed"
            ? 3
            : 1,
        cost: Number(formData.cost),
        scheduled_at: formData.scheduled_at || null,
        completed_at: formData.completed_at || null,
        issue: formData.issue,
      };
      const response = await axios.patch(
        `${BASE_URL}/admin/maintenance-history/${selectedRecord.maintenance_id}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchMaintenanceRecords();
        closeModal();
      } else {
        setError(response.data.message || "정비 기록 수정에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록을 수정하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 정비 기록 삭제 API 호출 (DELETE /admin/maintenance-history/{maintenance_id})
  const handleConfirmDelete = async () => {
    if (!selectedRecord) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/maintenance-history/${selectedRecord.maintenance_id}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchMaintenanceRecords();
        closeModal();
      } else {
        setError(response.data.message || "정비 기록 삭제에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록을 삭제하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 필터 변경 시 정비 기록을 다시 조회 (API로 item_type과 item_id 전달)
    fetchMaintenanceRecords();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.item_type, filters.item_id, filters.page, filters.pageSize]);

  return (
    <div className="maintenance-container">
      <div className="maintenance-header">
        <h1>정비 기록 관리</h1>
        <button className="add-button" onClick={() => openModal("add")}>
          신규 정비 요청
        </button>
      </div>

      {/* 필터링 섹션 */}
      <div className="filters">
        <label>
          정비 대상 종류
          <select
            name="item_type"
            value={filters.item_type}
            onChange={handleFilterChange}
          >
            <option value="">전체</option>
            <option value="vehicle">차량</option>
            <option value="module">모듈</option>
            <option value="option">옵션</option>
          </select>
        </label>
        <label>
          대상 ID
          <input
            type="text"
            name="item_id"
            value={filters.item_id}
            onChange={handleFilterChange}
            placeholder="대상 ID 입력"
          />
        </label>
        {/* 추가로 클라이언트 필터링할 정비 상태 및 날짜 */}
        <label>
          정비 상태
          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">전체</option>
            <option value="pending">대기 중</option>
            <option value="in_progress">진행 중</option>
            <option value="completed">완료됨</option>
          </select>
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
        <button onClick={() => setFilters({ ...filters })}>검색</button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <>
          <table className="maintenance-table">
            <thead>
              <tr>
                <th>정비 ID</th>
                <th>대상 종류</th>
                <th>대상 ID</th>
                <th>문제</th>
                <th>비용 (원)</th>
                <th>정비 상태</th>
                <th>정비 예정 날짜</th>
                <th>정비 완료 날짜</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
                <th>상세 보기</th>
                <th>수정</th>
                <th>삭제</th>
              </tr>
            </thead>
            <tbody>
              {maintenanceRecords.length > 0 ? (
                maintenanceRecords.map((record) => (
                  <tr key={record.maintenance_id}>
                    <td>{record.maintenance_id}</td>
                    <td>{record.item_type_name}</td>
                    <td>{record.item_id}</td>
                    <td>{record.issue}</td>
                    <td>{record.cost.toLocaleString()}원</td>
                    <td>{STATUS_MAP[record.maintenance_status_id] || "-"}</td>
                    <td>
                      {record.scheduled_at
                        ? new Date(record.scheduled_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      {record.completed_at
                        ? new Date(record.completed_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>{new Date(record.created_at).toLocaleString()}</td>
                    <td>{new Date(record.updated_at).toLocaleString()}</td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => openModal("detail", record)}
                      >
                        <MdSearch />
                      </button>
                    </td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => openModal("edit", record)}
                        disabled={
                          STATUS_MAP[record.maintenance_status_id] ===
                          "completed"
                        }
                        title={
                          STATUS_MAP[record.maintenance_status_id] ===
                          "completed"
                            ? "완료된 정비 기록은 수정할 수 없습니다."
                            : "정비 기록 수정"
                        }
                      >
                        <MdEdit />
                      </button>
                    </td>
                    <td>
                      <button
                        className="delete-button"
                        onClick={() => openModal("delete", record)}
                        disabled={
                          STATUS_MAP[record.maintenance_status_id] ===
                          "completed"
                        }
                        title={
                          STATUS_MAP[record.maintenance_status_id] ===
                          "completed"
                            ? "완료된 정비 기록은 삭제할 수 없습니다."
                            : "정비 기록 삭제"
                        }
                      >
                        <MdDelete />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="13">조회된 정비 기록이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
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

      <Modal isOpen={modalType !== null} onClose={closeModal}>
        {/* 상세 정보 모달 */}
        {modalType === "detail" && selectedRecord && (
          <div className="detail-content">
            <h2>정비 기록 상세 정보</h2>
            <p>
              <strong>정비 ID:</strong> {selectedRecord.maintenance_id}
            </p>
            <p>
              <strong>대상 종류:</strong> {selectedRecord.item_type_name}
            </p>
            <p>
              <strong>대상 ID:</strong> {selectedRecord.item_id}
            </p>
            <p>
              <strong>문제:</strong> {selectedRecord.issue}
            </p>
            <p>
              <strong>비용:</strong> {selectedRecord.cost.toLocaleString()}원
            </p>
            <p>
              <strong>정비 상태:</strong>{" "}
              {STATUS_MAP[selectedRecord.maintenance_status_id] || "-"}
            </p>
            <p>
              <strong>정비 예정 날짜:</strong>{" "}
              {selectedRecord.scheduled_at
                ? new Date(selectedRecord.scheduled_at).toLocaleString()
                : "-"}
            </p>
            <p>
              <strong>정비 완료 날짜:</strong>{" "}
              {selectedRecord.completed_at
                ? new Date(selectedRecord.completed_at).toLocaleString()
                : "-"}
            </p>
            <p>
              <strong>등록 일자:</strong>{" "}
              {new Date(selectedRecord.created_at).toLocaleString()}
            </p>
            <p>
              <strong>수정 일자:</strong>{" "}
              {new Date(selectedRecord.updated_at).toLocaleString()}
            </p>
            <div className="modal-actions">
              <button onClick={closeModal} className="cancel-button">
                닫기
              </button>
            </div>
          </div>
        )}

        {/* 수정 모달 */}
        {modalType === "edit" && selectedRecord && (
          <div className="edit-content">
            <h2>정비 기록 수정</h2>
            <form className="edit-form">
              <label>
                정비 상태:
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleFormChange}
                  disabled={
                    STATUS_MAP[selectedRecord.maintenance_status_id] ===
                    "completed"
                  }
                >
                  <option value="pending">대기 중</option>
                  <option value="in_progress">진행 중</option>
                  <option value="completed">완료됨</option>
                </select>
              </label>
              <label>
                정비 비용 (원):
                <input
                  type="number"
                  name="cost"
                  value={formData.cost}
                  onChange={handleFormChange}
                  disabled={
                    STATUS_MAP[selectedRecord.maintenance_status_id] ===
                    "completed"
                  }
                />
              </label>
              <label>
                정비 예정 날짜:
                <input
                  type="datetime-local"
                  name="scheduled_at"
                  value={formData.scheduled_at}
                  onChange={handleFormChange}
                  disabled={
                    STATUS_MAP[selectedRecord.maintenance_status_id] ===
                    "completed"
                  }
                />
              </label>
              <label>
                정비 완료 날짜:
                <input
                  type="datetime-local"
                  name="completed_at"
                  value={formData.completed_at}
                  onChange={handleFormChange}
                  disabled={
                    STATUS_MAP[selectedRecord.maintenance_status_id] ===
                    "completed"
                  }
                />
              </label>
              <label>
                문제:
                <input
                  type="text"
                  name="issue"
                  value={formData.issue}
                  onChange={handleFormChange}
                  disabled={
                    STATUS_MAP[selectedRecord.maintenance_status_id] ===
                    "completed"
                  }
                />
              </label>
            </form>
            <div className="modal-actions">
              <button
                onClick={handleSaveEdit}
                className="save-button"
                disabled={
                  STATUS_MAP[selectedRecord.maintenance_status_id] ===
                    "completed" || loading
                }
              >
                저장
              </button>
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}

        {/* 삭제 확인 모달 */}
        {modalType === "delete" && selectedRecord && (
          <div className="delete-content">
            <h2>정비 기록 삭제 확인</h2>
            <p>정말로 이 정비 기록을 삭제하시겠습니까?</p>
            <div className="modal-actions">
              <button
                onClick={handleConfirmDelete}
                className="confirm-delete-button"
                disabled={loading}
              >
                삭제
              </button>
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}

        {/* 신규 등록 모달 */}
        {modalType === "add" && (
          <div className="add-content">
            <h2>신규 정비 요청 등록</h2>
            <form className="add-form">
              <label>
                정비 대상 종류:
                <select
                  name="item_type"
                  value={formData.item_type}
                  onChange={handleFormChange}
                  required
                >
                  <option value="vehicle">차량</option>
                  <option value="module">모듈</option>
                  <option value="option">옵션</option>
                </select>
              </label>
              <label>
                대상 ID:
                <input
                  type="text"
                  name="item_id"
                  value={formData.item_id}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                문제:
                <input
                  type="text"
                  name="issue"
                  value={formData.issue}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                정비 예정 날짜:
                <input
                  type="datetime-local"
                  name="scheduled_at"
                  value={formData.scheduled_at}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                정비 비용 (원):
                <input
                  type="number"
                  name="cost"
                  value={formData.cost}
                  onChange={handleFormChange}
                  min="0"
                  required
                />
              </label>
              <label>
                정비 완료 날짜:
                <input
                  type="datetime-local"
                  name="completed_at"
                  value={formData.completed_at}
                  onChange={handleFormChange}
                />
              </label>
            </form>
            <div className="modal-actions">
              <button
                onClick={handleSaveAdd}
                className="save-button"
                disabled={loading}
              >
                등록
              </button>
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default MaintenanceRecords;
