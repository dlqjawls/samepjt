// src/admin/components/ModuleSetManagement.jsx
// 수정 중........

import React, { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import AddModal from "./AddModal";
import DeleteModal from "./DeleteModal";
import { MdEdit, MdDelete } from "react-icons/md";
import "./ModuleSetManagement.css";
import LoadingSpinner from "./LoadingSpinner";

const BASE_URL = import.meta.env.VITE_API_URL;

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
    // 아래는 편집 모드에서만 사용된다.
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

  // 모듈 타입 목록
  const [moduleTypes, setModuleTypes] = useState([]);
  // 옵션 타입 목록
  const [optionTypes, setOptionTypes] = useState([]);
  // 편집 모드에서 추가할 이미지 파일
  const [newImage, setNewImage] = useState(null);
  // 편집 모드에서 추가할 옵션 정보
  const [newOption, setNewOption] = useState({
    option_type_id: "",
    quantity: "",
  });

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
        params: {
          page: filters.moduleSetPage,
          pageSize: filters.moduleSetPageSize,
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
  }, [token, filters.moduleSetPage, filters.moduleSetPageSize]);

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

  // 옵션 타입 목록 조회
  const fetchOptionTypes = useCallback(async () => {
    try {
      const response = await axios.get(
        `${BASE_URL}/admin/option-types?page=1&pageSize=100`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        setOptionTypes(response.data.data.option_types);
      } else {
        console.error("옵션 타입 목록 불러오기 실패:", response.data.message);
      }
    } catch (err) {
      console.error("옵션 타입 목록 조회 중 오류:", err);
    }
  }, [token]);

  useEffect(() => {
    fetchOptionTypes();
  }, [fetchOptionTypes]);

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
      module_set_features: "",
      module_type_id: "",
    });
    setIsAddModalOpen(true);
  };
  const closeAddModal = () => setIsAddModalOpen(false);

  // 신규 모듈 세트 등록 API 호출
  const handleSubmitAdd = async () => {
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
        module_set_features: formData.module_set_features,
        module_type_id: Number(formData.module_type_id),
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
      module_set_features: moduleSet.module_set_features,
      module_type_id: Number(moduleSet.module_type_id),
      module_set_images: Array.isArray(moduleSet.module_set_images)
        ? moduleSet.module_set_images.join(", ")
        : moduleSet.module_set_images || "",
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
        module_set_features: formData.module_set_features,
        module_type_id: Number(formData.module_type_id),
      };
      if (formData.module_set_images.trim()) {
        payload.module_set_images = formData.module_set_images
          .split(",")
          .map((s) => s.trim());
      }
      if (formData.options.trim() && formData.options !== "[]") {
        try {
          payload.options = JSON.parse(formData.options);
        } catch (e) {
          payload.options = [];
        }
      }
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

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setNewImage(e.target.files[0]);
    }
  };

  const handleAddImage = async (moduleSetId) => {
    if (!newImage) {
      alert("이미지 파일을 선택하세요.");
      return;
    }
    const formDataImage = new FormData();
    formDataImage.append("images", newImage);
    try {
      const response = await axios.post(
        `${BASE_URL}/admin/module-sets/${moduleSetId}/images`,
        formDataImage,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        setNewImage(null);
      } else {
        alert(response.data.message || "이미지 추가 실패");
      }
    } catch (err) {
      console.error(err);
      alert("이미지 추가 중 오류 발생");
    }
  };

  const handleDeleteImage = async (moduleSetId, imageUrl) => {
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/module-sets/${moduleSetId}/images`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          data: { image_url: imageUrl },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
      } else {
        alert(response.data.message || "이미지 삭제 실패");
      }
    } catch (err) {
      console.error(err);
      alert("이미지 삭제 중 오류 발생");
    }
  };

  const handleAddOption = async (moduleSetId) => {
    if (!newOption.option_type_id || !newOption.quantity) {
      alert("옵션 타입과 수량을 입력하세요.");
      return;
    }
    try {
      const response = await axios.post(
        `${BASE_URL}/admin/module-sets/${moduleSetId}/options`,
        {
          option_type_id: Number(newOption.option_type_id),
          quantity: Number(newOption.quantity),
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        setNewOption({ option_type_id: "", quantity: "" });
      } else {
        alert(response.data.message || "옵션 추가 실패");
      }
    } catch (err) {
      console.error(err);
      alert("옵션 추가 중 오류 발생");
    }
  };

  const handleDeleteOption = async (moduleSetId, optionTypeId) => {
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/module-sets/${moduleSetId}/options/${optionTypeId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
      } else {
        alert(response.data.message || "옵션 삭제 실패");
      }
    } catch (err) {
      console.error(err);
      alert("옵션 삭제 중 오류 발생");
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
                <th>모듈 타입 정보</th>
                <th>가격</th>
              </tr>
            </thead>
            <tbody>
              {moduleSets.length > 0 ? (
                moduleSets.map((set) => (
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
                          {set.description || "설명 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {set.module_set_features || "특징 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {(() => {
                            const mt = moduleTypes.find(
                              (m) => m.module_type_id === set.module_type_id
                            );
                            return mt
                              ? `${mt.module_type_name} (크기: ${mt.module_type_size}, ${mt.module_type_cost}원)`
                              : set.module_type_id;
                          })()}
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
                              {/* 기본 상세 정보 */}
                              <div className="detail-item">
                                <div className="detail-label">모듈 세트 ID</div>
                                <div className="detail-value">
                                  {set.module_set_id}
                                </div>
                              </div>
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
                                    {set.description || "설명 없음"}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  모듈 세트 이미지
                                </div>
                                <div className="detail-value">
                                  {set.module_set_images &&
                                  Array.isArray(set.module_set_images) &&
                                  set.module_set_images.length > 0 ? (
                                    <img
                                      src={set.module_set_images[0]}
                                      alt={set.module_set_name}
                                      className="module-set-image"
                                    />
                                  ) : (
                                    "이미지 없음"
                                  )}
                                </div>
                                {editingModuleSetId === set.module_set_id && (
                                  <div className="edit-section">
                                    <h3>이미지 관리</h3>
                                    <div className="image-list">
                                      {set.module_set_images &&
                                      Array.isArray(set.module_set_images) &&
                                      set.module_set_images.length > 0 ? (
                                        set.module_set_images.map(
                                          (imgUrl, idx) => (
                                            <div
                                              key={idx}
                                              className="image-item"
                                            >
                                              <img
                                                src={imgUrl}
                                                alt={`이미지 ${idx}`}
                                                className="module-set-image-thumb"
                                              />
                                              <button
                                                onClick={(e) => {
                                                  e.stopPropagation();
                                                  handleDeleteImage(
                                                    set.module_set_id,
                                                    imgUrl
                                                  );
                                                }}
                                              >
                                                삭제
                                              </button>
                                            </div>
                                          )
                                        )
                                      ) : (
                                        <p>등록된 이미지가 없습니다.</p>
                                      )}
                                    </div>
                                    <div className="add-image">
                                      <input
                                        type="file"
                                        onChange={handleImageChange}
                                      />
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleAddImage(set.module_set_id);
                                        }}
                                      >
                                        이미지 추가
                                      </button>
                                    </div>
                                  </div>
                                )}
                              </div>

                              <div className="detail-item">
                                <div className="detail-label">
                                  모듈 세트에 포함된 옵션
                                </div>
                                <div className="detail-value">
                                  <div className="option-list">
                                    {set.module_set_option_types &&
                                    set.module_set_option_types.length > 0 ? (
                                      set.module_set_option_types.map((opt) => (
                                        <div
                                          key={opt.option_type_id}
                                          className="option-item"
                                        >
                                          <span>
                                            {opt.option_type_name} (수량:{" "}
                                            {opt.quantity})
                                          </span>
                                          {editingModuleSetId ===
                                            set.module_set_id && (
                                            <button
                                              onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteOption(
                                                  set.module_set_id,
                                                  opt.option_type_id
                                                );
                                              }}
                                            >
                                              삭제
                                            </button>
                                          )}
                                        </div>
                                      ))
                                    ) : (
                                      <p>등록된 옵션이 없습니다.</p>
                                    )}
                                  </div>
                                </div>
                                {editingModuleSetId === set.module_set_id && (
                                  <div className="add-option">
                                    <select
                                      value={newOption.option_type_id}
                                      onChange={(e) =>
                                        setNewOption((prev) => ({
                                          ...prev,
                                          option_type_id: e.target.value,
                                        }))
                                      }
                                    >
                                      <option value="">옵션 타입 선택</option>
                                      {optionTypes.map((opt) => (
                                        <option
                                          key={opt.option_type_id}
                                          value={opt.option_type_id}
                                        >
                                          {opt.option_type_name}
                                        </option>
                                      ))}
                                    </select>
                                    <input
                                      type="number"
                                      placeholder="수량"
                                      value={newOption.quantity}
                                      onChange={(e) =>
                                        setNewOption((prev) => ({
                                          ...prev,
                                          quantity: e.target.value,
                                        }))
                                      }
                                    />
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleAddOption(set.module_set_id);
                                      }}
                                    >
                                      옵션 추가
                                    </button>
                                  </div>
                                )}
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
                                    {set.module_set_features || "특징 없음"}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">모듈 타입</div>
                                {editingModuleSetId === set.module_set_id ? (
                                  <select
                                    name="module_type_id"
                                    value={formData.module_type_id}
                                    onChange={handleFormChange}
                                    className="edit-module-type-id"
                                  >
                                    <option value="">선택하세요</option>
                                    {moduleTypes.map((mt) => (
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
                                      const mt = moduleTypes.find(
                                        (m) =>
                                          m.module_type_id ===
                                          set.module_type_id
                                      );
                                      return mt
                                        ? `${mt.module_type_name} (크기: ${mt.module_type_size}, ${mt.module_type_cost}원)`
                                        : set.module_type_id;
                                    })()}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">가격</div>
                                <div className="detail-value">
                                  {set.price ? set.price : 0}
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
          <label>모듈 타입</label>
          <select
            name="module_type_id"
            value={formData.module_type_id}
            onChange={handleFormChange}
            required
          >
            <option value="">선택하세요</option>
            {moduleTypes.map((mt) => (
              <option key={mt.module_type_id} value={mt.module_type_id}>
                {mt.module_type_name} ({mt.module_type_size},{" "}
                {mt.module_type_cost})
              </option>
            ))}
          </select>
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
