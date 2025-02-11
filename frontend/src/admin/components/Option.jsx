// src/components/Option.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import Modal from "./Modal";
import { MdSearch } from "react-icons/md";
import "./Option.css";

function Option() {
  const token = localStorage.getItem("adminToken");
  const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

  // 전체 옵션 데이터를 백엔드에서 받아와 저장 (전체 데이터)
  const [allOptions, setAllOptions] = useState([]);
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

  // 필터 상태 (검색어와 상태)
  const [filters, setFilters] = useState({
    search: "",
    status: "",
    // 페이지 및 페이지당 항목수는 클라이언트 단에서 계산합니다.
    page: 1,
    pageSize: 10,
  });

  // 모달 관련 상태
  // modalType: "add", "detail", "edit", "delete"
  const [modalType, setModalType] = useState(null);
  const [selectedOption, setSelectedOption] = useState(null);
  // Add 모달: 신규 등록 시 option_type_id만 입력받음
  const [formData, setFormData] = useState({
    option_type_id: "",
  });

  // 전체 옵션 데이터를 API로부터 가져오기
  // (전체 데이터를 받아오기 위해 페이지네이션 파라미터는 보내지 않거나 매우 큰 pageSize를 사용)
  const fetchAllOptions = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/options`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        // 백엔드에서 전체 데이터를 반환하도록 pageSize를 크게 설정하거나,
        // 혹은 필터 파라미터 없이 호출 (API 구현에 따라 조정)
        params: {
          page: 1,
          pageSize: 1000,
        },
      });
      if (response.data.resultCode === "SUCCESS") {
        setAllOptions(response.data.data.options);
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
    fetchAllOptions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 전체 옵션 데이터와 필터(검색어, 상태)를 기준으로 필터링 및 클라이언트 단 페이지네이션 계산
  useEffect(() => {
    let filtered = allOptions;
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      // 여기서는 옵션 타입 ID를 문자열로 검색합니다.
      filtered = filtered.filter((option) =>
        String(option.option_type_id).toLowerCase().includes(searchLower)
      );
    }
    if (filters.status) {
      filtered = filtered.filter((option) => option.status === filters.status);
    }
    const total = filtered.length;
    const totalPages = Math.ceil(total / filters.pageSize) || 1;
    setPagination({
      currentPage: filters.page,
      totalPages: totalPages,
      totalItems: total,
      pageSize: filters.pageSize,
    });
    const startIndex = (filters.page - 1) * filters.pageSize;
    const paginated = filtered.slice(startIndex, startIndex + filters.pageSize);
    setOptions(paginated);
  }, [filters, allOptions]);

  // 필터 입력 변경 핸들러
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      // 검색어나 상태 변경 시 첫 페이지로 리셋
      ...(name === "search" || name === "status" ? { page: 1 } : {}),
    }));
  };

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

  // 모달 열기 함수
  const openDetailModal = (option) => {
    setSelectedOption(option);
    setModalType("detail");
  };

  // 신규 옵션 등록 모달 (Add)
  // 등록 시에는 option_type_id만 입력받음 (기본 상태는 inactive로 등록)
  const openAddModal = () => {
    setFormData({ option_type_id: "" });
    setModalType("add");
  };

  // 옵션 삭제 모달 (Delete)
  const openDeleteModal = (option) => {
    setSelectedOption(option);
    setModalType("delete");
  };

  const closeModal = () => {
    setModalType(null);
    setSelectedOption(null);
    setFormData({
      option_type_id: "",
      status: "",
      last_maintenance_at: "",
      next_maintenance_at: "",
    });
    setError("");
  };

  // 신규 옵션 등록 API 호출 (POST /admin/options)
  const handleSaveAdd = async () => {
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
        fetchAllOptions();
        closeModal();
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

  // 옵션 삭제 API 호출 (DELETE /admin/options/{option_id})
  const handleConfirmDelete = async () => {
    if (!selectedOption) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/options/${selectedOption.option_id}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        fetchAllOptions();
        closeModal();
      } else {
        setError(response.data.message || "옵션 삭제에 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      setError("옵션 삭제 중 오류가 발생했습니다.");
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

      {/* 필터링 섹션 */}
      {/* <div className="filters">
        <label>
          검색
          <input
            type="text"
            name="search"
            value={filters.search}
            onChange={handleFilterChange}
            placeholder="옵션 타입 ID 검색"
          />
        </label>
        <label>
          상태
          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">전체</option>
            <option value="active">활성화</option>
            <option value="inactive">비활성화</option>
            <option value="maintenance">정비 중</option>
          </select>
        </label>
        <button onClick={() => setFilters({ ...filters })}>검색</button>
      </div> */}

      {/* 옵션 목록 테이블 */}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <>
          {error && <p className="error">{error}</p>}
          <table className="option-table">
            <thead>
              <tr>
                <th>옵션 ID</th>
                <th>옵션 타입 ID</th>
                <th>상태</th>
                <th>마지막 정비 일자</th>
                <th>예정된 다음 정비 일자</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
                <th>상세 보기</th>
              </tr>
            </thead>
            <tbody>
              {options.length > 0 ? (
                options.map((option) => (
                  <tr key={option.option_id}>
                    <td>{option.option_id}</td>
                    <td>{option.option_type_id}</td>
                    <td>{option.status}</td>
                    <td>
                      {option.last_maintenance_at
                        ? new Date(option.last_maintenance_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      {option.next_maintenance_at
                        ? new Date(option.next_maintenance_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>{new Date(option.created_at).toLocaleString()}</td>
                    <td>{new Date(option.updated_at).toLocaleString()}</td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => openDetailModal(option)}
                      >
                        <MdSearch />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8">조회된 옵션이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
          {/* 백엔드에서 페이지네이션 정보를 반환한다고 가정 */}
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
        {modalType === "detail" && selectedOption && (
          <div className="detail-content">
            <h2>옵션 상세 정보</h2>
            <p>옵션 ID: {selectedOption.option_id}</p>
            <p>옵션 타입 ID: {selectedOption.option_type_id}</p>
            <p>상태: {selectedOption.status}</p>
            <p>
              마지막 정비 일자:{" "}
              {selectedOption.last_maintenance_at
                ? new Date(selectedOption.last_maintenance_at).toLocaleString()
                : "-"}
            </p>
            <p>
              예정된 다음 정비 일자:{" "}
              {selectedOption.next_maintenance_at
                ? new Date(selectedOption.next_maintenance_at).toLocaleString()
                : "-"}
            </p>
            <p>
              등록 일자: {new Date(selectedOption.created_at).toLocaleString()}
            </p>
            <p>
              수정 일자: {new Date(selectedOption.updated_at).toLocaleString()}
            </p>
            <div className="modal-actions">
              <button
                onClick={() => openDeleteModal(selectedOption)}
                className="delete-button"
              >
                삭제
              </button>
            </div>
          </div>
        )}

        {/* 삭제 확인 모달 */}
        {modalType === "delete" && selectedOption && (
          <div className="delete-content">
            <h2>옵션 삭제 확인</h2>
            <p>정말로 이 옵션을 삭제하시겠습니까?</p>
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
            <h2>신규 옵션 등록</h2>
            <form className="add-form">
              <label>
                옵션 타입 ID:
                <input
                  type="number"
                  name="option_type_id"
                  value={formData.option_type_id}
                  onChange={handleFormChange}
                  required
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

export default Option;
