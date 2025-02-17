import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import AddModal from "./AddModal";
import DeleteModal from "./DeleteModal";
import LoadingSpinner from "./LoadingSpinner";
import { MdEdit, MdDelete, MdSearch } from "react-icons/md";
import "./OptionType.css";

const BASE_URL = import.meta.env.VITE_API_URL;

function OptionTypeManagement() {
  const token = localStorage.getItem("adminToken");

  // 전체 옵션 타입 데이터 및 페이지네이션, 필터, 에러, 로딩 상태
  const [optionTypes, setOptionTypes] = useState([]);
  const [filters, setFilters] = useState({
    search: "",
    page: 1,
    pageSize: 10,
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 행 토글 및 인라인 편집 상태
  const [expandedOptionTypeId, setExpandedOptionTypeId] = useState(null);
  const [editingOptionTypeId, setEditingOptionTypeId] = useState(null);
  const [selectedOptionType, setSelectedOptionType] = useState(null);

  // 등록 및 수정 폼 데이터
  const [formData, setFormData] = useState({
    option_type_name: "",
    option_type_size: "",
    option_type_cost: "",
    description: "",
    option_type_images: "",
    option_type_features: "",
  });

  // 등록 모달 및 삭제 모달 상태
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  // 각 행의 ref (스크롤 이동용)
  const rowRefs = useRef({});
  const detailInfoRef = useRef(null);

  // 새 이미지 파일 상태 (편집 모드에서 이미지 추가 시 사용)
  const [newOptionImage, setNewOptionImage] = useState(null);

  // 옵션 타입 목록 조회 API 호출
  const fetchOptionTypes = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/option-types`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          page: filters.page,
          pageSize: filters.pageSize,
          search: filters.search || undefined,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        setOptionTypes(response.data.data.option_types);
        setPagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "옵션 타입 목록을 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.message || "옵션 타입 목록 조회 중 오류 발생"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOptionTypes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 폼 입력 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // 행 토글 (상세보기/인라인 편집 영역 확장 및 스크롤 이동)
  const toggleExpanded = (optionTypeId) => {
    setExpandedOptionTypeId((prev) =>
      prev === optionTypeId ? null : optionTypeId
    );
    setEditingOptionTypeId(null);
    setTimeout(() => {
      if (rowRefs.current[optionTypeId]) {
        rowRefs.current[optionTypeId].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  // 등록 모달 열기/닫기
  const openAddModal = () => {
    setFormData({
      option_type_name: "",
      option_type_size: "",
      option_type_cost: "",
      description: "",
      option_type_features: "",
    });
    setIsAddModalOpen(true);
  };
  const closeAddModal = () => setIsAddModalOpen(false);

  // 신규 옵션 타입 등록 API 호출
  const handleSubmitAdd = async () => {
    if (
      !formData.option_type_name.trim() ||
      !formData.option_type_cost.trim()
    ) {
      alert("옵션 타입 이름과 기본 가격은 필수 항목입니다.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const payload = {
        option_type_name: formData.option_type_name,
        option_type_size: formData.option_type_size,
        option_type_cost: Number(formData.option_type_cost),
        description: formData.description,
        option_type_features: formData.option_type_features,
      };
      const response = await axios.post(
        `${BASE_URL}/admin/option-types`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchOptionTypes();
        closeAddModal();
      } else {
        setError(response.data.message || "옵션 타입 등록에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "옵션 타입 등록 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  // 인라인 수정 모드 전환: 행의 상세정보 영역에서 "수정" 버튼 클릭 시
  const startEditing = (optionType) => {
    setSelectedOptionType(optionType);
    setFormData({
      option_type_name: optionType.option_type_name,
      option_type_size: optionType.option_type_size,
      option_type_cost: optionType.option_type_cost.toString(),
      description: optionType.description || "",
      option_type_images: Array.isArray(optionType.option_type_images)
        ? optionType.option_type_images.join(", ")
        : optionType.option_type_images || "",
      option_type_features: optionType.option_type_features || "",
    });
    setEditingOptionTypeId(optionType.option_type_id);
    setTimeout(() => {
      if (rowRefs.current[optionType.option_type_id]) {
        rowRefs.current[optionType.option_type_id].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  // 인라인 수정 API 호출
  const handleSubmitEdit = async (optionTypeId) => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        option_type_name: formData.option_type_name,
        option_type_size: formData.option_type_size,
        option_type_cost: Number(formData.option_type_cost),
        description: formData.description,
        option_type_images: formData.option_type_images
          ? formData.option_type_images.split(",").map((url) => url.trim())
          : [],
        option_type_features: formData.option_type_features,
      };
      const response = await axios.patch(
        `${BASE_URL}/admin/option-types/${optionTypeId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchOptionTypes();
        setEditingOptionTypeId(null);
      } else {
        setError(response.data.message || "옵션 타입 수정에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "옵션 타입 수정 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  const cancelEditing = () => {
    setEditingOptionTypeId(null);
  };

  // 삭제 모달 열기/닫기 및 삭제 API 호출
  const openDeleteModal = (optionType) => {
    setSelectedOptionType(optionType);
    setIsDeleteModalOpen(true);
  };
  const closeDeleteModal = () => setIsDeleteModalOpen(false);
  const handleSubmitDelete = async (optionTypeId) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/option-types/${optionTypeId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchOptionTypes();
        closeDeleteModal();
      } else {
        setError(response.data.message || "옵션 타입 삭제에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "옵션 타입 삭제 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  const handleOptionImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setNewOptionImage(e.target.files[0]);
    }
  };

  const handleAddOptionTypeImage = async (optionTypeId) => {
    if (!newOptionImage) {
      alert("이미지 파일을 선택하세요.");
      return;
    }
    const formDataImage = new FormData();
    formDataImage.append("images", newOptionImage);
    try {
      const response = await axios.post(
        `${BASE_URL}/admin/option-types/${optionTypeId}/images`,
        formDataImage,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchOptionTypes();
        setNewOptionImage(null);
      } else {
        alert(response.data.message || "옵션 타입 이미지 추가 실패");
      }
    } catch (err) {
      console.error(err);
      alert("옵션 타입 이미지 추가 중 오류 발생");
    }
  };

  const handleDeleteOptionTypeImage = async (optionTypeId, imageUrl) => {
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/option-types/${optionTypeId}/images`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
          data: { image_url: imageUrl },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchOptionTypes();
      } else {
        alert(response.data.message || "옵션 타입 이미지 삭제 실패");
      }
    } catch (err) {
      console.error(err);
      alert("옵션 타입 이미지 삭제 중 오류 발생");
    }
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  return (
    <div className="option-type-container">
      <div className="option-type-header">
        <h1>옵션 타입 관리</h1>
        <button className="add-button" onClick={openAddModal}>
          옵션 타입 등록
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-wrapper">
          <table className="option-type-table">
            <thead>
              <tr>
                <th>옵션 타입 ID</th>
                <th>옵션 타입 이름</th>
                <th>옵션 타입 크기</th>
                <th>옵션 기본 가격</th>
                <th>설명</th>
                <th>주요 기능</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
              </tr>
            </thead>
            <tbody>
              {optionTypes.length > 0 ? (
                optionTypes.map((ot) => (
                  <React.Fragment key={ot.option_type_id}>
                    <tr
                      ref={(el) => (rowRefs.current[ot.option_type_id] = el)}
                      className={`main-row ${
                        expandedOptionTypeId === ot.option_type_id
                          ? "expanded-main-row"
                          : ""
                      }`}
                      onClick={() => toggleExpanded(ot.option_type_id)}
                    >
                      <td>{ot.option_type_id}</td>
                      <td>
                        <span className="cell-text">{ot.option_type_name}</span>
                      </td>
                      <td>
                        <span className="cell-text">{ot.option_type_size}</span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {Number(ot.option_type_cost).toLocaleString()}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">{ot.description}</span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {ot.option_type_features}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {new Date(ot.created_at).toLocaleString()}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {new Date(ot.updated_at).toLocaleString()}
                        </span>
                      </td>
                    </tr>
                    {expandedOptionTypeId === ot.option_type_id && (
                      <tr className="expanded-row">
                        <td colSpan="10">
                          <div
                            className="detail-info-container"
                            ref={detailInfoRef}
                          >
                            <div className="detail-info">
                              <div className="detail-item">
                                <div className="detail-label">옵션 타입 ID</div>
                                <div className="detail-value">
                                  {ot.option_type_id}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  옵션 타입 이름
                                </div>
                                {editingOptionTypeId === ot.option_type_id ? (
                                  <input
                                    type="text"
                                    name="option_type_name"
                                    value={formData.option_type_name}
                                    onChange={handleFormChange}
                                    className="edit-input"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {ot.option_type_name}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  옵션 타입 크기
                                </div>
                                {editingOptionTypeId === ot.option_type_id ? (
                                  <input
                                    type="text"
                                    name="option_type_size"
                                    value={formData.option_type_size}
                                    onChange={handleFormChange}
                                    className="edit-input"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {ot.option_type_size}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  옵션 기본 가격
                                </div>
                                {editingOptionTypeId === ot.option_type_id ? (
                                  <input
                                    type="number"
                                    name="option_type_cost"
                                    value={formData.option_type_cost}
                                    onChange={handleFormChange}
                                    className="edit-input"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {Number(
                                      ot.option_type_cost
                                    ).toLocaleString()}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">설명</div>
                                {editingOptionTypeId === ot.option_type_id ? (
                                  <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleFormChange}
                                    className="edit-input"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {ot.description}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  옵션 타입 이미지
                                </div>
                                <div className="detail-value">
                                  {ot.option_type_images &&
                                  Array.isArray(ot.option_type_images) &&
                                  ot.option_type_images.length > 0
                                    ? ot.option_type_images.map(
                                        (imgUrl, idx) => (
                                          <div key={idx} className="image-item">
                                            <img
                                              src={imgUrl}
                                              alt={`옵션 이미지 ${idx}`}
                                              className="option-type-image-thumb"
                                            />
                                            {editingOptionTypeId ===
                                              ot.option_type_id && (
                                              <button
                                                onClick={(e) => {
                                                  e.stopPropagation();
                                                  handleDeleteOptionTypeImage(
                                                    ot.option_type_id,
                                                    imgUrl
                                                  );
                                                }}
                                              >
                                                삭제
                                              </button>
                                            )}
                                          </div>
                                        )
                                      )
                                    : "이미지 없음"}
                                  {editingOptionTypeId ===
                                    ot.option_type_id && (
                                    <div className="add-image">
                                      <input
                                        type="file"
                                        onChange={handleOptionImageChange}
                                      />
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleAddOptionTypeImage(
                                            ot.option_type_id
                                          );
                                        }}
                                      >
                                        이미지 추가
                                      </button>
                                    </div>
                                  )}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">주요 기능</div>
                                {editingOptionTypeId === ot.option_type_id ? (
                                  <input
                                    type="text"
                                    name="option_type_features"
                                    value={formData.option_type_features}
                                    onChange={handleFormChange}
                                    className="edit-input"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {ot.option_type_features}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">등록 일시</div>
                                <div className="detail-value">
                                  {ot.created_at}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">등록자</div>
                                <div className="detail-value">
                                  {ot.created_by}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">수정 일시</div>
                                <div className="detail-value">
                                  {ot.updated_at}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">수정자</div>
                                <div className="detail-value">
                                  {ot.updated_by}
                                </div>
                              </div>
                            </div>
                            <div className="detail-actions">
                              {editingOptionTypeId === ot.option_type_id ? (
                                <>
                                  <button
                                    className="detail-save-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleSubmitEdit(ot.option_type_id);
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
                                      startEditing(ot);
                                    }}
                                  >
                                    <MdEdit />
                                  </button>
                                  <button
                                    className="detail-delete-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      openDeleteModal(ot);
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
                  <td colSpan="10">조회된 옵션 타입이 없습니다.</td>
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
        </div>
      )}
      <AddModal
        isOpen={isAddModalOpen}
        onClose={closeAddModal}
        onSubmit={handleSubmitAdd}
        title="신규 옵션 타입 등록"
      >
        <div className="form-group">
          <label>옵션 타입 이름</label>
          <input
            type="text"
            name="option_type_name"
            placeholder="예: Option A"
            value={formData.option_type_name}
            onChange={handleFormChange}
            required
          />
        </div>
        <div className="form-group">
          <label>옵션 타입 크기</label>
          <input
            type="text"
            name="option_type_size"
            placeholder="예: Small"
            value={formData.option_type_size}
            onChange={handleFormChange}
            required
          />
        </div>
        <div className="form-group">
          <label>옵션 기본 가격</label>
          <input
            type="number"
            name="option_type_cost"
            placeholder="예: 1000"
            value={formData.option_type_cost}
            onChange={handleFormChange}
            required
          />
        </div>
        <div className="form-group">
          <label>설명</label>
          <textarea
            name="description"
            placeholder="옵션 타입에 대한 설명"
            value={formData.description}
            onChange={handleFormChange}
          />
        </div>
        <div className="form-group">
          <label>주요 기능</label>
          <input
            type="text"
            name="option_type_features"
            placeholder="예: 기능1, 기능2"
            value={formData.option_type_features}
            onChange={handleFormChange}
          />
        </div>
      </AddModal>

      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onDelete={() => handleSubmitDelete(selectedOptionType.option_type_id)}
        title="옵션 타입 삭제 확인"
        message={
          selectedOptionType
            ? `${selectedOptionType.option_type_name} 옵션 타입을 삭제하시겠습니까?`
            : ""
        }
      />
    </div>
  );
}

export default OptionTypeManagement;
