// src/admin/components/MaintenanceRecords.jsx
import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import Modal from "./Modal";
import { MdSearch, MdEdit, MdDelete } from "react-icons/md";
import "./MaintenanceRecords.css";

const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

const MaintenanceRecords = () => {
  const token = localStorage.getItem("adminToken");

  // State to manage the maintenance records, pagination, and error/loading
  const [maintenanceRecords, setMaintenanceRecords] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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

  const [modalContentType, setModalContentType] = useState("detail");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedMaintenanceRecord, setSelectedMaintenanceRecord] =
    useState(null);
  const [formData, setFormData] = useState({
    item_type_name: "",
    item_id: 0,
    issue: "",
    cost: 0,
    scheduled_at: "",
    completed_at: "",
  });

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
        setMaintenanceRecords(response.data.data.maintenance_history);
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

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      page: 1,
    }));
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

  const openAddModal = () => {
    // Initialize form data for adding a new record
    setFormData({
      item_type_name: "",
      item_id: 0,
      issue: "",
      cost: 0,
      scheduled_at: "",
      completed_at: "",
      maintenance_status_id: 1,
    });
    setModalContentType("add"); // Set to "add" instead of "edit"
    setIsModalOpen(true);
  };

  const openDetailModal = (record) => {
    setSelectedMaintenanceRecord(record);
    setModalContentType("detail");
    setIsModalOpen(true);
  };

  // The openEditModal function remains for editing existing records
  const openEditModal = (record) => {
    setSelectedMaintenanceRecord(record);
    setFormData({
      maintenance_status_id: record.maintenance_status_id || 1,
      cost: record.cost || 0,
      scheduled_at: record.scheduled_at || "",
      completed_at: record.completed_at || "",
      issue: record.issue || "",
    });
    setModalContentType("edit"); // Set to "edit" when modifying an existing record
    setIsModalOpen(true);
  };

  const openDeleteModal = (record) => {
    setSelectedMaintenanceRecord(record);
    setModalContentType("delete");
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedMaintenanceRecord(null);
    setModalContentType(null);
    setIsModalOpen(false);
  };

  const handleSaveEdit = async () => {
    setLoading(true);
    setError("");

    const payload = {
      item_type_name: formData.item_type_name,
      item_id: formData.item_id,
      maintenance_status_id: formData.maintenance_status_id,
      cost: formData.cost,
      scheduled_at: formData.scheduled_at,
      completed_at: formData.completed_at,
      issue: formData.issue,
    };

    try {
      let response;
      if (modalContentType === "add") {
        // Handle adding a new record
        response = await axios.post(
          `${BASE_URL}/admin/maintenance-history`,
          payload,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
      } else if (modalContentType === "edit" && selectedMaintenanceRecord) {
        // Handle editing an existing record
        response = await axios.patch(
          `${BASE_URL}/admin/maintenance-history/${selectedMaintenanceRecord.maintenance_id}`,
          payload,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
      }

      if (response.data.resultCode === "SUCCESS") {
        fetchMaintenanceRecords(); // Refresh the records list
        closeModal(); // Close the modal
      } else {
        setError("정비 기록 저장에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("정비 기록 저장 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedMaintenanceRecord) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/maintenance-history/${selectedMaintenanceRecord.maintenance_id}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      console.log(response);

      if (response.data.resultCode === "SUCCESS") {
        fetchMaintenanceRecords();
        closeModal();
      } else {
        setError("정비 기록 삭제에 실패했습니다.");
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

      <div className="filters">
        <label>
          항목 유형:
          <select
            name="itemType"
            value={filters.itemType}
            onChange={handleFilterChange}
          >
            <option value="vehicle">차량</option>
            <option value="module">모듈</option>
            <option value="option">옵션</option>
          </select>
        </label>
        <label>
          항목 ID:
          <input
            type="number"
            name="itemId"
            value={filters.itemId}
            onChange={handleFilterChange}
          />
        </label>
        <button onClick={() => setFilters({ ...filters })}>검색</button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>로딩 중...</p>
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
                    <td>{record.issue}</td>
                    <td>{record.cost.toLocaleString()}</td>
                    <td>{record.maintenance_status_name}</td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => openEditModal(record)}
                      >
                        <MdEdit />
                      </button>
                    </td>
                    <td>
                      <button
                        className="delete-button"
                        onClick={() => openDeleteModal(record)}
                      >
                        <MdDelete />
                      </button>
                    </td>
                  </tr>
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

      {modalContentType && isModalOpen && (
        <Modal isOpen={isModalOpen} onClose={closeModal} title="정비 기록 관리">
          {modalContentType === "add" && (
            <div className="edit-content">
              <h2>정비 기록 등록</h2>
              <form>
                <label>
                  정비 대상:
                  <input
                    type="text"
                    name="item_type_name"
                    value={formData.item_type_name}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  고유 ID:
                  <input
                    type="number"
                    name="item_id"
                    value={formData.item_id}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  문제:
                  <input
                    type="text"
                    name="issue"
                    value={formData.issue}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  비용:
                  <input
                    type="number"
                    name="cost"
                    value={formData.cost}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  정비 예정 날짜:
                  <input
                    type="datetime-local"
                    name="scheduled_at"
                    value={formData.scheduled_at}
                    onChange={handleFormChange}
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
                <button onClick={handleSaveEdit} className="save-button">
                  등록
                </button>
                <button onClick={closeModal} className="cancel-button">
                  취소
                </button>
              </div>
            </div>
          )}
          {modalContentType === "edit" && (
            <div className="edit-content">
              <h2>정비 기록 수정</h2>
              <form>
                <label>
                  정비 상태 ID:
                  <input
                    type="number"
                    name="maintenance_status_id"
                    value={formData.maintenance_status_id}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  비용:
                  <input
                    type="number"
                    name="cost"
                    value={formData.cost}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  정비 예정 날짜:
                  <input
                    type="datetime-local"
                    name="scheduled_at"
                    value={formData.scheduled_at}
                    onChange={handleFormChange}
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
                <label>
                  문제:
                  <input
                    type="text"
                    name="issue"
                    value={formData.issue}
                    onChange={handleFormChange}
                  />
                </label>
              </form>
              <div className="modal-actions">
                <button onClick={handleSaveEdit} className="save-button">
                  저장
                </button>
                <button onClick={closeModal} className="cancel-button">
                  취소
                </button>
              </div>
            </div>
          )}
          {modalContentType === "delete" && selectedMaintenanceRecord && (
            <div className="delete-content">
              <h2>정비 기록 삭제 확인</h2>
              <p>정말 이 정비 기록을 삭제하시겠습니까?</p>
              <div className="modal-actions">
                <button
                  onClick={handleConfirmDelete}
                  className="confirm-delete-button"
                >
                  삭제
                </button>
                <button onClick={closeModal} className="cancel-button">
                  취소
                </button>
              </div>
            </div>
          )}
        </Modal>
      )}
    </div>
  );
};

export default MaintenanceRecords;
