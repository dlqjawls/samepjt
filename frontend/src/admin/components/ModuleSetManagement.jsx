// src/admin/components/ModuleSetManagement.jsx
import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import Modal from "./Modal";
import { MdSearch, MdEdit, MdDelete } from "react-icons/md";
import "./ModuleSetManagement.css";

const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

const ModuleSetManagement = () => {
  const token = localStorage.getItem("adminToken");

  // 전체 모듈 세트 데이터와 필터링된 데이터 상태
  const [allModuleSets, setAllModuleSets] = useState([]);
  const [filteredModuleSets, setFilteredModuleSets] = useState([]);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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

  // 모달 관련 상태
  // modalContentType: "detail" | "edit" | "delete" | "add"
  const [modalContentType, setModalContentType] = useState("detail");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedModuleSet, setSelectedModuleSet] = useState(null);
  const [formData, setFormData] = useState({
    module_set_name: "",
    description: "",
    module_set_images: "", // 콤마로 구분된 문자열 → 배열로 변환하여 전송
    module_set_features: "",
    module_type_id: "",
    options: "[]", // 등록 시 옵션을 JSON 문자열로 입력 (수정 시에는 사용하지 않음)
  });

  const [moduleTypes, setModuleTypes] = useState([]);

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
        setAllModuleSets(modulesData);
      } else {
        setError(
          response.data.message || "모듈 세트 목록을 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 세트 목록을 불러오는 중 오류가 발생했습니다.");
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
    fetchModuleSets();
  }, [fetchModuleSets]);

  // 컴포넌트가 마운트될 때 모듈 타입 목록도 조회
  useEffect(() => {
    fetchModuleTypes();
  });

  // 필터(검색어 등)를 적용하여 전체 데이터에서 필터링
  useEffect(() => {
    let result = allModuleSets;
    if (filters.moduleSetSearch) {
      const searchLower = filters.moduleSetSearch.toLowerCase();
      result = result.filter((moduleSet) =>
        moduleSet.module_set_name.toLowerCase().includes(searchLower)
      );
    }
    setFilteredModuleSets(result);
    // 필터링된 데이터의 길이를 기준으로 페이징 정보 업데이트
    setPagination({
      currentPage: filters.moduleSetPage,
      totalItems: result.length,
      pageSize: filters.moduleSetPageSize,
      totalPages: Math.ceil(result.length / filters.moduleSetPageSize),
    });
  }, [filters, allModuleSets]);

  // 현재 페이지에 해당하는 데이터
  const paginatedModuleSets = filteredModuleSets.slice(
    (filters.moduleSetPage - 1) * filters.moduleSetPageSize,
    filters.moduleSetPage * filters.moduleSetPageSize
  );

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      moduleSetPage: 1, // 필터 변경 시 첫 페이지로 초기화
    }));
  };

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
      moduleSetPage: newPage,
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
  const openDetailModal = (moduleSet) => {
    setSelectedModuleSet(moduleSet);
    setModalContentType("detail");
    setIsModalOpen(true);
  };

  const openEditModal = (moduleSet) => {
    setSelectedModuleSet(moduleSet);
    setFormData({
      module_set_name: moduleSet.module_set_name,
      description: moduleSet.description || "",
      module_set_images: Array.isArray(moduleSet.module_set_images)
        ? moduleSet.module_set_images.join(", ")
        : moduleSet.module_set_images || "",
      module_set_features: moduleSet.module_set_features || "",
      module_type_id: moduleSet.module_type_id || "",
      options: "[]",
    });
    setModalContentType("edit");
    setIsModalOpen(true);
  };

  const openDeleteModal = (moduleSet) => {
    setSelectedModuleSet(moduleSet);
    setModalContentType("delete");
    setIsModalOpen(true);
  };

  const openAddModal = () => {
    setFormData({
      module_set_name: "",
      description: "",
      module_set_images: "",
      module_set_features: "",
      module_type_id: "",
      options: "[]",
    });
    setModalContentType("add");
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedModuleSet(null);
    setModalContentType(null);
    setIsModalOpen(false);
  };

  // 등록/수정 시 payload 구성 함수 (수정 시 옵션은 보내지 않음)
  const buildPayload = () => {
    const payload = {
      module_set_name: formData.module_set_name,
      description: formData.description,
      module_set_images: formData.module_set_images
        ? formData.module_set_images.split(",").map((s) => s.trim())
        : [],
      module_set_features: formData.module_set_features,
      module_type_id: Number(formData.module_type_id),
    };
    if (modalContentType === "add") {
      try {
        payload.options = JSON.parse(formData.options);
      } catch (e) {
        payload.options = [];
      }
    }
    return payload;
  };

  // 신규 모듈 세트 등록 API 호출
  const handleSaveAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = buildPayload();
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
        closeModal();
      } else {
        setError(
          response.data.message || "모듈 세트를 등록하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 세트를 등록하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 모듈 세트 수정 API 호출
  const handleSaveEdit = async () => {
    if (!selectedModuleSet) return;
    setLoading(true);
    setError("");
    try {
      const payload = buildPayload();
      const response = await axios.patch(
        `${BASE_URL}/admin/module-sets/${selectedModuleSet.module_set_id}`,
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
        closeModal();
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

  // 모듈 세트 삭제 API 호출
  const handleConfirmDelete = async () => {
    if (!selectedModuleSet) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/module-sets/${selectedModuleSet.module_set_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        closeModal();
      } else {
        setError(
          response.data.message || "모듈 세트를 삭제하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 세트를 삭제하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

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
        <p>로딩 중...</p>
      ) : (
        <div className="table-wrapper">
          <table className="module-set-table">
            <thead>
              <tr>
                <th>모듈 세트 ID</th>
                <th>모듈 세트 이름</th>
                <th>설명</th>
                <th>이미지</th>
                <th>상세보기</th>
                <th>특징</th>
                <th>모듈 타입 ID</th>
                <th>수정</th>
                <th>삭제</th>
              </tr>
            </thead>
            <tbody>
              {paginatedModuleSets.length > 0 ? (
                paginatedModuleSets.map((set) => (
                  <tr key={set.module_set_id}>
                    <td>{set.module_set_id}</td>
                    <td>{set.module_set_name}</td>
                    <td>{set.description}</td>
                    <td>
                      {set.module_set_images ? (
                        <img
                          src={
                            Array.isArray(set.module_set_images)
                              ? set.module_set_images[0]
                              : set.module_set_images
                          }
                          alt={set.module_set_name}
                          className="module-set-image"
                        />
                      ) : (
                        "이미지 없음"
                      )}
                    </td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => openDetailModal(set)}
                      >
                        <MdSearch />
                      </button>
                    </td>
                    <td>{set.module_set_features || "-"}</td>
                    <td>{set.module_type_id || "-"}</td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => openEditModal(set)}
                      >
                        <MdEdit />
                      </button>
                    </td>
                    <td>
                      <button
                        className="delete-button"
                        onClick={() => openDeleteModal(set)}
                      >
                        <MdDelete />
                      </button>
                    </td>
                  </tr>
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

      {modalContentType && isModalOpen && (
        <Modal isOpen={isModalOpen} onClose={closeModal} title="모듈 세트 관리">
          {modalContentType === "detail" && selectedModuleSet && (
            <div className="detail-content">
              <h2>모듈 세트 상세 정보</h2>
              <p>
                <strong>모듈 세트 이름:</strong>{" "}
                {selectedModuleSet.module_set_name}
              </p>
              <p>
                <strong>설명:</strong> {selectedModuleSet.description}
              </p>
              <p>
                <strong>특징:</strong> {selectedModuleSet.module_set_features}
              </p>
              <p>
                <strong>모듈 타입 ID:</strong>{" "}
                {selectedModuleSet.module_type_id}
              </p>
              <div className="modal-actions">
                <button
                  onClick={() => openEditModal(selectedModuleSet)}
                  className="edit-button"
                >
                  수정
                </button>
                <button
                  onClick={() => openDeleteModal(selectedModuleSet)}
                  className="delete-button"
                >
                  삭제
                </button>
                <button onClick={closeModal} className="cancel-button">
                  닫기
                </button>
              </div>
            </div>
          )}
          {modalContentType === "add" && (
            <div className="add-content">
              <h2>모듈 세트 등록</h2>
              <form className="add-form">
                <label>
                  모듈 세트 이름:
                  <input
                    type="text"
                    name="module_set_name"
                    value={formData.module_set_name}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  설명:
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  모듈 세트 이미지 (콤마로 구분):
                  <input
                    type="text"
                    name="module_set_images"
                    value={formData.module_set_images}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  모듈 세트 특징:
                  <input
                    type="text"
                    name="module_set_features"
                    value={formData.module_set_features}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  모듈 타입 ID:
                  <input
                    type="number"
                    name="module_type_id"
                    value={formData.module_type_id}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  옵션 (JSON 형식):
                  <textarea
                    name="options"
                    value={formData.options}
                    onChange={handleFormChange}
                    placeholder='[{"option_type_id":201,"quantity":1}]'
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
          {modalContentType === "edit" && selectedModuleSet && (
            <div className="edit-content">
              <h2>모듈 세트 수정</h2>
              <form className="edit-form">
                <label>
                  모듈 세트 이름:
                  <input
                    type="text"
                    name="module_set_name"
                    value={formData.module_set_name}
                    onChange={handleFormChange}
                    required
                  />
                </label>
                <label>
                  설명:
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  모듈 세트 이미지 (콤마로 구분):
                  <input
                    type="text"
                    name="module_set_images"
                    value={formData.module_set_images}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  모듈 세트 특징:
                  <input
                    type="text"
                    name="module_set_features"
                    value={formData.module_set_features}
                    onChange={handleFormChange}
                  />
                </label>
                <label>
                  모듈 타입 ID:
                  <input
                    type="number"
                    name="module_type_id"
                    value={formData.module_type_id}
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
                  onClick={handleSaveEdit}
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
          {modalContentType === "delete" && selectedModuleSet && (
            <div className="delete-content">
              <h2>모듈 세트 삭제 확인</h2>
              <p>정말 이 모듈 세트를 삭제하시겠습니까?</p>
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

export default ModuleSetManagement;
