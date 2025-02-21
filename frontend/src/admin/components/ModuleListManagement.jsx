// src/admin/components/ModuleListManagement.jsx
import React, { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import AddModal from "./AddModal";
import DeleteModal from "./DeleteModal";
import { MdEdit, MdDelete } from "react-icons/md";
import "./ModuleListManagement.css";
import LoadingSpinner from "./LoadingSpinner";

const BASE_URL = import.meta.env.VITE_API_URL;

const ModuleManagementList = () => {
  // 모듈 데이터 상태
  const [modules, setModules] = useState([]);
  // 확장(토글)된 행의 module_id
  const [expandedModuleId, setExpandedModuleId] = useState(null);
  // 선택된 모듈 (삭제 등에서 사용)
  const [selectedModule, setSelectedModule] = useState(null);
  // 인라인 편집 시 수정할 모듈의 ID
  const [editingModuleId, setEditingModuleId] = useState(null);

  const [moduleTypes, setModuleTypes] = useState(null);

  // 등록 및 수정 폼 데이터 (NFC 태그 ID와 모듈 타입 ID)
  const [formData, setFormData] = useState({
    module_nfc_tag_id: "",
    module_type_id: "",
  });
  // 등록 모달 상태
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  // 삭제 모달 상태
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  // 필터, 페이지네이션, 로딩, 오류 상태
  const [filters, setFilters] = useState({
    search: "",
    page: 1,
    pageSize: 10,
    // moduleStatus: "", // 필요하면 추가
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const rowRefs = useRef({});

  // 상세정보 영역 ref (인라인 편집 시 스크롤 이동용)
  const detailInfoRef = useRef(null);

  const token = localStorage.getItem("adminToken");

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
  }, [token]);

  useEffect(() => {
    fetchModules();
  }, [fetchModules]);

  // 폼 입력 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // 행 토글 핸들러 (확장/축소)
  const toggleExpanded = (moduleId) => {
    setExpandedModuleId((prev) => (prev === moduleId ? null : moduleId));
    setEditingModuleId(null); // 토글 시 편집 모드 초기화
    setTimeout(() => {
      if (rowRefs.current[moduleId]) {
        rowRefs.current[moduleId].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  // 등록 모달 열기/닫기
  const openAddModal = () => {
    setFormData({
      module_nfc_tag_id: "",
      module_type_id: "",
    });
    setIsAddModalOpen(true);
  };
  const closeAddModal = () => setIsAddModalOpen(false);

  // 모듈 타입 목록 조회 함수
  const fetchModuleTypes = useCallback(async () => {
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
  }, [token]);

  useEffect(() => {
    fetchModules();
  }, [fetchModules]);

  // 컴포넌트가 마운트될 때 모듈 타입 목록도 조회
  useEffect(() => {
    fetchModuleTypes();
  }, [fetchModuleTypes]);

  // 등록 API 호출
  const handleSubmitAdd = async () => {
    if (!formData.module_nfc_tag_id.trim() || !formData.module_type_id.trim()) {
      alert("필수 항목을 모두 입력하세요.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const payload = {
        module_nfc_tag_id: formData.module_nfc_tag_id,
        module_type_id: Number(formData.module_type_id),
      };
      const response = await axios.post(`${BASE_URL}/admin/modules`, payload, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        await fetchModules();
        closeAddModal();
      } else {
        setError(response.data.message || "모듈 등록 실패");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "모듈 등록 중 오류 발생");
    } finally {
      setLoading(false);
    }
  }; // 인라인 수정 모드 전환 (상세정보 영역에서 "수정" 버튼 클릭)
  const startEditing = (module) => {
    setSelectedModule(module);
    setFormData({
      module_nfc_tag_id: module.module_nfc_tag_id,
      module_type_id: module.module_type_id.toString(),
    });
    setEditingModuleId(module.module_id);
    setTimeout(() => {
      if (detailInfoRef.current) {
        detailInfoRef.current.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  // 인라인 수정 API 호출
  const handleSubmitEdit = async (moduleId) => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        module_nfc_tag_id: formData.module_nfc_tag_id,
        module_type_id: Number(formData.module_type_id),
      };
      const response = await axios.patch(
        `${BASE_URL}/admin/modules/${moduleId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchModules();
        setEditingModuleId(null);
      } else {
        setError(response.data.message || "모듈 수정 실패");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "모듈 수정 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  // 인라인 수정 취소
  const cancelEditing = () => {
    setEditingModuleId(null);
  };

  // 삭제 모달 열기/닫기
  const openDeleteModal = (module) => {
    setSelectedModule(module);
    setIsDeleteModalOpen(true);
  };
  const closeDeleteModal = () => setIsDeleteModalOpen(false);

  // 삭제 API 호출
  const handleSubmitDelete = async (moduleId) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/modules/${moduleId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchModules();
        closeDeleteModal();
      } else {
        setError(response.data.message || "모듈 삭제 실패");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "모듈 삭제 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  return (
    <div className="module-management-list">
      <div className="module-management-list-header">
        <h1>모듈 목록</h1>
        <button className="add-button" onClick={openAddModal}>
          모듈 등록
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-wrapper">
          <table className="module-table">
            <thead>
              <tr>
                <th>모듈 ID</th>
                <th>NFC 태그 ID</th>
                <th>모듈 타입</th>
                <th>상태</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
              </tr>
            </thead>
            <tbody>
              {modules.length > 0 ? (
                modules.map((module) => (
                  <React.Fragment key={module.module_id}>
                    <tr
                      ref={(el) => (rowRefs.current[module.module_id] = el)}
                      className={`main-row ${
                        expandedModuleId === module.module_id
                          ? "expanded-main-row"
                          : ""
                      }`}
                      onClick={() => toggleExpanded(module.module_id)}
                    >
                      <td>{module.module_id}</td>
                      <td>
                        <span className="cell-text">
                          {module.module_nfc_tag_id}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {module.module_type_name}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {module.item_status_name === "active"
                            ? "활성화"
                            : module.item_status_name === "inactive"
                            ? "비활성화"
                            : module.item_status_name === "maintenance"
                            ? "정비 중"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {module.created_at
                            ? new Date(module.created_at).toLocaleString()
                            : "-"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {module.updated_at
                            ? new Date(module.updated_at).toLocaleString()
                            : "-"}
                        </span>
                      </td>
                    </tr>
                    {expandedModuleId === module.module_id && (
                      <tr className="expanded-row">
                        <td colSpan="6">
                          <div
                            className="detail-info-container"
                            ref={detailInfoRef}
                          >
                            <div className="detail-info">
                              <div className="detail-item">
                                <div className="detail-label">NFC 태그 ID</div>
                                <div className="detail-value">
                                  {module.module_nfc_tag_id}
                                </div>
                              </div>

                              <div className="detail-item">
                                <div className="detail-label">모듈 ID</div>
                                <div className="detail-value">
                                  {module.module_id}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">모듈 타입</div>
                                {editingModuleId === module.module_id ? (
                                  <select
                                    name="module_type_id"
                                    value={formData.module_type_id}
                                    onChange={handleFormChange}
                                    className="edit-module-type-id"
                                  >
                                    <option value="">선택하세요</option>
                                    {moduleTypes &&
                                      moduleTypes.map((mt) => (
                                        <option
                                          key={mt.module_type_id}
                                          value={mt.module_type_id}
                                        >
                                          {mt.module_type_name} (크기:{" "}
                                          {mt.module_type_size},{" "}
                                          {mt.module_type_cost}원)
                                        </option>
                                      ))}
                                  </select>
                                ) : (
                                  <div className="detail-value">
                                    {(() => {
                                      const mt = moduleTypes
                                        ? moduleTypes.find(
                                            (m) =>
                                              m.module_type_id ===
                                              module.module_type_id
                                          )
                                        : null;
                                      return mt
                                        ? `${mt.module_type_name} (크기: ${mt.module_type_size}, ${mt.module_type_cost}원)`
                                        : module.module_type_id;
                                    })()}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  모듈 타입 이름
                                </div>
                                <div className="detail-value">
                                  {module.module_type_name}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  마지막 정비 일시
                                </div>
                                <div className="detail-value">
                                  {module.last_maintenance_at
                                    ? new Date(
                                        module.last_maintenance_at
                                      ).toLocaleString()
                                    : "미정"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  다음 정비 일시
                                </div>
                                <div className="detail-value">
                                  {module.next_maintenance_at
                                    ? new Date(
                                        module.next_maintenance_at
                                      ).toLocaleString()
                                    : "미정"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">모듈 상태</div>
                                <div className="detail-value">
                                  {module.item_status_name === "active"
                                    ? "활성화"
                                    : module.item_status_name === "inactive"
                                    ? "비활성화"
                                    : module.item_status_name === "maintenance"
                                    ? "정비 중"
                                    : "알 수 없음"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">등록 일시</div>
                                <div className="detail-value">
                                  {new Date(module.created_at).toLocaleString()}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">등록자</div>
                                <div className="detail-value">
                                  {module.created_by}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">수정 일시</div>
                                <div className="detail-value">
                                  {new Date(module.updated_at).toLocaleString()}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">수정자</div>
                                <div className="detail-value">
                                  {module.updated_by}
                                </div>
                              </div>
                            </div>
                            <div className="detail-actions">
                              {editingModuleId === module.module_id ? (
                                <>
                                  <button
                                    className="detail-save-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleSubmitEdit(module.module_id);
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
                                      startEditing(module);
                                    }}
                                  >
                                    <MdEdit />
                                  </button>
                                  <button
                                    className="detail-delete-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      openDeleteModal(module);
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
                  <td colSpan="6">등록된 모듈이 없습니다.</td>
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

      <AddModal
        isOpen={isAddModalOpen}
        onClose={closeAddModal}
        onSubmit={handleSubmitAdd}
        title="신규 모듈 등록"
      >
        <div className="form-group">
          <label>NFC 태그 ID</label>
          <input
            type="text"
            name="module_nfc_tag_id"
            className="add-module-nfc-tag-id"
            placeholder="예) 043F8E6A6C1D90"
            value={formData.module_nfc_tag_id}
            onChange={handleFormChange}
            required
          />
        </div>
        <div className="form-group">
          <label>모듈 타입</label>
          <select
            name="module_type_id"
            value={formData.module_type_id}
            onChange={handleFormChange}
            required
          >
            <option value="">선택하세요</option>
            {moduleTypes &&
              moduleTypes.map((mt) => (
                <option key={mt.module_type_id} value={mt.module_type_id}>
                  {mt.module_type_name} (크기: {mt.module_type_size},{" "}
                  {mt.module_type_cost})
                </option>
              ))}
          </select>
        </div>
      </AddModal>

      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onDelete={() => handleSubmitDelete(selectedModule.module_id)}
        title="모듈 삭제 확인"
        message={
          selectedModule
            ? `${selectedModule.module_nfc_tag_id} 모듈을 삭제하시겠습니까?`
            : ""
        }
      />
    </div>
  );
};

export default ModuleManagementList;
