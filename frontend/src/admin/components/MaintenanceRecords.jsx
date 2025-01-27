// src/components/MaintenanceRecords.jsx
import React, { useState, useEffect } from "react";
import Modal from "./Modal";
import "./MaintenanceRecords.css";
import axios from "axios";

function MaintenanceRecords() {
  /**
   * 초기 더미 데이터 설정
   * 정비 기록 목록을 더미 데이터로 관리.
   */
  const initialDummyMaintenanceRecords = [
    {
      maintenanceId: "MT001",
      adminId: "adminMaster",
      type: "module",
      targetId: "MOD001",
      issue: "타이어 교체",
      maintenanceDate: "2025-01-10",
      cost: 50000,
      status: "completed",
      completedAt: "2025-01-15",
      notes: "모든 타이어 교체 완료",
      createdAt: "2025-01-01T09:00:00Z",
      updatedAt: "2025-01-15T10:00:00Z",
    },
    {
      maintenanceId: "MT002",
      adminId: "adminSemi",
      type: "vehicle",
      targetId: "VEH001",
      issue: "엔진 오일 교환",
      maintenanceDate: "2025-01-20",
      cost: 30000,
      status: "in-progress",
      completedAt: null,
      notes: "엔진 오일 교환 중",
      createdAt: "2025-01-10T08:00:00Z",
      updatedAt: "2025-01-20T12:00:00Z",
    },
  ];

  // 정비 기록 목록 상태: 초기 더미 데이터로 설정
  const [maintenanceRecords, setMaintenanceRecords] = useState([]);

  // 모달 관리 상태
  const [modalType, setModalType] = useState(null); // 'detail', 'edit', 'delete', 'add'
  const [selectedRecord, setSelectedRecord] = useState(null); // 선택된 정비 기록

  // 필터 상태
  const [filters, setFilters] = useState({
    type: "",
    targetId: "",
    status: "",
    startDate: "",
    endDate: "",
    page: 1,
    pageSize: 10,
  });

  // 페이지네이션 상태
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
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
   * 정비 기록 목록 조회 함수
   * 현재는 더미 데이터를 사용하지만, 추후 API 연동 시 수정 필요.
   */
  const fetchMaintenanceRecords = async () => {
    setLoading(true);
    setError("");
    try {
      // API 연동 시 주석 해제하고 사용
      /*
      const response = await axios.get(`${BASE_URL}/admin/maintenance/list`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          type: filters.type || undefined,
          targetId: filters.targetId || undefined,
          status: filters.status || undefined,
          startDate: filters.startDate || undefined,
          endDate: filters.endDate || undefined,
          page: filters.page,
          pageSize: filters.pageSize,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setMaintenanceRecords(response.data.data.maintenanceRecords);
        setPagination(response.data.data.pagination);
      } else {
        setError(response.data.message || "정비 기록을 불러오는 데 실패했습니다.");
        setMaintenanceRecords(initialDummyMaintenanceRecords);
        setPagination({
          currentPage: 1,
          totalPages: 1,
          totalItems: initialDummyMaintenanceRecords.length,
          pageSize: filters.pageSize,
        });
      }
      */

      // 현재는 더미 데이터 사용
      let filteredRecords = [...initialDummyMaintenanceRecords];

      if (filters.type) {
        filteredRecords = filteredRecords.filter(
          (record) => record.type.toLowerCase() === filters.type.toLowerCase()
        );
      }

      if (filters.targetId) {
        filteredRecords = filteredRecords.filter((record) =>
          record.targetId.toLowerCase().includes(filters.targetId.toLowerCase())
        );
      }

      if (filters.status) {
        filteredRecords = filteredRecords.filter(
          (record) =>
            record.status.toLowerCase() === filters.status.toLowerCase()
        );
      }

      if (filters.startDate) {
        filteredRecords = filteredRecords.filter(
          (record) =>
            new Date(record.maintenanceDate) >= new Date(filters.startDate)
        );
      }

      if (filters.endDate) {
        filteredRecords = filteredRecords.filter(
          (record) =>
            new Date(record.maintenanceDate) <= new Date(filters.endDate)
        );
      }

      // 페이지네이션 적용
      const startIndex = (filters.page - 1) * filters.pageSize;
      const endIndex = startIndex + filters.pageSize;
      const paginatedRecords = filteredRecords.slice(startIndex, endIndex);

      setMaintenanceRecords(paginatedRecords);
      setPagination({
        currentPage: filters.page,
        totalPages: Math.ceil(filteredRecords.length / filters.pageSize),
        totalItems: filteredRecords.length,
        pageSize: filters.pageSize,
      });
    } catch (err) {
      console.error(err);
      setError("정비 기록을 불러오는 중 오류가 발생했습니다.");
      setMaintenanceRecords(initialDummyMaintenanceRecords);
      setPagination({
        currentPage: 1,
        totalPages: 1,
        totalItems: initialDummyMaintenanceRecords.length,
        pageSize: filters.pageSize,
      });
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 및 필터 변경 시 정비 기록 목록 조회
  useEffect(() => {
    fetchMaintenanceRecords();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 필터 변경 핸들러
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
      // 필터 변경 시 페이지를 1로 리셋
      ...(["type", "targetId", "status", "startDate", "endDate"].includes(name)
        ? { page: 1 }
        : {}),
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
  const openModal = (type, record = null) => {
    setModalType(type);
    setSelectedRecord(record);
  };

  // 모달 닫기 함수
  const closeModal = () => {
    setModalType(null);
    setSelectedRecord(null);
    setError("");
  };

  // 수정 저장 시
  const handleSaveEdit = async () => {
    // 상태가 'completed'인 경우 수정 불가
    if (selectedRecord.status === "completed") {
      alert("완료된 정비 기록은 수정할 수 없습니다.");
      closeModal();
      return;
    }

    // API 연동 시 주석 해제하고 사용
    /*
    try {
      const response = await axios.put(
        `${BASE_URL}/admin/maintenance/update/${selectedRecord.maintenanceId}`,
        {
          status: formData.status,
          issue: formData.issue,
          cost: parseFloat(formData.cost),
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        // 데이터 업데이트
        setMaintenanceRecords((prevRecords) =>
          prevRecords.map((record) =>
            record.maintenanceId === selectedRecord.maintenanceId
              ? { ...record, ...response.data.data }
              : record
          )
        );
        closeModal();
      } else {
        alert(response.data.message || "정비 기록을 수정하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      alert("정비 기록을 수정하는 중 오류가 발생했습니다.");
    }
    */

    // 현재는 더미 데이터 업데이트
    setMaintenanceRecords((prevRecords) =>
      prevRecords.map((record) =>
        record.maintenanceId === selectedRecord.maintenanceId
          ? {
              ...record,
              status: formData.status,
              issue: formData.issue,
              cost: parseFloat(formData.cost),
              completedAt:
                formData.status === "completed"
                  ? new Date().toISOString()
                  : null,
              updatedAt: new Date().toISOString(),
            }
          : record
      )
    );
    closeModal();
  };

  // 삭제 확인 시
  const handleConfirmDelete = async () => {
    // API 연동 시 주석 해제하고 사용
    /*
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/maintenance/delete/${selectedRecord.maintenanceId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        // 데이터 삭제
        setMaintenanceRecords((prevRecords) =>
          prevRecords.filter(
            (record) => record.maintenanceId !== selectedRecord.maintenanceId
          )
        );
        closeModal();
      } else {
        alert(response.data.message || "정비 기록을 삭제하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      alert("정비 기록을 삭제하는 중 오류가 발생했습니다.");
    }
    */

    // 현재는 더미 데이터 삭제
    setMaintenanceRecords((prevRecords) =>
      prevRecords.filter(
        (record) => record.maintenanceId !== selectedRecord.maintenanceId
      )
    );
    closeModal();
  };

  // 신규 등록 저장 시
  const handleSaveAdd = async () => {
    // API 연동 시 주석 해제하고 사용
    /*
    try {
      const response = await axios.post(
        `${BASE_URL}/admin/maintenance/register`,
        {
          type: formData.type,
          targetId: formData.targetId,
          issue: formData.issue,
          maintenanceDate: formData.maintenanceDate,
          cost: parseFloat(formData.cost) || 0.0,
          status: formData.status || "pending",
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        // 데이터 추가
        setMaintenanceRecords((prevRecords) => [
          ...prevRecords,
          response.data.data,
        ]);
        closeModal();
      } else {
        alert(response.data.message || "정비 기록을 등록하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      alert("정비 기록을 등록하는 중 오류가 발생했습니다.");
    }
    */

    // 현재는 더미 데이터 추가
    const newRecord = {
      maintenanceId: `MT${String(maintenanceRecords.length + 1).padStart(
        3,
        "0"
      )}`,
      adminId: formData.adminId,
      type: formData.type,
      targetId: formData.targetId,
      issue: formData.issue,
      maintenanceDate: formData.maintenanceDate,
      cost: parseFloat(formData.cost) || 0.0,
      status: formData.status || "pending",
      completedAt:
        formData.status === "completed" ? new Date().toISOString() : null,
      notes: formData.notes,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setMaintenanceRecords((prevRecords) => [...prevRecords, newRecord]);
    closeModal();
  };

  // 폼 데이터 상태
  const [formData, setFormData] = useState({
    type: "vehicle", // 기본값 설정
    targetId: "",
    issue: "",
    maintenanceDate: "",
    cost: "",
    status: "pending",
    completedAt: "",
    notes: "",
  });

  // 폼 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  return (
    <div className="maintenance-container">
      <div className="maintenance-header">
        <h1>정비 기록 관리</h1>
        <button className="add-button" onClick={() => openModal("add")}>
          + 신규 정비 요청
        </button>
      </div>

      {/* 필터링 섹션 */}
      <div className="filters">
        <label>
          정비 대상 종류:
          <select
            name="type"
            value={filters.type}
            onChange={handleFilterChange}
          >
            <option value="">전체</option>
            <option value="vehicle">차량</option>
            <option value="module">모듈</option>
            <option value="option">옵션</option>
          </select>
        </label>
        <label>
          대상 ID:
          <input
            type="text"
            name="targetId"
            value={filters.targetId}
            onChange={handleFilterChange}
            placeholder="대상 ID 입력"
          />
        </label>
        <label>
          정비 상태:
          <select
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
          >
            <option value="">전체</option>
            <option value="pending">대기 중</option>
            <option value="in-progress">진행 중</option>
            <option value="completed">완료됨</option>
          </select>
        </label>
        <label>
          시작 날짜:
          <input
            type="date"
            name="startDate"
            value={filters.startDate}
            onChange={handleFilterChange}
          />
        </label>
        <label>
          종료 날짜:
          <input
            type="date"
            name="endDate"
            value={filters.endDate}
            onChange={handleFilterChange}
          />
        </label>
        <button onClick={fetchMaintenanceRecords}>검색</button>
      </div>

      {/* 정비 기록 목록 테이블 */}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <>
          {error && <p className="error">{error}</p>}
          <table className="maintenance-table">
            <thead>
              <tr>
                <th>정비 ID</th>
                <th>관리자 ID</th>
                <th>정비 대상 종류</th>
                <th>대상 ID</th>
                <th>문제</th>
                <th>정비 일자</th>
                <th>비용 (원)</th>
                <th>상태</th>
                <th>완료 일자</th>
                <th>노트</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
                <th>상세 보기</th>
                <th>수정</th>
                <th>삭제</th>
              </tr>
            </thead>
            <tbody>
              {maintenanceRecords.length > 0 ? (
                maintenanceRecords.map((record) => (
                  <tr key={record.maintenanceId}>
                    <td>{record.maintenanceId}</td>
                    <td>{record.adminId}</td>
                    <td>
                      {record.type === "vehicle"
                        ? "차량"
                        : record.type === "module"
                        ? "모듈"
                        : "옵션"}
                    </td>
                    <td>{record.targetId}</td>
                    <td>{record.issue}</td>
                    <td>{record.maintenanceDate}</td>
                    <td>{record.cost.toLocaleString()}원</td>
                    <td>
                      {record.status === "pending"
                        ? "대기 중"
                        : record.status === "in-progress"
                        ? "진행 중"
                        : "완료됨"}
                    </td>
                    <td>
                      {record.completedAt ? record.completedAt : "진행 중"}
                    </td>
                    <td>{record.notes}</td>
                    <td>{new Date(record.createdAt).toLocaleString()}</td>
                    <td>{new Date(record.updatedAt).toLocaleString()}</td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => openModal("detail", record)}
                      >
                        🔍 상세보기
                      </button>
                    </td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => openModal("edit", record)}
                        disabled={record.status === "completed"}
                        title={
                          record.status === "completed"
                            ? "완료된 정비 기록은 수정할 수 없습니다."
                            : "정비 기록 수정"
                        }
                      >
                        ✏️ 수정
                      </button>
                    </td>
                    <td>
                      <button
                        className="delete-button"
                        onClick={() => openModal("delete", record)}
                        disabled={record.status === "completed"}
                        title={
                          record.status === "completed"
                            ? "완료된 정비 기록은 삭제할 수 없습니다."
                            : "정비 기록 삭제"
                        }
                      >
                        🗑️ 삭제
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="15">조회된 정비 기록이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>

          {/* 페이지네이션 */}
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
        {modalType === "detail" && selectedRecord && (
          <div className="detail-content">
            <h2>정비 기록 상세 정보</h2>
            <p>정비 ID: {selectedRecord.maintenanceId}</p>
            <p>관리자 ID: {selectedRecord.adminId}</p>
            <p>
              정비 대상 종류:{" "}
              {selectedRecord.type === "vehicle"
                ? "차량"
                : selectedRecord.type === "module"
                ? "모듈"
                : "옵션"}
            </p>
            <p>대상 ID: {selectedRecord.targetId}</p>
            <p>문제: {selectedRecord.issue}</p>
            <p>정비 일자: {selectedRecord.maintenanceDate}</p>
            <p>비용: {selectedRecord.cost.toLocaleString()}원</p>
            <p>
              상태:{" "}
              {selectedRecord.status === "pending"
                ? "대기 중"
                : selectedRecord.status === "in-progress"
                ? "진행 중"
                : "완료됨"}
            </p>
            <p>완료 일자: {selectedRecord.completedAt || "진행 중"}</p>
            <p>노트: {selectedRecord.notes}</p>
            <p>
              등록 일자: {new Date(selectedRecord.createdAt).toLocaleString()}
            </p>
            <p>
              수정 일자: {new Date(selectedRecord.updatedAt).toLocaleString()}
            </p>
          </div>
        )}

        {/* 수정 모달 */}
        {modalType === "edit" && selectedRecord && (
          <div className="edit-content">
            <h2>정비 기록 수정</h2>
            <form className="edit-form">
              <label>
                관리자 ID:
                <input
                  type="text"
                  name="adminId"
                  value={formData.adminId}
                  onChange={handleFormChange}
                  disabled={selectedRecord.status === "completed"}
                />
              </label>
              <label>
                정비 대상 종류:
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleFormChange}
                  disabled
                >
                  <option value="vehicle">차량</option>
                  <option value="module">모듈</option>
                  <option value="option">옵션</option>
                </select>
              </label>
              <label>
                대상 ID:
                <input
                  type="text"
                  name="targetId"
                  value={formData.targetId}
                  onChange={handleFormChange}
                  disabled={selectedRecord.status === "completed"}
                />
              </label>
              <label>
                문제:
                <input
                  type="text"
                  name="issue"
                  value={formData.issue}
                  onChange={handleFormChange}
                  disabled={selectedRecord.status === "completed"}
                />
              </label>
              <label>
                정비 일자:
                <input
                  type="date"
                  name="maintenanceDate"
                  value={formData.maintenanceDate}
                  onChange={handleFormChange}
                  disabled={selectedRecord.status === "completed"}
                />
              </label>
              <label>
                비용 (원):
                <input
                  type="number"
                  name="cost"
                  value={formData.cost}
                  onChange={handleFormChange}
                  disabled={selectedRecord.status === "completed"}
                />
              </label>
              <label>
                상태:
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleFormChange}
                  disabled={selectedRecord.status === "completed"}
                >
                  <option value="pending">대기 중</option>
                  <option value="in-progress">진행 중</option>
                  <option value="completed">완료됨</option>
                </select>
              </label>
              {formData.status === "completed" && (
                <label>
                  완료 일자:
                  <input
                    type="date"
                    name="completedAt"
                    value={formData.completedAt}
                    onChange={handleFormChange}
                  />
                </label>
              )}
              <label>
                노트:
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleFormChange}
                  disabled={selectedRecord.status === "completed"}
                ></textarea>
              </label>
            </form>
            <div className="modal-actions">
              <button
                onClick={handleSaveEdit}
                className="save-button"
                disabled={selectedRecord.status === "completed"}
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
        {modalType === "delete" && selectedRecord && (
          <div className="delete-content">
            <h2>정비 기록 삭제 확인</h2>
            <p>정말로 이 정비 기록을 삭제하시겠습니까?</p>
            <div className="modal-actions">
              <button
                onClick={handleConfirmDelete}
                className="confirm-delete-button"
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
            <h2>신규 정비 요청</h2>
            <form className="add-form">
              <label>
                관리자 ID:
                <input
                  type="text"
                  name="adminId"
                  value={formData.adminId}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                정비 대상 종류:
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleFormChange}
                  required
                >
                  <option value="vehicle">차량</option>
                  <option value="module">모듈</option>
                  <option value="option">옵션</option>
                </select>
              </label>
              <label>
                대상 ID:
                <input
                  type="text"
                  name="targetId"
                  value={formData.targetId}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                문제:
                <input
                  type="text"
                  name="issue"
                  value={formData.issue}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                정비 일자:
                <input
                  type="date"
                  name="maintenanceDate"
                  value={formData.maintenanceDate}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                비용 (원):
                <input
                  type="number"
                  name="cost"
                  value={formData.cost}
                  onChange={handleFormChange}
                  min="0"
                />
              </label>
              <label>
                상태:
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleFormChange}
                >
                  <option value="pending">대기 중</option>
                  <option value="in-progress">진행 중</option>
                  <option value="completed">완료됨</option>
                </select>
              </label>
              {formData.status === "completed" && (
                <label>
                  완료 일자:
                  <input
                    type="date"
                    name="completedAt"
                    value={formData.completedAt}
                    onChange={handleFormChange}
                  />
                </label>
              )}
              <label>
                노트:
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleFormChange}
                ></textarea>
              </label>
            </form>
            <div className="modal-actions">
              <button onClick={handleSaveAdd} className="save-button">
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

export default MaintenanceRecords;
