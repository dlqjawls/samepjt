// src/admin/components/ModuleListManagement.jsx
import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { MdSearch, MdEdit, MdDelete } from "react-icons/md";
import Modal from "./Modal";
import "./ModuleListManagement.css";

const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

const ModuleManagementList = () => {
  const token = localStorage.getItem("adminToken");

  // 백엔드에서 받아온 전체 모듈 데이터와 필터링된 데이터 상태
  const [allModules, setAllModules] = useState([]);
  const [filteredModules, setFilteredModules] = useState([]);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // 필터 관련 상태 (검색어, 상태, 페이지, 페이지당 항목수)
  const [filters, setFilters] = useState({
    moduleSearch: "",
    moduleStatus: "",
    modulePage: 1,
    modulePageSize: 10,
  });

  // 클라이언트 단 페이징 계산
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  // 모달 관련 상태: modalType는 "add", "edit", "delete", "detail"
  const [modalType, setModalType] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);
  const [formData, setFormData] = useState({
    moduleNfcTagId: "",
    moduleTypeId: "",
  });

  const [moduleTypes, setModuleTypes] = useState([]);

  const fetchModules = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/modules`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        const modulesData = response.data.data.modules;
        setAllModules(modulesData);
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
  }, [token]);

  // 모듈 타입 목록 조회 함수
  const fetchModuleTypes = async () => {
    try {
      const response = await axios.get(`${BASE_URL}/admin/module-types`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        setModuleTypes(response.data.data.module_types);
      } else {
        console.error("모듈 타입 목록 불러오기 실패:", response.data.message);
      }
    } catch (err) {
      console.error("모듈 타입 목록 불러오는 중 오류:", err);
    }
  };

  useEffect(() => {
    fetchModules();
  }, [fetchModules]);

  // 컴포넌트가 마운트될 때 모듈 타입 목록도 조회
  useEffect(() => {
    fetchModuleTypes();
  });

  // 필터(검색어, 상태)와 전체 데이터를 기준으로 클라이언트 단 필터링
  useEffect(() => {
    let result = allModules;

    // 검색어 필터: NFC 태그 ID와 모듈 타입 이름을 소문자로 비교
    if (filters.moduleSearch) {
      const searchLower = filters.moduleSearch.toLowerCase();
      result = result.filter(
        (module) =>
          module.module_nfc_tag_id.toLowerCase().includes(searchLower) ||
          module.module_type_name.toLowerCase().includes(searchLower)
      );
    }

    // 상태 필터: status_name이 필터값과 일치하는 경우
    if (filters.moduleStatus) {
      result = result.filter(
        (module) => module.status_name === filters.moduleStatus
      );
    }

    setFilteredModules(result);

    // 필터링된 데이터의 총 개수를 기준으로 페이지네이션 계산
    setPagination({
      currentPage: filters.modulePage,
      totalItems: result.length,
      pageSize: filters.modulePageSize,
      totalPages: Math.ceil(result.length / filters.modulePageSize),
    });
  }, [filters, allModules]);

  // 현재 페이지에 해당하는 모듈 데이터 (client-side 페이징)
  const paginatedModules = filteredModules.slice(
    (filters.modulePage - 1) * filters.modulePageSize,
    filters.modulePage * filters.modulePageSize
  );

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      modulePage: 1, // 필터 변경 시 첫 페이지로 초기화
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

  // 모달 열기 함수들
  const openAddModal = () => {
    setFormData({
      moduleNfcTagId: "",
      moduleTypeId: "",
    });
    setModalType("add");
  };

  const openEditModal = (module) => {
    setSelectedModule(module);
    setFormData({
      moduleNfcTagId: module.module_nfc_tag_id,
      moduleTypeId: module.module_type_id,
    });
    setModalType("edit");
  };

  // 상세 보기 모달 열기 함수 추가
  const openDetailModal = (module) => {
    setSelectedModule(module);
    setModalType("detail");
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
    });
  };

  // 신규 모듈 등록 API 호출
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

  // 모듈 수정 API 호출 (모듈 타입만 수정 가능)
  const handleSaveModuleEdit = async () => {
    if (!selectedModule) return;
    setLoading(true);
    setError("");
    try {
      const payload = {
        module_type_id: Number(formData.moduleTypeId),
      };
      const response = await axios.patch(
        `${BASE_URL}/admin/modules/${selectedModule.module_id}`,
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

  // 모듈 삭제 API 호출
  const handleConfirmDelete = async () => {
    if (!selectedModule) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/modules/${selectedModule.module_id}`,
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
      <div className="module-management-list-header">
        <h1>모듈 목록</h1>
        <button className="add-button" onClick={openAddModal}>
          모듈 등록
        </button>
      </div>

      {/* <div className="filters">
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
        </label> */}
      {/* 검색 버튼: 필터 상태 변경은 useEffect에서 처리됨 */}
      {/* <button onClick={() => setFilters({ ...filters })}>검색</button>
      </div> */}
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
                <th>마지막 정비 일자</th>
                <th>다음 정비 일자</th>
                <th>상태</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
                <th>상세 보기</th>
                <th>수정</th>
                <th>삭제</th>
              </tr>
            </thead>
            <tbody>
              {paginatedModules.length > 0 ? (
                paginatedModules.map((module, index) => (
                  <tr key={module.module_id || index}>
                    <td>{module.module_id}</td>
                    <td>{module.module_nfc_tag_id}</td>
                    <td>{module.module_type_name}</td>
                    <td>
                      {module.last_maintenance_at
                        ? new Date(module.last_maintenance_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      {module.next_maintenance_at
                        ? new Date(module.next_maintenance_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>{module.status_name || "-"}</td>
                    <td>
                      {module.created_at
                        ? new Date(module.created_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      {module.updated_at
                        ? new Date(module.updated_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => openDetailModal(module)}
                      >
                        <MdSearch />
                      </button>
                    </td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => openEditModal(module)}
                      >
                        <MdEdit />
                      </button>
                    </td>
                    <td>
                      <button
                        className="delete-button"
                        onClick={() => openDeleteModal(module)}
                      >
                        <MdDelete />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="11">조회된 모듈이 없습니다.</td>
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
          {modalType === "detail" && selectedModule && (
            <div className="detail-content">
              <h2>모듈 상세 정보</h2>
              <p>
                <strong>모듈 ID:</strong> {selectedModule.module_id}
              </p>
              <p>
                <strong>NFC 태그 ID:</strong> {selectedModule.module_nfc_tag_id}
              </p>
              <p>
                <strong>모듈 타입:</strong> {selectedModule.module_type_name}
              </p>
              <p>
                <strong>상태:</strong> {selectedModule.status_name}
              </p>
              <p>
                <strong>등록 일자:</strong>{" "}
                {selectedModule.created_at
                  ? new Date(selectedModule.created_at).toLocaleString()
                  : "-"}
              </p>
              <p>
                <strong>수정 일자:</strong>{" "}
                {selectedModule.updated_at
                  ? new Date(selectedModule.updated_at).toLocaleString()
                  : "-"}
              </p>
              <div className="modal-actions">
                <button onClick={closeModal} className="cancel-button">
                  닫기
                </button>
              </div>
            </div>
          )}
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
                    type="number"
                    name="moduleTypeId"
                    value={formData.moduleTypeId}
                    onChange={handleFormChange}
                    required
                  />
                </label>
              </form>
              {/* 모듈 타입 조회 표 추가 */}
              <h3>모듈 타입 목록</h3>
              <table className="module-type-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>이름</th>
                    <th>크기</th>
                    <th>비용</th>
                  </tr>
                </thead>
                <tbody>
                  {moduleTypes.length > 0 ? (
                    moduleTypes.map((mt) => (
                      <tr key={mt.module_type_id}>
                        <td>{mt.module_type_id}</td>
                        <td>{mt.module_type_name}</td>
                        <td>{mt.module_type_size}</td>
                        <td>{mt.module_type_cost.toLocaleString()}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4">모듈 타입이 없습니다.</td>
                    </tr>
                  )}
                </tbody>
              </table>
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
                  모듈 타입 ID:
                  <input
                    type="number"
                    name="moduleTypeId"
                    value={formData.moduleTypeId}
                    onChange={handleFormChange}
                    required
                  />
                </label>
              </form>
              {/* 모듈 타입 조회 표 추가 */}
              <h3>모듈 타입 목록</h3>
              <table className="module-type-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>이름</th>
                    <th>크기</th>
                    <th>비용</th>
                  </tr>
                </thead>
                <tbody>
                  {moduleTypes.length > 0 ? (
                    moduleTypes.map((mt) => (
                      <tr key={mt.module_type_id}>
                        <td>{mt.module_type_id}</td>
                        <td>{mt.module_type_name}</td>
                        <td>{mt.module_type_size}</td>
                        <td>{mt.module_type_cost.toLocaleString()}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4">모듈 타입이 없습니다.</td>
                    </tr>
                  )}
                </tbody>
              </table>
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
