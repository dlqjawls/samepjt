import React, { useState, useEffect } from "react";
import axios from "axios";
import Modal from "./Modal";
import { MdSearch } from "react-icons/md";
import "./OptionType.css";

function OptionTypeManagement() {
  const token = localStorage.getItem("adminToken");
  const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

  // 전체 옵션 타입 목록 및 페이지네이션 (백엔드 처리)
  const [optionTypes, setOptionTypes] = useState([]);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 프론트엔드 검색 필터 (옵션 타입 이름으로 필터링)
  const [searchFilter, setSearchFilter] = useState("");

  // 백엔드에서 받은 옵션 타입 목록은 그대로 사용하고,
  // 프론트엔드에서 검색 필터를 적용하여 화면에 표시할 데이터 계산
  const [displayOptionTypes, setDisplayOptionTypes] = useState([]);

  // 모달 관련 상태 (modalType: "add", "detail", "edit", "delete")
  const [modalType, setModalType] = useState(null);
  const [selectedOptionType, setSelectedOptionType] = useState(null);

  // 폼 데이터 (등록/수정 시 사용)
  const [formData, setFormData] = useState({
    option_type_name: "",
    option_type_size: "",
    option_type_cost: "",
    description: "",
    option_type_images: "", // 콤마로 구분된 URL 문자열 → 배열로 변환
    option_type_features: "",
  });

  // 옵션 타입 목록 조회 (GET /admin/option-types)
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
          page: pagination.currentPage,
          pageSize: pagination.pageSize,
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
      setError("옵션 타입 목록을 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 및 pagination 변경 시 옵션 타입 목록 재조회
  useEffect(() => {
    fetchOptionTypes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.currentPage, pagination.pageSize]);

  // 프론트엔드 검색 필터 적용
  useEffect(() => {
    if (!searchFilter) {
      setDisplayOptionTypes(optionTypes);
    } else {
      const filtered = optionTypes.filter((ot) =>
        ot.option_type_name.toLowerCase().includes(searchFilter.toLowerCase())
      );
      setDisplayOptionTypes(filtered);
    }
  }, [searchFilter, optionTypes]);

  // 필터 입력 변경 핸들러
  const handleSearchChange = (e) => {
    setSearchFilter(e.target.value);
  };

  // 페이지 변경 핸들러 (백엔드 페이지네이션)
  const handlePageChange = (newPage) => {
    setPagination((prev) => ({
      ...prev,
      currentPage: newPage,
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

  // 모달 열기 함수들
  const openDetailModal = (optionType) => {
    setSelectedOptionType(optionType);
    setModalType("detail");
  };

  const openAddModal = () => {
    setFormData({
      option_type_name: "",
      option_type_size: "",
      option_type_cost: "",
      description: "",
      option_type_images: "",
      option_type_features: "",
    });
    setModalType("add");
  };

  const openEditModal = (optionType) => {
    setSelectedOptionType(optionType);
    setFormData({
      option_type_name: optionType.option_type_name,
      option_type_size: optionType.option_type_size,
      option_type_cost: optionType.option_type_cost,
      description: optionType.description || "",
      option_type_images: Array.isArray(optionType.option_type_images)
        ? optionType.option_type_images.join(", ")
        : optionType.option_type_images || "",
      option_type_features: optionType.option_type_features || "",
    });
    setModalType("edit");
  };

  const openDeleteModal = (optionType) => {
    setSelectedOptionType(optionType);
    setModalType("delete");
  };

  const closeModal = () => {
    setModalType(null);
    setSelectedOptionType(null);
    setFormData({
      option_type_name: "",
      option_type_size: "",
      option_type_cost: "",
      description: "",
      option_type_images: "",
      option_type_features: "",
    });
    setError("");
  };

  // 신규 옵션 타입 등록 API 호출 (POST /admin/option-types)
  const handleSaveAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        option_type_name: formData.option_type_name,
        option_type_size: formData.option_type_size,
        option_type_cost: Number(formData.option_type_cost),
        description: formData.description,
        option_type_images: formData.option_type_images
          ? formData.option_type_images.split(";;;").map((url) => url.trim())
          : [],
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
        fetchOptionTypes();
        closeModal();
      } else {
        setError(response.data.message || "옵션 타입 등록에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("옵션 타입 등록 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 옵션 타입 수정 API 호출 (PATCH /admin/option-types/{option_type_id})
  const handleSaveEdit = async () => {
    if (!selectedOptionType) return;
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
        `${BASE_URL}/admin/option-types/${selectedOptionType.option_type_id}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchOptionTypes();
        closeModal();
      } else {
        setError(response.data.message || "옵션 타입 수정에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("옵션 타입 수정 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 옵션 타입 삭제 API 호출 (DELETE /admin/option-types/{option_type_id})
  const handleConfirmDelete = async () => {
    if (!selectedOptionType) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/option-types/${selectedOptionType.option_type_id}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchOptionTypes();
        closeModal();
      } else {
        setError(response.data.message || "옵션 타입 삭제에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("옵션 타입 삭제 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="option-type-container">
      <div className="option-type-header">
        <h1>옵션 타입</h1>
        <button className="add-button" onClick={openAddModal}>
          옵션 타입 등록
        </button>
      </div>

      {/* 필터링 섹션: 옵션 타입 이름으로 검색 */}
      {/* <div className="filters">
        <label>
          검색
          <input
            type="text"
            name="search"
            value={searchFilter}
            onChange={handleSearchChange}
            placeholder="옵션 타입 이름 검색"
          />
        </label>
        <button onClick={() => setSearchFilter(searchFilter)}>검색</button>
      </div> */}

      {loading ? (
        <p>로딩 중...</p>
      ) : error ? (
        <p className="error">{error}</p>
      ) : (
        <>
          <table className="option-type-table">
            <thead>
              <tr>
                <th>옵션 타입 ID</th>
                <th>옵션 타입 이름</th>
                <th>옵션 타입 크기</th>
                <th>옵션 기본 가격</th>
                <th>설명</th>
                <th>이미지 URL</th>
                <th>주요 기능</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
                <th>상세 보기</th>
              </tr>
            </thead>
            <tbody>
              {optionTypes.length > 0 ? (
                // 백엔드에서 반환된 옵션 타입 목록 중, 프론트엔드 검색 필터를 적용합니다.
                optionTypes
                  .filter((ot) =>
                    ot.option_type_name
                      .toLowerCase()
                      .includes(searchFilter.toLowerCase())
                  )
                  .map((ot) => (
                    <tr key={ot.option_type_id}>
                      <td>{ot.option_type_id}</td>
                      <td>{ot.option_type_name}</td>
                      <td>{ot.option_type_size}</td>
                      <td>{ot.option_type_cost.toLocaleString()}</td>
                      <td>{ot.description}</td>
                      <td>{ot.option_type_images}</td>
                      <td>{ot.option_type_features}</td>
                      <td>{new Date(ot.created_at).toLocaleString()}</td>
                      <td>{new Date(ot.updated_at).toLocaleString()}</td>
                      <td>
                        <button
                          className="detail-button"
                          onClick={() => openDetailModal(ot)}
                        >
                          <MdSearch />
                        </button>
                      </td>
                    </tr>
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
        </>
      )}

      {/* 모달 */}
      <Modal isOpen={modalType !== null} onClose={closeModal}>
        {/* 상세 정보 모달 */}
        {modalType === "detail" && selectedOptionType && (
          <div className="detail-content">
            <h2>옵션 타입 상세 정보</h2>
            <p>옵션 타입 ID: {selectedOptionType.option_type_id}</p>
            <p>옵션 타입 이름: {selectedOptionType.option_type_name}</p>
            <p>옵션 타입 크기: {selectedOptionType.option_type_size}</p>
            <p>
              옵션 기본 가격:{" "}
              {selectedOptionType.option_type_cost.toLocaleString()}
            </p>
            <p>설명: {selectedOptionType.description}</p>
            <p>이미지 URL: {selectedOptionType.option_type_images}</p>
            <p>주요 기능: {selectedOptionType.option_type_features}</p>
            <p>
              등록 일자:{" "}
              {new Date(selectedOptionType.created_at).toLocaleString()}
            </p>
            <p>
              수정 일자:{" "}
              {new Date(selectedOptionType.updated_at).toLocaleString()}
            </p>
            <div className="modal-actions">
              <button
                onClick={() => openEditModal(selectedOptionType)}
                className="edit-button"
              >
                수정
              </button>
              <button
                onClick={() => openDeleteModal(selectedOptionType)}
                className="delete-button"
              >
                삭제
              </button>
            </div>
          </div>
        )}

        {/* 수정 모달 */}
        {modalType === "edit" && selectedOptionType && (
          <div className="edit-content">
            <h2>옵션 타입 수정</h2>
            <form className="edit-form">
              <label>
                옵션 타입 이름:
                <input
                  type="text"
                  name="option_type_name"
                  value={formData.option_type_name}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 타입 크기:
                <input
                  type="text"
                  name="option_type_size"
                  value={formData.option_type_size}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 기본 가격:
                <input
                  type="number"
                  name="option_type_cost"
                  value={formData.option_type_cost}
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
                이미지 URL 목록 (콤마로 구분):
                <input
                  type="text"
                  name="option_type_images"
                  value={formData.option_type_images}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                주요 기능:
                <input
                  type="text"
                  name="option_type_features"
                  value={formData.option_type_features}
                  onChange={handleFormChange}
                />
              </label>
            </form>
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

        {/* 삭제 확인 모달 */}
        {modalType === "delete" && selectedOptionType && (
          <div className="delete-content">
            <h2>옵션 타입 삭제 확인</h2>
            <p>정말로 이 옵션 타입을 삭제하시겠습니까?</p>
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
            <h2>신규 옵션 타입 등록</h2>
            <form className="add-form">
              <label>
                옵션 타입 이름:
                <input
                  type="text"
                  name="option_type_name"
                  value={formData.option_type_name}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 타입 크기:
                <input
                  type="text"
                  name="option_type_size"
                  value={formData.option_type_size}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 기본 가격:
                <input
                  type="number"
                  name="option_type_cost"
                  value={formData.option_type_cost}
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
                이미지 URL 목록 (콤마로 구분):
                <input
                  type="text"
                  name="option_type_images"
                  value={formData.option_type_images}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                주요 기능:
                <input
                  type="text"
                  name="option_type_features"
                  value={formData.option_type_features}
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

export default OptionTypeManagement;
