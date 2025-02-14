// src/admin/components/ModuleSetManagement.jsx

import React, { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import AddModal from "./AddModal";
import DeleteModal from "./DeleteModal";
import { MdEdit, MdDelete } from "react-icons/md";
import "./ModuleSetManagement.css";
import LoadingSpinner from "./LoadingSpinner";

const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

const ModuleSetManagement = () => {
  // 전체 모듈 세트 데이터와 필터링된 데이터 상태
  const [moduleSets, setModuleSets] = useState([]);
  // 확장(토글)된 행의 module_set_id
  const [expandedModuleSetId, setExpandedModuleSetId] = useState(null);
  // 선택된 모듈 세트(삭제 등에서 사용)
  const [selectedModuleSet, setSelectedModuleSet] = useState(null);
  // 등록 및 수정 폼 데이터
  const [formData, setFormData] = useState({
    module_set_name: "",
    description: "",
    module_set_images: "",
    module_set_features: "",
    module_type_id: "",
    options: "[]",
  });

  // 등록 모달 상태
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  // 삭제 모달 상태
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  // 편집 모드 여부 (인라인 편집)
  const [editingModuleSetId, setEditingModuleSetId] = useState(null);

  // 필터 관련 상태 (검색어, 페이지, 페이지당 항목수)
  const [filters, setFilters] = useState({
    moduleSetSearch: "",
    moduleSetPage: 1,
    moduleSetPageSize: 10,
  });

  // 클라이언트 단 페이징 계산
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 모듈 타입 목록 (추가 정보 용)
  const [moduleTypes, setModuleTypes] = useState([]);

  const rowRefs = useRef({});

  // 상세정보 영역 ref (편집 시 스크롤 이동용)
  const detailInfoRef = useRef(null);

  const token = localStorage.getItem("adminToken");

  //모듈 셋트 조회 API 호출
  const fetchModuleSets = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/module-sets`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        const modulesData = response.data.data.module_sets;
        setModuleSets(modulesData);
        setPagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "모듈 세트 목록을 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.message ||
          "모듈 세트 목록을 불러오는 중 오류가 발생했습니다."
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchModuleSets();
  }, [fetchModuleSets]);

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

  // 컴포넌트가 마운트될 때 모듈 타입 목록도 조회
  useEffect(() => {
    fetchModuleTypes();
  });

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      moduleSetPage: 1, // 필터 변경 시 첫 페이지로 초기화
    }));
  };

  // 폼 입력 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // 토글(확장) 핸들러
  const toggleExpanded = (moduleSetId) => {
    setExpandedModuleSetId((prev) =>
      prev === moduleSetId ? null : moduleSetId
    );
    // 인라인 편집 모드 초기화
    setEditingModuleSetId(null);
    setTimeout(() => {
      if (rowRefs.current[moduleSetId]) {
        rowRefs.current[moduleSetId].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  // 등록 모달 열기 및 닫기
  const openAddModal = () => {
    setFormData({
      module_set_name: "",
      description: "",
      module_set_images: "",
      module_set_features: "",
      module_type_id: "",
      options: "[]",
    });
    setIsAddModalOpen(true);
  };
  const closeAddModal = () => setIsAddModalOpen(false);

  // 신규 모듈 세트 등록 API 호출
  const handleSubmitAdd = async () => {
    // <!> options[].option_type_id, options[].quantity가 추가되어야 한다.
    if (!formData.module_set_name.trim() || !formData.module_type_id.trim()) {
      alert("모듈 세트 이름과 모듈 타입 아이디는 필수 항목입니다.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const optionsPayload = (() => {
        try {
          return JSON.parse(formData.options);
        } catch (e) {
          return [];
        }
      })();
      const payload = {
        module_set_name: formData.module_set_name,
        description: formData.description,
        module_set_images: formData.module_set_images
          ? formData.module_set_images.split(",").map((s) => s.trim())
          : [],
        module_set_features: formData.module_set_features,
        module_type_id: Number(formData.module_type_id),
        options: optionsPayload,
      };
      const response = await axios.post(
        `${BASE_URL}/admin/module-sets`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        closeAddModal();
      } else {
        setError(
          response.data.message || "모듈 세트를 등록하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.message ||
          "모듈 세트를 등록하는 중 오류가 발생했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  // 인라인 수정 모드 전환: 상세 정보 영역에서 "수정" 버튼 클릭 시 호출됨
  const startEditing = (moduleSet) => {
    setSelectedModuleSet(moduleSet);
    setFormData({
      module_set_name: moduleSet.module_set_name,
      description: moduleSet.description,
      module_set_images: Array.isArray(moduleSet.module_set_images)
        ? moduleSet.module_set_images.join(", ")
        : moduleSet.module_set_images || "",
      module_set_features: moduleSet.module_set_features,
      module_type_id: Number(moduleSet.module_type_id),
      options: "[]",
    });
    setEditingModuleSetId(moduleSet.module_set_id);
    setTimeout(() => {
      if (detailInfoRef.current) {
        detailInfoRef.current.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100); // 약간의 딜레이 후 스크롤 호출 (렌더링 완료 후)
  };

  // 인라인 수정을 위한 수정 API 호출
  const handleSubmitEdit = async (moduleSetId) => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        module_set_name: formData.module_set_name,
        description: formData.description,
        module_set_images: formData.module_set_images
          ? formData.module_set_images.split(",").map((s) => s.trim())
          : [],
        module_set_features: formData.module_set_features,
        module_type_id: Number(formData.module_type_id),
      };
      const response = await axios.patch(
        `${BASE_URL}/admin/module-sets/${moduleSetId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        setEditingModuleSetId(null);
      } else {
        setError(
          response.data.message || "모듈 세트 정보를 수정하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 세트 정보를 수정하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 인라인 수정 취소
  const cancelEditing = () => {
    setEditingModuleSetId(null);
  };

  // 삭제 모달 열기
  const openDeleteModal = (moduleSet) => {
    setSelectedModuleSet(moduleSet);
    setIsDeleteModalOpen(true);
  };
  const closeDeleteModal = () => setIsDeleteModalOpen(false);

  // 삭제 API 호출
  const handleSubmitDelete = async (moduleSetId) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/module-sets/${moduleSetId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchModuleSets();
        closeDeleteModal();
      } else {
        setError(
          response.data.message || "모듈 세트를 삭제하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.message ||
          "모듈 세트를 삭제하는 중 오류가 발생했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, moduleSetPage: newPage }));
  };

  // 필터링 적용: 간단히 모듈 세트 이름으로 필터링
  const filteredModuleSets = moduleSets.filter((ms) =>
    filters.moduleSetSearch
      ? ms.module_set_name
          .toLowerCase()
          .includes(filters.moduleSetSearch.toLowerCase())
      : true
  );
  const paginatedModuleSets = filteredModuleSets.slice(
    (filters.moduleSetPage - 1) * filters.moduleSetPageSize,
    filters.moduleSetPage * filters.moduleSetPageSize
  );

  return (
    <div className="module-set-management">
      <div className="module-set-header">
        <h1>모듈 세트 목록</h1>
        <button className="add-button" onClick={openAddModal}>
          모듈 세트 등록
        </button>
      </div>

      {/* <div className="filters">
        <label>
          검색
          <input
            type="text"
            name="moduleSetSearch"
            value={filters.moduleSetSearch}
            onChange={handleFilterChange}
            placeholder="모듈 세트 이름 검색"
          />
        </label> */}
      {/* 검색 버튼은 필터 입력 변경 시 이미 useEffect로 필터링됨 */}
      {/* <button onClick={() => setFilters({ ...filters })}>검색</button>
      </div> */}

      {error && <p className="error">{error}</p>}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-wrapper">
          <table className="module-set-table">
            <thead>
              <tr>
                <th>모듈 세트 ID</th>
                <th>모듈 세트 이름</th>
                <th>설명</th>
                <th>특징</th>
                <th>모듈 타입 ID</th>
                <th>가격</th>
              </tr>
            </thead>
            <tbody>
              {paginatedModuleSets.length > 0 ? (
                paginatedModuleSets.map((set) => (
                  <React.Fragment key={set.module_set_id}>
                    <tr
                      ref={(el) => (rowRefs.current[set.module_set_id] = el)}
                      className={`main-row ${
                        expandedModuleSetId === set.module_set_id
                          ? "expanded-main-row"
                          : ""
                      }`}
                      onClick={() => toggleExpanded(set.module_set_id)}
                    >
                      <td>{set.module_set_id}</td>
                      <td>
                        <span className="cell-text">{set.module_set_name}</span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {set.description || "-"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {set.module_set_features || "-"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {set.module_type_id || "-"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">{set.price || 0}</span>
                      </td>
                    </tr>
                    {expandedModuleSetId === set.module_set_id && (
                      <tr className="expanded-row">
                        <td colSpan="6">
                          <div
                            className="detail-info-container"
                            ref={detailInfoRef}
                          >
                            <div className="detail-info">
                              <div className="detail-item">
                                <div className="detail-label">
                                  모듈 세트 이름
                                </div>
                                {editingModuleSetId === set.module_set_id ? (
                                  <input
                                    type="text"
                                    name="module_set_name"
                                    value={formData.module_set_name}
                                    onChange={handleFormChange}
                                    className="edit-module-set-name"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {set.module_set_name}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">설명</div>
                                {editingModuleSetId === set.module_set_id ? (
                                  <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleFormChange}
                                    className="edit-description"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {set.description}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  모듈 세트 이미지
                                </div>
                                <div className="detail-value">
                                  {set.module_set_images &&
                                  Array.isArray(set.module_set_images) ? (
                                    <img
                                      src={set.module_set_images[0]}
                                      alt={set.module_set_name}
                                      className="module-set-image"
                                    />
                                  ) : (
                                    set.module_set_images || "이미지 없음"
                                  )}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">특징</div>
                                {editingModuleSetId === set.module_set_id ? (
                                  <input
                                    type="text"
                                    name="module_set_features"
                                    value={formData.module_set_features}
                                    onChange={handleFormChange}
                                    className="edit-module-set-features"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {set.module_set_features}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">모듈 타입 ID</div>
                                {editingModuleSetId === set.module_set_id ? (
                                  <input
                                    type="number"
                                    name="module_type_id"
                                    value={formData.module_type_id}
                                    onChange={handleFormChange}
                                    className="edit-module-type-id"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {set.module_type_id}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">가격</div>
                                <div className="detail-value">
                                  {set.cost ? set.cost : 0}
                                </div>
                              </div>
                            </div>
                            <div className="detail-actions">
                              {editingModuleSetId === set.module_set_id ? (
                                <>
                                  <button
                                    className="detail-save-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleSubmitEdit(set.module_set_id);
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
                                      startEditing(set);
                                    }}
                                  >
                                    <MdEdit />
                                  </button>
                                  <button
                                    className="detail-delete-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      openDeleteModal(set);
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
                  <td colSpan="9">조회된 모듈 세트가 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      <div className="pagination">
        <button
          onClick={() => handlePageChange(filters.moduleSetPage - 1)}
          disabled={filters.moduleSetPage === 1}
        >
          이전
        </button>
        <span>
          {filters.moduleSetPage} / {pagination.totalPages}
        </span>
        <button
          onClick={() => handlePageChange(filters.moduleSetPage + 1)}
          disabled={filters.moduleSetPage === pagination.totalPages}
        >
          다음
        </button>
      </div>

      <AddModal
        isOpen={isAddModalOpen}
        onClose={closeAddModal}
        onSubmit={handleSubmitAdd}
        title="신규 모듈 세트 등록"
      >
        <div className="form-group">
          <label>모듈 세트 이름</label>
          <input
            type="text"
            name="module_set_name"
            placeholder="예: 모듈 세트 A"
            value={formData.module_set_name}
            onChange={handleFormChange}
            required
          />
        </div>
        <div className="form-group">
          <label>설명</label>
          <textarea
            name="description"
            placeholder="모듈 세트에 대한 설명"
            value={formData.description}
            onChange={handleFormChange}
          />
        </div>
        <div className="form-group">
          <label>모듈 세트 이미지 (콤마로 구분)</label>
          <input
            type="text"
            name="module_set_images"
            placeholder="이미지 URL1, 이미지 URL2"
            value={formData.module_set_images}
            onChange={handleFormChange}
          />
        </div>
        <div className="form-group">
          <label>모듈 세트 특징</label>
          <input
            type="text"
            name="module_set_features"
            placeholder="예: 기능1, 기능2"
            value={formData.module_set_features}
            onChange={handleFormChange}
          />
        </div>
        <div className="form-group">
          <label>모듈 타입 ID</label>
          <input
            type="number"
            name="module_type_id"
            placeholder="예: 1"
            value={formData.module_type_id}
            onChange={handleFormChange}
            required
          />
        </div>
        <div className="form-group">
          <label>옵션 (JSON 형식)</label>
          <textarea
            name="options"
            placeholder='예: [{"option_type_id":201,"quantity":1}]'
            value={formData.options}
            onChange={handleFormChange}
          />
        </div>
      </AddModal>

      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onDelete={() => handleSubmitDelete(selectedModuleSet.module_set_id)}
        title="모듈 세트 삭제 확인"
        message={
          selectedModuleSet
            ? `${selectedModuleSet.module_set_name} 모듈 세트를 삭제하시겠습니까?`
            : ""
        }
      />
    </div>
  );
};

export default ModuleSetManagement;
