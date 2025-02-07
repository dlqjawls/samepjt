// src/admin/components/ModuleListManagement.jsx
import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { MdSearch } from "react-icons/md";
import Modal from "./Modal"; // Modal 컴포넌트 경로 (예시)
import "./ModuleManagement.css";

const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

const ModuleManagementList = ({ token, onSelectModule }) => {
  const [modules, setModules] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    moduleSearch: "",
    moduleStatus: "",
    modulePage: 1,
    modulePageSize: 10,
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  // 모달 관련 상태: modalType는 "add", "edit", "delete"
  const [modalType, setModalType] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);
  const [formData, setFormData] = useState({
    moduleNfcTagId: "",
    moduleTypeId: "",
    moduleType: "",
    moduleSize: "",
    moduleCost: "",
    status: "active",
    lastMaintenanceAt: "",
    nextMaintenanceAt: "",
    currentLocation: "",
  });

  const fetchModules = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/modules`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          search: filters.moduleSearch || undefined,
          status: filters.moduleStatus || undefined,
          page: filters.modulePage,
          pageSize: filters.modulePageSize,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        setModules(response.data.data.modules);
        setPagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "모듈 목록을 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 목록을 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }, [token, filters]);

  useEffect(() => {
    fetchModules();
  }, [fetchModules]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      modulePage: 1,
    }));
  };

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
      modulePage: newPage,
    }));
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // 모달 열기 함수
  const openAddModal = () => {
    setFormData({
      moduleNfcTagId: "",
      moduleTypeId: "",
      moduleType: "",
      moduleSize: "",
      moduleCost: "",
      status: "active",
      lastMaintenanceAt: "",
      nextMaintenanceAt: "",
      currentLocation: "",
    });
    setModalType("add");
  };

  const openEditModal = (module) => {
    setSelectedModule(module);
    setFormData({
      moduleNfcTagId: module.moduleNfcTagId,
      moduleTypeId: module.moduleTypeId,
      moduleType: module.moduleType,
      moduleSize: module.moduleSize,
      moduleCost: module.moduleCost,
      status: module.status,
      lastMaintenanceAt: module.lastMaintenanceAt || "",
      nextMaintenanceAt: module.nextMaintenanceAt || "",
      currentLocation: module.currentLocation || "",
    });
    setModalType("edit");
  };

  const openDeleteModal = (module) => {
    setSelectedModule(module);
    setModalType("delete");
  };

  const closeModal = () => {
    setModalType(null);
    setSelectedModule(null);
    setFormData({
      moduleNfcTagId: "",
      moduleTypeId: "",
      moduleType: "",
      moduleSize: "",
      moduleCost: "",
      status: "active",
      lastMaintenanceAt: "",
      nextMaintenanceAt: "",
      currentLocation: "",
    });
  };

  // CRUD API 호출 함수
  const handleSaveModuleAdd = async () => {
    if (!formData.moduleNfcTagId.trim() || !formData.moduleTypeId.trim()) {
      setError("NFC 태그 ID와 모듈 타입은 필수 항목입니다.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const payload = {
        module_nfc_tag_id: formData.moduleNfcTagId,
        module_type_id: Number(formData.moduleTypeId),
      };
      const response = await axios.post(`${BASE_URL}/admin/modules`, payload, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        fetchModules();
        closeModal();
      } else {
        setError(response.data.message || "모듈을 등록하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("모듈을 등록하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveModuleEdit = async () => {
    if (!selectedModule) return;
    setLoading(true);
    setError("");
    try {
      const payload = {
        moduleTypeId: Number(formData.moduleTypeId),
      };
      const response = await axios.patch(
        `${BASE_URL}/admin/modules/${selectedModule.moduleId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModules();
        closeModal();
      } else {
        setError(response.data.message || "모듈을 수정하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("모듈을 수정하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedModule) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/module/${selectedModule.moduleId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModules();
        closeModal();
      } else {
        setError(response.data.message || "모듈을 삭제하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("모듈을 삭제하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="module-management-list">
      <div className="filters">
        <h2>모듈 목록</h2>
        <label>
          상태
          <select
            name="moduleStatus"
            value={filters.moduleStatus}
            onChange={handleFilterChange}
          >
            <option value="">전체</option>
            <option value="active">활성화</option>
            <option value="inactive">비활성화</option>
            <option value="maintenance">정비 중</option>
          </select>
        </label>
        <label>
          검색
          <input
            type="text"
            name="moduleSearch"
            value={filters.moduleSearch}
            onChange={handleFilterChange}
            placeholder="모듈 NFC 태그 ID 또는 타입 검색"
          />
        </label>
        <button onClick={fetchModules}>검색</button>
        <button className="add-button" onClick={openAddModal}>
          모듈 등록
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <div className="table-wrapper">
          <table className="module-table">
            <thead>
              <tr>
                <th>모듈 ID</th>
                <th>NFC 태그 ID</th>
                <th>모듈 타입</th>
                <th>모듈 크기</th>
                <th>모듈 비용 (원)</th>
                <th>상태</th>
                <th>현재 위치</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
                <th>상세 보기</th>
                <th>수정</th>
                <th>삭제</th>
              </tr>
            </thead>
            <tbody>
              {modules.length > 0 ? (
                modules.map((module) => (
                  <tr key={module.moduleId}>
                    <td>{module.moduleId}</td>
                    <td>{module.moduleNfcTagId}</td>
                    <td>{module.moduleType}</td>
                    <td>{module.moduleSize}</td>
                    <td>{module.moduleCost.toLocaleString()}원</td>
                    <td>
                      <span
                        className={`status-badge ${
                          module.status === "active"
                            ? "status-active"
                            : module.status === "inactive"
                            ? "status-inactive"
                            : "status-maintenance"
                        }`}
                      >
                        {module.status === "active"
                          ? "활성화"
                          : module.status === "inactive"
                          ? "비활성화"
                          : "정비 중"}
                      </span>
                    </td>
                    <td>{module.currentLocation || "미정"}</td>
                    <td>
                      {module.createdAt
                        ? new Date(module.createdAt).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      {module.updatedAt
                        ? new Date(module.updatedAt).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => {
                          if (onSelectModule) onSelectModule(module);
                        }}
                      >
                        <MdSearch />
                      </button>
                    </td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => openEditModal(module)}
                      >
                        수정
                      </button>
                    </td>
                    <td>
                      <button
                        className="delete-button"
                        onClick={() => openDeleteModal(module)}
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="12">조회된 모듈이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      <div className="pagination">
        <button
          onClick={() => handlePageChange(filters.modulePage - 1)}
          disabled={filters.modulePage === 1}
        >
          이전
        </button>
        <span>
          {filters.modulePage} / {pagination.totalPages}
        </span>
        <button
          onClick={() => handlePageChange(filters.modulePage + 1)}
          disabled={filters.modulePage === pagination.totalPages}
        >
          다음
        </button>
      </div>

      {modalType && (
        <Modal isOpen={true} onClose={closeModal}>
          {modalType === "add" && (
            <div className="add-content">
              <h2>모듈 등록</h2>
              <form className="add-form">
                <label>
                  NFC 태그 ID:
                  <input
                    type="text"
                    name="moduleNfcTagId"
                    value={formData.moduleNfcTagId}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  모듈 타입 ID:
                  <input
                    type="text"
                    name="moduleTypeId"
                    value={formData.moduleTypeId}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  모듈 타입:
                  <input
                    type="text"
                    name="moduleType"
                    value={formData.moduleType}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  모듈 크기:
                  <input
                    type="text"
                    name="moduleSize"
                    value={formData.moduleSize}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  모듈 비용 (원):
                  <input
                    type="number"
                    name="moduleCost"
                    value={formData.moduleCost}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  상태:
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleFormChange}
                  >
                    <option value="active">활성화</option>
                    <option value="inactive">비활성화</option>
                    <option value="maintenance">정비 중</option>
                  </select>
                </label>
                <label>
                  최근 정비 일자:
                  <input
                    type="date"
                    name="lastMaintenanceAt"
                    value={formData.lastMaintenanceAt}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  다음 정비 일자:
                  <input
                    type="date"
                    name="nextMaintenanceAt"
                    value={formData.nextMaintenanceAt}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  현재 위치:
                  <input
                    type="text"
                    name="currentLocation"
                    value={formData.currentLocation}
                    onChange={handleFormChange}
                  />
                </label>
              </form>
              <div className="modal-actions">
                <button
                  onClick={handleSaveModuleAdd}
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
          {modalType === "edit" && selectedModule && (
            <div className="edit-content">
              <h2>모듈 수정</h2>
              <form className="edit-form">
                <label>
                  NFC 태그 ID:
                  <input
                    type="text"
                    name="moduleNfcTagId"
                    value={formData.moduleNfcTagId}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  모듈 타입 ID:
                  <input
                    type="text"
                    name="moduleTypeId"
                    value={formData.moduleTypeId}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  모듈 타입:
                  <input
                    type="text"
                    name="moduleType"
                    value={formData.moduleType}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  모듈 크기:
                  <input
                    type="text"
                    name="moduleSize"
                    value={formData.moduleSize}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  모듈 비용 (원):
                  <input
                    type="number"
                    name="moduleCost"
                    value={formData.moduleCost}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  상태:
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleFormChange}
                  >
                    <option value="active">활성화</option>
                    <option value="inactive">비활성화</option>
                    <option value="maintenance">정비 중</option>
                  </select>
                </label>
                <label>
                  최근 정비 일자:
                  <input
                    type="date"
                    name="lastMaintenanceAt"
                    value={formData.lastMaintenanceAt}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  다음 정비 일자:
                  <input
                    type="date"
                    name="nextMaintenanceAt"
                    value={formData.nextMaintenanceAt}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  현재 위치:
                  <input
                    type="text"
                    name="currentLocation"
                    value={formData.currentLocation}
                    onChange={handleFormChange}
                  />
                </label>
              </form>
              <div className="modal-actions">
                <button
                  onClick={handleSaveModuleEdit}
                  className="save-button"
                  disabled={loading}
                >
                  저장
                </button>
                <button onClick={closeModal} className="cancel-button">
                  취소
                </button>
              </div>
            </div>
          )}
          {modalType === "delete" && selectedModule && (
            <div className="delete-content">
              <h2>모듈 삭제 확인</h2>
              <p>정말 이 모듈을 삭제하시겠습니까?</p>
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
        </Modal>
      )}
    </div>
  );
};

export default ModuleManagementList;
