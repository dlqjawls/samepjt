// src/admin/components/MaintenanceRecords.jsx

import React, { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import AddModal from "./AddModal";
import DeleteModal from "./DeleteModal";
import LoadingSpinner from "./LoadingSpinner";
import { MdEdit, MdDelete } from "react-icons/md";
import "./MaintenanceRecords.css";

const BASE_URL = import.meta.env.VITE_API_URL;

const MaintenanceRecords = () => {
  const token = localStorage.getItem("adminToken");

  const [records, setRecords] = useState([]);
  const [expandedRecordId, setExpandedRecordId] = useState(null);
  const [editingRecordId, setEditingRecordId] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  // 각 행의 ref들을 저장할 객체
  const rowRefs = useRef({});

  const detailInfoRef = useRef(null);

  const [formData, setFormData] = useState({
    item_type_name: "",
    item_id: 0,
    issue: "",
    cost: 0,
    scheduled_at: "",
    completed_at: "",
    maintenance_status_id: "",
  });

  const [filters, setFilters] = useState({
    itemType: "vehicle",
    itemId: 0,
    page: 1,
    pageSize: 10,
  });

  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  const [maintenanceStatuses, setMaintenanceStatuses] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchMaintenanceRecords = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(
        `${BASE_URL}/admin/maintenance-history`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          params: {
            ...filters,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        setRecords(response.data.data.maintenance_history);
        setPagination(response.data.data.pagination);
      } else {
        setError("정비 기록을 불러오는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록을 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }, [filters, token]);

  useEffect(() => {
    fetchMaintenanceRecords();
  }, [fetchMaintenanceRecords]);

  // 정비 상태 목록 조회
  const fetchMaintenanceStatuses = useCallback(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/admin/maintenance-status`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        setMaintenanceStatuses(response.data.data.maintenance_statuses);
      } else {
        console.error("정비 상태 목록 조회 실패:", response.data.message);
      }
    } catch (err) {
      console.error("정비 상태 목록 조회 중 오류:", err);
    }
  }, [token]);

  useEffect(() => {
    fetchMaintenanceStatuses();
  }, [fetchMaintenanceStatuses]);

  // 정비 예정 날짜 기본값 (현재 시각 + 1시간)
  useEffect(() => {
    const now = new Date();
    now.setHours(now.getHours() + 1);
    const localISOTime = now.toISOString().slice(0, 16);
    setFormData((prev) => ({ ...prev, scheduled_at: localISOTime }));
  }, []);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
      page: newPage,
    }));
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // 행 토글 (확장/축소)
  const toggleExpanded = (recordId) => {
    setExpandedRecordId((prev) => (prev === recordId ? null : recordId));
    setEditingRecordId(null);
    // 해당 행으로 스크롤 이동
    setTimeout(() => {
      if (rowRefs.current[recordId]) {
        rowRefs.current[recordId].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  const openAddModal = () => {
    const now = new Date();
    now.setHours(now.getHours() + 1);
    const localISOTime = now.toISOString().slice(0, 16);

    setFormData({
      item_type_name: "vehicle",
      item_id: 0,
      issue: "",
      cost: 0,
      scheduled_at: localISOTime,
      completed_at: "",
      maintenance_status_id: "",
    });
    setIsAddModalOpen(true);
  };
  const closeAddModal = () => setIsAddModalOpen(false);

  // 신규 정비 기록 등록 API 호출
  const handleSubmitAdd = async () => {
    if (
      !formData.item_type_name.trim() ||
      !formData.item_id ||
      !formData.issue.trim() ||
      !formData.cost ||
      !formData.scheduled_at
    ) {
      alert("필수 필드를 모두 입력하세요.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const payload = { ...formData };
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
        await fetchMaintenanceRecords();
        closeAddModal();
      } else {
        setError(response.data.message || "정비 기록 등록 실패");
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록 등록 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 인라인 수정 모드 전환
  const startEditing = (record) => {
    setSelectedRecord(record);
    setFormData({
      maintenance_status_id: record.maintenance_status_id
        ? record.maintenance_status_id.toString()
        : "",
      cost: record.cost,
      scheduled_at: record.scheduled_at
        ? new Date(record.scheduled_at).toISOString().slice(0, 16)
        : "",
      completed_at: record.completed_at
        ? new Date(record.completed_at).toISOString().slice(0, 16)
        : "",
      issue: record.issue,
    });
    setEditingRecordId(record.maintenance_id);
    setTimeout(() => {
      if (detailInfoRef.current) {
        detailInfoRef.current.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100); // 약간의 딜레이 후 스크롤 호출
  };

  // 인라인 수정 API 호출
  const handleSubmitEdit = async (recordId) => {
    setLoading(true);
    setError("");
    try {
      const payload = { ...formData };
      const response = await axios.patch(
        `${BASE_URL}/admin/maintenance-history/${recordId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchMaintenanceRecords();
        setEditingRecordId(null);
      } else {
        setError(response.data.message || "정비 기록 수정 실패");
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록 수정 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const cancelEditing = () => {
    setEditingRecordId(null);
  };

  // 삭제 모달 열기/닫기
  const openDeleteModal = (record) => {
    setSelectedRecord(record);
    setIsDeleteModalOpen(true);
  };
  const closeDeleteModal = () => setIsDeleteModalOpen(false);

  // 삭제 API 호출
  const handleSubmitDelete = async (recordId) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/maintenance-history/${recordId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchMaintenanceRecords();
        closeDeleteModal();
      } else {
        setError(response.data.message || "정비 기록 삭제 실패");
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록 삭제 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="maintenance-records">
      <div className="maintenance-header">
        <h1>정비 기록 관리</h1>
        <button className="add-button" onClick={openAddModal}>
          정비 기록 등록
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-wrapper">
          <table className="maintenance-table">
            <thead>
              <tr>
                <th>정비 기록 ID</th>
                <th>항목 유형</th>
                <th>문제</th>
                <th>비용</th>
                <th>정비 상태</th>
                <th>등록 일자</th>
              </tr>
            </thead>
            <tbody>
              {records.length > 0 ? (
                records.map((record) => (
                  <React.Fragment key={record.maintenance_id}>
                    <tr
                      ref={(el) =>
                        (rowRefs.current[record.maintenance_id] = el)
                      }
                      className={`main-row ${
                        expandedRecordId === record.maintenance_id
                          ? "expanded-main-row"
                          : ""
                      }`}
                      onClick={() => toggleExpanded(record.maintenance_id)}
                    >
                      <td>{record.maintenance_id}</td>
                      <td>
                        <span className="cell-text">
                          {record.item_type_name === "vehicle"
                            ? "차량"
                            : record.item_type_name === "module"
                            ? "모듈"
                            : record.item_type_name === "option"
                            ? "옵션"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">{record.issue}</span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {record.cost.toLocaleString()}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {record.maintenance_status_name === "pending"
                            ? "대기"
                            : record.maintenance_status_name === "in_progress"
                            ? "진행 중"
                            : record.maintenance_status_name === "completed"
                            ? "완료"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {new Date(record.created_at).toLocaleString()}
                        </span>
                      </td>
                    </tr>
                    {expandedRecordId === record.maintenance_id && (
                      <tr className="expanded-row">
                        <td colSpan="6">
                          <div
                            className="detail-info-container"
                            ref={detailInfoRef}
                          >
                            <div className="detail-info">
                              <div className="detail-item">
                                <div className="detail-label">정비 기록 ID</div>
                                <div className="detail-value">
                                  {record.maintenance_id}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">항목 유형</div>
                                {editingRecordId === record.maintenance_id ? (
                                  <select
                                    name="item_type_name"
                                    value={formData.item_type_name}
                                    onChange={handleFormChange}
                                    className="edit-input edit-item-type-name"
                                  >
                                    <option value="vehicle">vehicle</option>
                                    <option value="module">module</option>
                                    <option value="option">option</option>
                                  </select>
                                ) : (
                                  <div className="detail-value">
                                    {record.item_type_name === "vehicle"
                                      ? "차량"
                                      : record.item_type_name === "module"
                                      ? "모듈"
                                      : record.item_type_name === "option"
                                      ? "옵션"
                                      : "알 수 없음"}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  정비 대상의 고유 ID
                                </div>
                                <div className="detail-value">
                                  {record.item_id}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">문제</div>
                                {editingRecordId === record.maintenance_id ? (
                                  <input
                                    type="text"
                                    name="issue"
                                    value={formData.issue}
                                    onChange={handleFormChange}
                                    className="edit-input edit-issue"
                                  />
                                ) : (
                                  <div className="detail-value edit-issue">
                                    {record.issue}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">비용</div>
                                {editingRecordId === record.maintenance_id ? (
                                  <input
                                    type="number"
                                    name="cost"
                                    value={formData.cost}
                                    onChange={handleFormChange}
                                    className="edit-input edit-cost"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {record.cost.toLocaleString()}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">정비 상태</div>
                                {editingRecordId === record.maintenance_id ? (
                                  <select
                                    name="maintenance_status_id"
                                    value={formData.maintenance_status_id}
                                    onChange={handleFormChange}
                                    className="edit-input edit-maintenance-status-id"
                                  >
                                    <option value="">선택하세요</option>
                                    {maintenanceStatuses.map((ms) => (
                                      <option
                                        key={ms.maintenance_status_id}
                                        value={ms.maintenance_status_id}
                                      >
                                        {ms.maintenance_status_name ===
                                        "pending"
                                          ? "대기"
                                          : ms.maintenance_status_name ===
                                            "in_progress"
                                          ? "진행 중"
                                          : ms.maintenance_status_name ===
                                            "completed"
                                          ? "완료"
                                          : "알 수 없음"}
                                      </option>
                                    ))}
                                  </select>
                                ) : (
                                  <div className="detail-value">
                                    {record.maintenance_status_name ===
                                    "pending"
                                      ? "대기"
                                      : record.maintenance_status_name ===
                                        "in_progress"
                                      ? "진행 중"
                                      : record.maintenance_status_name ===
                                        "completed"
                                      ? "완료"
                                      : "알 수 없음"}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  정비 예정 날짜
                                </div>
                                {editingRecordId === record.maintenance_id ? (
                                  <input
                                    type="datetime-local"
                                    name="scheduled_at"
                                    value={formData.scheduled_at}
                                    onChange={handleFormChange}
                                    className="edit-input edit-scheduled-at"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {new Date(
                                      record.scheduled_at
                                    ).toLocaleString()}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  정비 완료 날짜
                                </div>
                                {editingRecordId === record.maintenance_id ? (
                                  <input
                                    type="datetime-local"
                                    name="completed_at"
                                    value={formData.completed_at}
                                    onChange={handleFormChange}
                                    className="edit-input edit-completed-at"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {new Date(
                                      record.completed_at
                                    ).toLocaleString()}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">고유 ID</div>
                                <div className="detail-value">
                                  {record.item_id}
                                </div>
                              </div>
                            </div>
                            <div className="detail-actions">
                              {editingRecordId === record.maintenance_id ? (
                                <>
                                  <button
                                    className="detail-save-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleSubmitEdit(record.maintenance_id);
                                    }}
                                  >
                                    저장
                                  </button>
                                  <button
                                    className="detail-cancel-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      cancelEditing();
                                    }}
                                  >
                                    취소
                                  </button>
                                </>
                              ) : (
                                <>
                                  <button
                                    className="detail-edit-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      startEditing(record);
                                    }}
                                  >
                                    <MdEdit />
                                  </button>
                                  <button
                                    className="detail-delete-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      openDeleteModal(record);
                                    }}
                                  >
                                    <MdDelete />
                                  </button>
                                </>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan="7">조회된 정비 기록이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="pagination">
        <button
          onClick={() => handlePageChange(filters.page - 1)}
          disabled={filters.page === 1}
        >
          이전
        </button>
        <span>
          {filters.page} / {pagination.totalPages}
        </span>
        <button
          onClick={() => handlePageChange(filters.page + 1)}
          disabled={filters.page === pagination.totalPages}
        >
          다음
        </button>
      </div>

      {isAddModalOpen && (
        <AddModal
          isOpen={isAddModalOpen}
          onClose={closeAddModal}
          onSubmit={handleSubmitAdd}
          title="신규 정비 기록 등록"
        >
          <div className="form-group">
            <label>정비 대상</label>
            <select
              name="item_type_name"
              className="add-item-type-name"
              value={formData.item_type_name}
              onChange={handleFormChange}
              required
            >
              <option value="vehicle">vehicle</option>
              <option value="module">module</option>
              <option value="option">option</option>
            </select>
          </div>
          <div className="form-group">
            <label>정비 대상의 고유 ID</label>
            <input
              type="number"
              name="item_id"
              className="add-item-id"
              value={formData.item_id}
              onChange={handleFormChange}
              placeholder="정비 대상의 고유 ID"
            />
          </div>
          <div className="form-group">
            <label>문제</label>
            <input
              type="text"
              name="issue"
              className="add-issue"
              value={formData.issue}
              onChange={handleFormChange}
            />
          </div>
          <div className="form-group">
            <label>비용</label>
            <input
              type="number"
              name="cost"
              className="add-cost"
              value={formData.cost}
              onChange={handleFormChange}
            />
          </div>
          <div className="form-group">
            <label>정비 예정 날짜</label>
            <input
              type="datetime-local"
              name="scheduled_at"
              className="add-scheduled-at"
              value={formData.scheduled_at}
              onChange={handleFormChange}
            />
          </div>
          <div className="form-group">
            <label>정비 완료 날짜</label>
            <input
              type="datetime-local"
              name="completed_at"
              className="add-completed-at"
              value={formData.completed_at}
              onChange={handleFormChange}
            />
          </div>
        </AddModal>
      )}

      {isDeleteModalOpen && selectedRecord && (
        <DeleteModal
          isOpen={isDeleteModalOpen}
          onClose={closeDeleteModal}
          onDelete={() => handleSubmitDelete(selectedRecord.maintenance_id)}
          title="정비 기록 삭제 확인"
          message={
            selectedRecord
              ? `${selectedRecord.item_type_name} 정비 기록을 삭제하시겠습니까?`
              : ""
          }
        />
      )}
    </div>
  );
};

export default MaintenanceRecords;
