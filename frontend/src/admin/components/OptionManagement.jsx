// src/components/OptionManagement.jsx
import React, { useState, useEffect } from "react";
import Modal from "./Modal";
import "./OptionManagement.css";

function OptionManagement() {
  /**
   * 초기 더미 데이터 설정
   * 옵션 목록을 더미 데이터로 관리.
   */
  const initialDummyOptions = [
    {
      optionId: 1,
      optionName: "침대",
      optionType: "기본",
      optionSize: "2x3",
      optionCost: 50000,
      stockQuantity: 10,
      status: "active",
      description: "차량 내에서 사용할 수 있는 침대 옵션.",
      imgUrls: [
        "https://example.com/images/bed1.jpg",
        "https://example.com/images/bed2.jpg",
      ],
      createdAt: "2024-10-10T10:00",
      updatedAt: "2024-11-10T10:00",
    },
    {
      optionId: 2,
      optionName: "냉장고",
      optionType: "가전",
      optionSize: "1x1",
      optionCost: 80000,
      stockQuantity: 5,
      status: "inactive",
      description: "신선 식품을 저장하기 위한 냉장고.",
      imgUrls: ["https://example.com/images/fridge1.jpg"],
      createdAt: "2024-09-15T09:00",
      updatedAt: "2024-10-15T09:00",
    },
  ];

  // 옵션 목록 상태: 초기 더미 데이터로 설정
  const [options, setOptions] = useState(initialDummyOptions);

  // 모달 관리 상태
  const [modalType, setModalType] = useState(null); // 'add', 'detail', 'edit', 'delete'
  const [selectedOption, setSelectedOption] = useState(null); // 선택된 옵션

  // 폼 데이터 상태
  const [formData, setFormData] = useState({
    optionName: "",
    optionType: "",
    optionSize: "",
    optionCost: "",
    stockQuantity: "",
    status: "active",
    description: "",
    imgUrls: "",
    createdAt: "",
    updatedAt: "",
  });

  // 필터 상태
  const [filters, setFilters] = useState({
    search: "",
    status: "",
    page: 1,
    pageSize: 10,
  });

  // 페이지네이션 상태
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: initialDummyOptions.length,
    pageSize: 10,
  });

  // 로딩 및 오류 상태
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 관리자 인증 토큰 (필요 시 설정)
  const token = localStorage.getItem("adminToken"); // 토큰 저장 방식에 따라 수정

  // API 베이스 URL 설정
  const BASE_URL = "https://backend-wandering-river-6835.fly.dev"; // 실제 백엔드 API URL로 변경하세요

  /**
   * 옵션 목록 조회 함수
   * 현재는 더미 데이터를 사용하지만, 추후 API 연동 시 수정 필요.
   */
  const fetchOptions = async () => {
    setLoading(true);
    setError("");
    try {
      // API 연동 시 주석 해제하고 사용
      /*
      const response = await axios.get(`${BASE_URL}/admin/option/list`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          search: filters.search || undefined,
          status: filters.status || undefined,
          page: filters.page,
          pageSize: filters.pageSize,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setOptions(response.data.data.options);
        setPagination(response.data.data.pagination);
      } else {
        setError(response.data.message || "옵션 목록을 불러오는 데 실패했습니다.");
        setOptions(initialDummyOptions);
      }
      */

      // 현재는 더미 데이터 사용
      // 필터링 로직 구현
      let filteredOptions = [...initialDummyOptions];

      if (filters.search) {
        filteredOptions = filteredOptions.filter((option) =>
          option.optionName.toLowerCase().includes(filters.search.toLowerCase())
        );
      }

      if (filters.status) {
        filteredOptions = filteredOptions.filter(
          (option) => option.status === filters.status
        );
      }

      // 페이지네이션 적용
      const startIndex = (filters.page - 1) * filters.pageSize;
      const endIndex = startIndex + filters.pageSize;
      const paginatedOptions = filteredOptions.slice(startIndex, endIndex);

      setOptions(paginatedOptions);
      setPagination({
        currentPage: filters.page,
        totalPages: Math.ceil(filteredOptions.length / filters.pageSize),
        totalItems: filteredOptions.length,
        pageSize: filters.pageSize,
      });
    } catch (err) {
      console.error(err);
      setError("옵션 목록을 불러오는 중 오류가 발생했습니다.");
      setOptions(initialDummyOptions);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 옵션 목록 조회
  useEffect(() => {
    fetchOptions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 필터 변경 핸들러
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
      // 필터 변경 시 페이지를 1로 리셋
      ...(name === "search" || name === "status" ? { page: 1 } : {}),
    }));
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      page: newPage,
    }));
  };

  // 모달 열기 함수
  const openModal = (type, option = null) => {
    setModalType(type);
    setSelectedOption(option);
    if (option) {
      setFormData({
        optionName: option.optionName,
        optionType: option.optionType,
        optionSize: option.optionSize,
        optionCost: option.optionCost,
        stockQuantity: option.stockQuantity,
        status: option.status,
        description: option.description,
        imgUrls: option.imgUrls.join(", "),
        createdAt: option.createdAt,
        updatedAt: option.updatedAt,
      });
    } else {
      setFormData({
        optionName: "",
        optionType: "",
        optionSize: "",
        optionCost: "",
        stockQuantity: "",
        status: "active",
        description: "",
        imgUrls: "",
        createdAt: "",
        updatedAt: "",
      });
    }
  };

  // 모달 닫기 함수
  const closeModal = () => {
    setModalType(null);
    setSelectedOption(null);
    setFormData({
      optionName: "",
      optionType: "",
      optionSize: "",
      optionCost: "",
      stockQuantity: "",
      status: "active",
      description: "",
      imgUrls: "",
      createdAt: "",
      updatedAt: "",
    });
    setError("");
  };

  // 폼 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  /**
   * CRUD 기능 구현
   * 현재는 더미 데이터를 사용 중이며, 추후 API 연동 시 수정 필요.
   */

  // 옵션 신규 등록 저장 시 (더미 데이터 사용)
  const handleSaveAddDummy = () => {
    const newOption = {
      optionId:
        options.length > 0
          ? Math.max(...options.map((o) => o.optionId)) + 1
          : 1,
      optionName: formData.optionName,
      optionType: formData.optionType,
      optionSize: formData.optionSize,
      optionCost: Number(formData.optionCost),
      stockQuantity: Number(formData.stockQuantity),
      status: formData.status,
      description: formData.description,
      imgUrls: formData.imgUrls
        ? formData.imgUrls.split(",").map((url) => url.trim())
        : [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setOptions((prevOptions) => [...prevOptions, newOption]);
    closeModal();
  };

  // 옵션 신규 등록 저장 시 (API 연동)
  const handleSaveAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        optionName: formData.optionName,
        optionType: formData.optionType,
        optionSize: formData.optionSize,
        optionCost: Number(formData.optionCost),
        stockQuantity: Number(formData.stockQuantity),
        status: formData.status,
        description: formData.description,
        imgUrls: formData.imgUrls
          ? formData.imgUrls.split(",").map((url) => url.trim())
          : [],
      };

      // API 연동 시 주석 해제하고 사용
      /*
      const response = await axios.post(
        `${BASE_URL}/admin/option/register`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchOptions();
        closeModal();
      } else {
        setError(response.data.message || "옵션을 등록하는 데 실패했습니다.");
      }
      */

      // 현재는 더미 데이터 사용
      handleSaveAddDummy();
    } catch (err) {
      console.error(err);
      setError("옵션을 등록하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 옵션 수정 저장 시 (더미 데이터 사용)
  const handleSaveEditDummy = () => {
    if (!selectedOption) return;
    setOptions((prevOptions) =>
      prevOptions.map((option) =>
        option.optionId === selectedOption.optionId
          ? {
              ...option,
              optionName: formData.optionName,
              optionType: formData.optionType,
              optionSize: formData.optionSize,
              optionCost: Number(formData.optionCost),
              stockQuantity: Number(formData.stockQuantity),
              status: formData.status,
              description: formData.description,
              imgUrls: formData.imgUrls
                ? formData.imgUrls.split(",").map((url) => url.trim())
                : [],
              updatedAt: new Date().toISOString(),
            }
          : option
      )
    );
    closeModal();
  };

  // 옵션 수정 저장 시 (API 연동)
  const handleSaveEdit = async () => {
    if (!selectedOption) return;
    setLoading(true);
    setError("");
    try {
      const payload = {
        optionName: formData.optionName,
        optionType: formData.optionType,
        optionSize: formData.optionSize,
        optionCost: Number(formData.optionCost),
        stockQuantity: Number(formData.stockQuantity),
        status: formData.status,
        description: formData.description,
        imgUrls: formData.imgUrls
          ? formData.imgUrls.split(",").map((url) => url.trim())
          : [],
      };

      // API 연동 시 주석 해제하고 사용
      /*
      const response = await axios.put(
        `${BASE_URL}/admin/option/update/${selectedOption.optionId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchOptions();
        closeModal();
      } else {
        setError(response.data.message || "옵션을 수정하는 데 실패했습니다.");
      }
      */

      // 현재는 더미 데이터 사용
      handleSaveEditDummy();
    } catch (err) {
      console.error(err);
      setError("옵션을 수정하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 옵션 삭제 확인 시 (더미 데이터 사용)
  const handleConfirmDeleteDummy = () => {
    if (!selectedOption) return;
    setOptions((prevOptions) =>
      prevOptions.filter(
        (option) => option.optionId !== selectedOption.optionId
      )
    );
    closeModal();
  };

  // 옵션 삭제 확인 시 (API 연동)
  const handleConfirmDelete = async () => {
    if (!selectedOption) return;
    setLoading(true);
    setError("");
    try {
      // API 연동 시 주석 해제하고 사용
      /*
      const response = await axios.delete(
        `${BASE_URL}/admin/option/delete/${selectedOption.optionId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchOptions();
        closeModal();
      } else {
        setError(response.data.message || "옵션을 삭제하는 데 실패했습니다.");
      }
      */

      // 현재는 더미 데이터 사용
      handleConfirmDeleteDummy();
    } catch (err) {
      console.error(err);
      setError("옵션을 삭제하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="option-container">
      <div className="option-header">
        <h1>옵션 관리</h1>
        <button className="add-button" onClick={() => openModal("add")}>
          + 신규 등록
        </button>
      </div>

      {/* 필터링 섹션 */}
      <div className="filters">
        <label>
          검색:
          <input
            type="text"
            name="search"
            value={filters.search}
            onChange={handleFilterChange}
            placeholder="옵션 이름 검색"
          />
        </label>
        <label>
          상태:
          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">전체</option>
            <option value="active">활성화</option>
            <option value="inactive">비활성화</option>
          </select>
        </label>
        <button onClick={fetchOptions}>검색</button>
      </div>

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
                <th>옵션 이름</th>
                <th>옵션 유형</th>
                <th>옵션 크기</th>
                <th>옵션 비용 (원)</th>
                <th>재고 수량</th>
                <th>상태</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
                <th>상세 보기</th>
              </tr>
            </thead>
            <tbody>
              {options.length > 0 ? (
                options.map((option) => (
                  <tr key={option.optionId}>
                    <td>{option.optionId}</td>
                    <td>{option.optionName}</td>
                    <td>{option.optionType}</td>
                    <td>{option.optionSize}</td>
                    <td>{option.optionCost.toLocaleString()}원</td>
                    <td>{option.stockQuantity}</td>
                    <td>
                      {option.status === "active" ? "활성화" : "비활성화"}
                    </td>
                    <td>{new Date(option.createdAt).toLocaleString()}</td>
                    <td>{new Date(option.updatedAt).toLocaleString()}</td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => openModal("detail", option)}
                      >
                        🔍 상세보기
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="10">조회된 옵션이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>

          {/* 옵션 페이지네이션 */}
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
            <p>옵션 ID: {selectedOption.optionId}</p>
            <p>옵션 이름: {selectedOption.optionName}</p>
            <p>옵션 유형: {selectedOption.optionType}</p>
            <p>옵션 크기: {selectedOption.optionSize}</p>
            <p>옵션 비용: {selectedOption.optionCost.toLocaleString()}원</p>
            <p>재고 수량: {selectedOption.stockQuantity}</p>
            <p>
              상태: {selectedOption.status === "active" ? "활성화" : "비활성화"}
            </p>
            <p>설명: {selectedOption.description || "없음"}</p>
            <p>이미지:</p>
            {selectedOption.imgUrls.length > 0 ? (
              selectedOption.imgUrls.map((url, index) => (
                <img
                  key={index}
                  src={url}
                  alt={`${selectedOption.optionName} 이미지 ${index + 1}`}
                  className="option-image"
                />
              ))
            ) : (
              <p>이미지 없음</p>
            )}
            <p>
              등록 일자: {new Date(selectedOption.createdAt).toLocaleString()}
            </p>
            <p>
              수정 일자: {new Date(selectedOption.updatedAt).toLocaleString()}
            </p>
            <div className="modal-actions">
              <button
                onClick={() => openModal("edit", selectedOption)}
                className="edit-button"
              >
                수정
              </button>
              <button
                onClick={() => openModal("delete", selectedOption)}
                className="delete-button"
              >
                삭제
              </button>
            </div>
          </div>
        )}

        {/* 수정 모달 */}
        {modalType === "edit" && selectedOption && (
          <div className="edit-content">
            <h2>옵션 수정</h2>
            <form className="edit-form">
              <label>
                옵션 이름:
                <input
                  type="text"
                  name="optionName"
                  value={formData.optionName}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 유형:
                <input
                  type="text"
                  name="optionType"
                  value={formData.optionType}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 크기:
                <input
                  type="text"
                  name="optionSize"
                  value={formData.optionSize}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 비용 (원):
                <input
                  type="number"
                  name="optionCost"
                  value={formData.optionCost}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                재고 수량:
                <input
                  type="number"
                  name="stockQuantity"
                  value={formData.stockQuantity}
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
                </select>
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
                  name="imgUrls"
                  value={formData.imgUrls}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                등록 일자:
                <input
                  type="datetime-local"
                  name="createdAt"
                  value={formData.createdAt}
                  onChange={handleFormChange}
                  disabled
                />
              </label>
              <label>
                수정 일자:
                <input
                  type="datetime-local"
                  name="updatedAt"
                  value={formData.updatedAt}
                  onChange={handleFormChange}
                  disabled
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
                옵션 이름:
                <input
                  type="text"
                  name="optionName"
                  value={formData.optionName}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 유형:
                <input
                  type="text"
                  name="optionType"
                  value={formData.optionType}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 크기:
                <input
                  type="text"
                  name="optionSize"
                  value={formData.optionSize}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                옵션 비용 (원):
                <input
                  type="number"
                  name="optionCost"
                  value={formData.optionCost}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                재고 수량:
                <input
                  type="number"
                  name="stockQuantity"
                  value={formData.stockQuantity}
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
                </select>
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
                  name="imgUrls"
                  value={formData.imgUrls}
                  onChange={handleFormChange}
                />
              </label>
              {/* 등록 일자 및 수정 일자는 자동 설정 */}
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

export default OptionManagement;
