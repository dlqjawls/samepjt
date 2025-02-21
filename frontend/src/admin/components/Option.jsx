// src/admin/components/Option.jsx

import React, { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import AddModal from "./AddModal";
import DeleteModal from "./DeleteModal";
import LoadingSpinner from "./LoadingSpinner";
import { MdEdit, MdDelete } from "react-icons/md";
import "./Option.css";

const BASE_URL = import.meta.env.VITE_API_URL;

function Option() {
  const token = localStorage.getItem("adminToken");

  // 화면에 표시할 옵션 데이터 (필터링 및 클라이언트 단 페이지네이션 적용)
  const [options, setOptions] = useState([]);
  // 페이지네이션 상태 (클라이언트 단 계산)
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  // 로딩 및 오류 상태
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 토글(확장) 및 인라인 편집 상태
  const [expandedOptionId, setExpandedOptionId] = useState(null);
  const [editingOptionId, setEditingOptionId] = useState(null);
  const [selectedOption, setSelectedOption] = useState(null);

  // 등록 모달 상태
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  // 삭제 모달 상태
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  // 인라인 편집 폼 데이터
  const [formData, setFormData] = useState({
    option_type_id: "",
  });

  // 각 행의 ref들을 저장 (스크롤 이동용)
  const rowRefs = useRef({});
  const detailInfoRef = useRef(null);

  // 옵션 타입 목록
  const [optionTypes, setOptionTypes] = useState([]);

  // 필터 상태 (검색어와 상태)
  const [filters, setFilters] = useState({
    search: "",
    status: "",
    // 페이지 및 페이지당 항목수는 클라이언트 단에서 계산합니다.
    page: 1,
    pageSize: 10,
  });

  const fetchOptions = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/options`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          page: filters.page,
          pageSize: filters.pageSize,
          search: filters.search || undefined,
          status: filters.status || undefined,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        setOptions(response.data.data.options);
        setPagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "옵션 목록을 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("옵션 목록을 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 전체 옵션 데이터를 처음 받아옴
  useEffect(() => {
    fetchOptions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

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

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
      page: newPage,
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

  // 행 토글 (상세보기 및 인라인 편집 영역 확장/축소)
  const toggleExpanded = (optionId) => {
    setExpandedOptionId((prev) => (prev === optionId ? null : optionId));
    setEditingOptionId(null);
    setTimeout(() => {
      if (rowRefs.current[optionId]) {
        rowRefs.current[optionId].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  // 인라인 편집 모드 전환
  const startEditing = (option) => {
    setSelectedOption(option);
    setFormData({ option_type_id: option.option_type_id.toString() });
    setEditingOptionId(option.option_id);
    setTimeout(() => {
      if (rowRefs.current[option.option_id]) {
        rowRefs.current[option.option_id].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  const cancelEditing = () => {
    setEditingOptionId(null);
  };

  const openAddModal = () => {
    setFormData({ option_type_id: "" });
    setIsAddModalOpen("add");
  };
  const closeAddModal = () => setIsAddModalOpen(false);

  // 신규 옵션 등록 API 호출
  const handleSubmitAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = { option_type_id: Number(formData.option_type_id) };
      const response = await axios.post(`${BASE_URL}/admin/options`, payload, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        // 전체 옵션 데이터를 새로 받아옴
        await fetchOptions();
        closeAddModal();
      } else {
        setError(response.data.message || "옵션 등록에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("옵션 등록 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 인라인 수정 API 호출 (현재는 쓰지 않는다.)
  // const handleSubmitEdit = async (optionId) => {
  //   setLoading(true);
  //   setError("");
  //   try {
  //     const payload = {
  //       option_type_id: Number(formData.option_type_id),
  //     };
  //     const response = await axios.patch(
  //       `${BASE_URL}/admin/options/${optionId}`,
  //       payload,
  //       {
  //         headers: {
  //           "Content-Type": "application/json",
  //           Authorization: token ? `Bearer ${token}` : undefined,
  //         },
  //       }
  //     );
  //     if (response.data.resultCode === "SUCCESS") {
  //       await fetchOptions();
  //       setEditingOptionId(null);
  //     } else {
  //       setError(response.data.message || "옵션 수정 실패");
  //     }
  //   } catch (err) {
  //     console.error(err);
  //     setError("옵션 수정 중 오류 발생");
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  // 삭제 모달 열기
  const openDeleteModal = (vehicle) => {
    setSelectedOption(vehicle);
    setIsDeleteModalOpen(true);
  };
  const closeDeleteModal = () => setIsDeleteModalOpen(false);

  // 삭제 API 호출
  const handleSubmitDelete = async (optionId) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/options/${optionId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchOptions();
        closeDeleteModal();
      } else {
        setError(response.data.message || "옵션 삭제 실패");
      }
    } catch (err) {
      console.error(err);
      setError("옵션 삭제 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="option-container">
      <div className="option-header">
        <h1>옵션</h1>
        <button className="add-button" onClick={openAddModal}>
          옵션 등록
        </button>
      </div>
      {/* 옵션 목록 테이블 */}
      {error && <p className="error">{error}</p>}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-wrapper">
          <table className="option-table">
            <thead>
              <tr>
                <th>옵션 ID</th>
                <th>옵션 타입 ID</th>
                <th>상태</th>
                <th>마지막 정비 일자</th>
                <th>다음 정비 일자</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
              </tr>
            </thead>
            <tbody>
              {options.length > 0 ? (
                options.map((option) => (
                  <React.Fragment key={option.option_id}>
                    <tr
                      ref={(el) => (rowRefs.current[option.option_id] = el)}
                      className={`main-row ${
                        expandedOptionId === option.option_id
                          ? "expanded-main-row"
                          : ""
                      }`}
                      onClick={() => toggleExpanded(option.option_id)}
                    >
                      <td>
                        <span className="cell-text">{option.option_id}</span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {option.option_type_id}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {option.item_status_name === "active"
                            ? "활성화"
                            : option.item_status_name === "inactive"
                            ? "비활성화"
                            : option.item_status_name === "maintenance"
                            ? "정비 중"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {option.last_maintenance_at
                            ? new Date(
                                option.last_maintenance_at
                              ).toLocaleString()
                            : "미정"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {option.next_maintenance_at
                            ? new Date(
                                option.next_maintenance_at
                              ).toLocaleString()
                            : "미정"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {new Date(option.created_at).toLocaleString()}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {new Date(option.updated_at).toLocaleString()}
                        </span>
                      </td>
                    </tr>
                    {expandedOptionId === option.option_id && (
                      <tr className="expanded-row">
                        <td colSpan="8">
                          <div
                            className="detail-info-container"
                            ref={detailInfoRef}
                          >
                            <div className="detail-info">
                              <div className="detail-item">
                                <div className="detail-label">옵션 ID</div>
                                <div className="detail-value">
                                  {option.option_id}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">옵션 타입 ID</div>
                                {editingOptionId === option.option_id ? (
                                  <input
                                    type="number"
                                    name="option_type_id"
                                    value={formData.option_type_id}
                                    onChange={handleFormChange}
                                    className="option-container__edit-input"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {option.option_type_id}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">상태</div>
                                <div className="detail-value">
                                  {option.item_status_name === "active"
                                    ? "활성화"
                                    : option.item_status_name === "inactive"
                                    ? "비활성화"
                                    : option.item_status_name === "maintenance"
                                    ? "정비 중"
                                    : "알 수 없음"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  마지막 정비 일자
                                </div>
                                <div className="detail-value">
                                  {option.last_maintenance_at
                                    ? new Date(
                                        option.last_maintenance_at
                                      ).toLocaleString()
                                    : "미정"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  다음 정비 일자
                                </div>
                                <div className="detail-value">
                                  {option.next_maintenance_at
                                    ? new Date(
                                        option.next_maintenance_at
                                      ).toLocaleString()
                                    : "미정"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">등록 일자</div>
                                <div className="detail-value">
                                  {new Date(option.created_at).toLocaleString()}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">등록자</div>
                                <div className="detail-value">
                                  {option.created_by}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">수정 일자</div>
                                <div className="detail-value">
                                  {new Date(option.updated_at).toLocaleString()}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">수정자</div>
                                <div className="detail-value">
                                  {option.updated_by}
                                </div>
                              </div>
                            </div>
                            <div className="detail-actions">
                              {editingOptionId === option.option_id ? (
                                <>
                                  <button
                                    className="detail-save-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      // handleSubmitEdit(option.option_id);
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
                                  {/* <button
                                    className="detail-edit-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      startEditing(option);
                                    }}
                                  >
                                    <MdEdit />
                                  </button> */}
                                  <button
                                    className="detail-delete-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      openDeleteModal(option);
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
                  <td colSpan="8">조회된 옵션이 없습니다.</td>
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
        title="신규 옵션 등록"
      >
        <div className="form-group">
          <label>옵션 타입</label>
          <select
            name="option_type_id"
            value={formData.option_type_id}
            onChange={handleFormChange}
            required
            className="add-option-type"
          >
            <option value="">옵션 타입 선택</option>
            {optionTypes &&
              optionTypes.map((opt) => (
                <option key={opt.option_type_id} value={opt.option_type_id}>
                  {opt.option_type_name}
                </option>
              ))}
          </select>
        </div>
      </AddModal>

      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onDelete={() => handleSubmitDelete(selectedOption.option_id)}
        title="옵션 삭제 확인"
        message={
          selectedOption
            ? `${selectedOption.option_id} 옵션을 삭제하시겠습니까?`
            : ""
        }
      />
    </div>
  );
}

export default Option;
