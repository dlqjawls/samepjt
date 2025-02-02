// src/components/VehicleManagement.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import Modal from "./Modal";
import "./VehicleManagement.css";

function VehicleManagement() {
  /**
   * 초기 더미 데이터 설정
   * 디버깅 용으로 사용되며, API 연동 시 제거 예정
   */
  const initialDummyData = [
    {
      vehicleId: 1,
      carNumber: "아3123",
      vin: "VIN1241241",
      currentLocation: "차고지",
      status: "active",
      mileage: 3000,
      lastMaintenanceAt: "2024-12-21",
      nextMaintenanceAt: "2025-03-01",
      createdAt: "2024-01-01T09:00",
      updatedAt: "2024-12-21T09:00",
    },
    {
      vehicleId: 2,
      carNumber: "나3123",
      vin: "VIN1243141",
      currentLocation: "차고지",
      status: "active",
      mileage: 2000,
      lastMaintenanceAt: "2024-01-21",
      nextMaintenanceAt: "2025-04-01",
      createdAt: "2024-02-01T10:00",
      updatedAt: "2024-01-21T10:00",
    },
  ];

  // 차량 목록 상태: 초기 더미 데이터로 설정
  const [vehicles, setVehicles] = useState(initialDummyData);

  // 선택된 차량 및 모달 상태 관리
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  // 모달 콘텐츠 유형: "detail", "edit", "delete", "add"
  const [modalContentType, setModalContentType] = useState("detail");

  const [formData, setFormData] = useState({
    carNumber: "",
    vin: "",
    currentLocation: "",
    status: "active",
    mileage: "",
    lastMaintenanceAt: "",
    nextMaintenanceAt: "",
  });

  // 필터 상태
  const [filters, setFilters] = useState({
    status: "",
    search: "",
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

  // API 베이스 URL 설정
  const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

  // 관리자 인증 토큰 (필요 시 설정)
  const token = localStorage.getItem("adminToken");

  /**
   * 차량 목록 조회 함수
   * API 호출 시도 후 실패하면 더미 데이터를 사용합니다.
   */
  const fetchVehicles = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/vehicle/list`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          status: filters.status || undefined,
          search: filters.search || undefined,
          page: filters.page,
          pageSize: filters.pageSize,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setVehicles(response.data.data.vehicles);
        setPagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "차량 목록을 불러오는 데 실패했습니다."
        );
        // API 호출 실패 시 더미 데이터를 사용
        setVehicles(initialDummyData);
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setError(
          err.response.data.message ||
            "차량 목록을 불러오는 중 오류가 발생했습니다."
        );
      } else {
        setError("차량 목록을 불러오는 중 오류가 발생했습니다.");
      }
      // API 호출 실패 시 더미 데이터를 사용
      setVehicles(initialDummyData);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 차량 목록 조회
  useEffect(() => {
    fetchVehicles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 필터 변경 핸들러
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
      page: 1,
    }));
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      page: newPage,
    }));
  };

  // 모달 열기: 상세보기 모드로 열기
  const handleDetailClick = (vehicle) => {
    setSelectedVehicle(vehicle);
    setModalContentType("detail");
    setIsModalOpen(true);
  };

  // 모달 닫기 (모든 모달 콘텐츠 공통)
  const closeModal = () => {
    setSelectedVehicle(null);
    setIsModalOpen(false);
  };

  // 상세보기에서 수정 버튼 클릭 시 -> 모달 콘텐츠를 "edit"으로 전환
  const handleEditClick = () => {
    setFormData({
      carNumber: selectedVehicle.carNumber,
      vin: selectedVehicle.vin,
      currentLocation: selectedVehicle.currentLocation,
      status: selectedVehicle.status,
      mileage: selectedVehicle.mileage,
      lastMaintenanceAt: selectedVehicle.lastMaintenanceAt,
      nextMaintenanceAt: selectedVehicle.nextMaintenanceAt,
    });
    setModalContentType("edit");
  };

  // 상세보기에서 삭제 버튼 클릭 시 -> 모달 콘텐츠를 "delete"로 전환
  const handleDeleteClick = () => {
    setModalContentType("delete");
  };

  // 신규 등록 버튼 클릭 시 -> 모달 콘텐츠를 "add"로 전환
  const handleAddClick = () => {
    setFormData({
      carNumber: "",
      vin: "",
      currentLocation: "",
      status: "inactive",
      mileage: "",
      lastMaintenanceAt: "",
      nextMaintenanceAt: "",
    });
    setModalContentType("add");
    setIsModalOpen(true);
  };

  // 신규 등록 모달 닫기 함수
  const closeAddModal = () => {
    setFormData({
      carNumber: "",
      vin: "",
      currentLocation: "",
      status: "inactive",
      mileage: "",
      lastMaintenanceAt: "",
      nextMaintenanceAt: "",
    });
    closeModal();
  };

  // 폼 입력 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  /**
   * CRUD 기능 API 연동 (주석 처리된 부분은 그대로 유지)
   */

  // 수정 저장 시 (더미 데이터 사용)
  const handleSaveEditDummy = () => {
    setVehicles((prevVehicles) =>
      prevVehicles.map((item) =>
        item.vehicleId === selectedVehicle.vehicleId
          ? {
              ...item,
              ...formData,
              mileage: Number(formData.mileage),
              updatedAt: new Date().toISOString(),
            }
          : item
      )
    );
    closeModal();
  };

  // 수정 저장 시 (API 연동)
  const handleSaveEdit = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        carNumber: formData.carNumber,
        status: formData.status,
      };

      const response = await axios.put(
        `${BASE_URL}/admin/vehicle/update/${selectedVehicle.vehicleId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchVehicles();
        closeModal();
      } else {
        setError(
          response.data.message || "차량 정보를 수정하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setError(
          err.response.data.message ||
            "차량 정보를 수정하는 중 오류가 발생했습니다."
        );
      } else {
        setError("차량 정보를 수정하는 중 오류가 발생했습니다.");
      }
      setVehicles(initialDummyData);
    } finally {
      setLoading(false);
    }
  };

  // 삭제 확인 시 (더미 데이터 사용)
  const handleConfirmDeleteDummy = () => {
    setVehicles((prevVehicles) =>
      prevVehicles.filter(
        (item) => item.vehicleId !== selectedVehicle.vehicleId
      )
    );
    closeModal();
  };

  // 삭제 확인 시 (API 연동)
  const handleConfirmDelete = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/vehicle/delete/${selectedVehicle.vehicleId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchVehicles();
        closeModal();
      } else {
        setError(response.data.message || "차량을 삭제하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setError(
          err.response.data.message || "차량을 삭제하는 중 오류가 발생했습니다."
        );
      } else {
        setError("차량을 삭제하는 중 오류가 발생했습니다.");
      }
      setVehicles(initialDummyData);
    } finally {
      setLoading(false);
    }
  };

  // 신규 등록 저장 시 (더미 데이터 사용)
  const handleSaveAddDummy = () => {
    const newVehicle = {
      vehicleId: vehicles.length + 1,
      ...formData,
      mileage: Number(formData.mileage),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setVehicles((prevVehicles) => [...prevVehicles, newVehicle]);
    closeModal();
  };

  // 신규 등록 저장 시 (API 연동)
  const handleSaveAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        vin: formData.vin,
        carNumber: formData.carNumber,
      };

      const response = await axios.post(
        `${BASE_URL}/admin/vehicle/register`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchVehicles();
        closeModal();
      } else {
        setError(response.data.message || "차량을 등록하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMessages = err.response.data.errors
          ? err.response.data.errors
              .map((error) => `${error.field}: ${error.message}`)
              .join(", ")
          : err.response.data.message;
        setError(errorMessages || "차량을 등록하는 중 오류가 발생했습니다.");
      } else {
        setError("차량을 등록하는 중 오류가 발생했습니다.");
      }
      setVehicles(initialDummyData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vehicle-container">
      <div className="vehicle-header">
        <h1>차량 관리</h1>
        <button className="add-button" onClick={handleAddClick}>
          차량 등록
        </button>
      </div>

      {/* 필터링 섹션 */}
      <div className="filters">
        <div className="filter-item">
          <span className="filter-description">상태</span>
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
        </div>
        <div className="filter-item">
          <span className="filter-description">검색</span>
          <input
            type="text"
            name="search"
            value={filters.search}
            onChange={handleFilterChange}
            placeholder="차량 번호 또는 VIN"
          />
        </div>
        <button onClick={() => fetchVehicles()}>검색</button>
      </div>

      {error && <p className="error">{error}</p>}

      {/* 차량 목록 테이블 */}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <table className="vehicle-table">
          <thead>
            <tr>
              <th>차량번호</th>
              <th>차대번호 (VIN)</th>
              <th>현재 위치</th>
              <th>현재 상태</th>
              <th>주행 거리 (km)</th>
              <th>최근 정비 일자</th>
              <th>다음 정비 일자</th>
              <th>상세 보기</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.length > 0 ? (
              vehicles.map((vehicle) => (
                <tr key={vehicle.vehicleId}>
                  <td>{vehicle.carNumber}</td>
                  <td>{vehicle.vin}</td>
                  <td>{vehicle.currentLocation || "미정"}</td>
                  <td>
                    {vehicle.status === "active"
                      ? "활성화"
                      : vehicle.status === "inactive"
                      ? "비활성화"
                      : "정비 중"}
                  </td>
                  <td>{vehicle.mileage || 0}</td>
                  <td>{vehicle.lastMaintenanceAt || "없음"}</td>
                  <td>{vehicle.nextMaintenanceAt || "없음"}</td>
                  <td>
                    <button
                      className="detail-button"
                      onClick={() => handleDetailClick(vehicle)}
                    >
                      🔍
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8">조회된 차량이 없습니다.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      {/* 페이지네이션 섹션 */}
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

      {/* 단일 모달: 모달 콘텐츠 유형에 따라 내용 전환 */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={
          modalContentType === "detail"
            ? "차량 상세 정보"
            : modalContentType === "edit"
            ? "차량 수정"
            : modalContentType === "add"
            ? "신규 차량 등록"
            : modalContentType === "delete"
            ? "차량 삭제 확인"
            : ""
        }
      >
        {modalContentType === "detail" && selectedVehicle && (
          <div className="detail-content">
            <p>차량번호: {selectedVehicle.carNumber}</p>
            <p>차대번호 (VIN): {selectedVehicle.vin}</p>
            <p>현재 위치: {selectedVehicle.currentLocation || "미정"}</p>
            <p>
              상태:{" "}
              {selectedVehicle.status === "active"
                ? "활성화"
                : selectedVehicle.status === "inactive"
                ? "비활성화"
                : "정비 중"}
            </p>
            <p>주행 거리: {selectedVehicle.mileage || 0} km</p>
            <p>최근 정비 일자: {selectedVehicle.lastMaintenanceAt || "없음"}</p>
            <p>다음 정비 일자: {selectedVehicle.nextMaintenanceAt || "없음"}</p>
            <div className="modal-actions">
              <button onClick={handleEditClick} className="edit-button">
                수정
              </button>
              <button
                onClick={() => setModalContentType("delete")}
                className="delete-button"
              >
                삭제
              </button>
            </div>
          </div>
        )}

        {modalContentType === "edit" && (
          <div className="edit-content">
            <form className="edit-form">
              <label>
                차량번호:
                <input
                  type="text"
                  name="carNumber"
                  value={formData.carNumber}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                차대번호 (VIN):
                <input
                  type="text"
                  name="vin"
                  value={formData.vin}
                  onChange={handleFormChange}
                  disabled
                />
              </label>
              <label>
                현재 위치:
                <input
                  type="text"
                  name="currentLocation"
                  value={formData.currentLocation}
                  onChange={handleFormChange}
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
                  <option value="maintenance">정비 중</option>
                </select>
              </label>
              <label>
                주행 거리 (km):
                <input
                  type="number"
                  name="mileage"
                  value={formData.mileage}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                최근 정비 일자:
                <input
                  type="date"
                  name="lastMaintenanceAt"
                  value={formData.lastMaintenanceAt}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                다음 정비 일자:
                <input
                  type="date"
                  name="nextMaintenanceAt"
                  value={formData.nextMaintenanceAt}
                  onChange={handleFormChange}
                />
              </label>
            </form>
            <div className="modal-actions">
              {/* 더미 데이터 수정 저장 */}
              <button
                onClick={handleSaveEditDummy}
                className="save-button"
                disabled={loading}
              >
                저장
              </button>
              {/* API 연동 수정 저장 */}
              {/* <button onClick={handleSaveEdit} className="save-button" disabled={loading}>
                저장
              </button> */}
              <button
                onClick={() => setModalContentType("detail")}
                className="cancel-button"
              >
                취소
              </button>
            </div>
          </div>
        )}

        {modalContentType === "delete" && selectedVehicle && (
          <div className="delete-content">
            <h2>차량 삭제 확인</h2>
            <p>정말로 이 차량을 삭제하시겠습니까?</p>
            <div className="modal-actions">
              {/* 더미 데이터 삭제 */}
              <button
                onClick={handleConfirmDeleteDummy}
                className="confirm-delete-button"
                disabled={loading}
              >
                삭제
              </button>
              {/* API 연동 삭제 */}
              {/* <button onClick={handleConfirmDelete} className="confirm-delete-button" disabled={loading}>
                삭제
              </button> */}
              <button
                onClick={() => setModalContentType("detail")}
                className="cancel-button"
              >
                취소
              </button>
            </div>
          </div>
        )}

        {modalContentType === "add" && (
          <div className="add-content">
            <form className="add-form">
              <label>
                차량번호:
                <input
                  type="text"
                  name="carNumber"
                  value={formData.carNumber}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                차대번호 (VIN):
                <input
                  type="text"
                  name="vin"
                  value={formData.vin}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                현재 위치:
                <input
                  type="text"
                  name="currentLocation"
                  value={formData.currentLocation}
                  onChange={handleFormChange}
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
                  <option value="maintenance">정비 중</option>
                </select>
              </label>
              <label>
                주행 거리 (km):
                <input
                  type="number"
                  name="mileage"
                  value={formData.mileage}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                최근 정비 일자:
                <input
                  type="date"
                  name="lastMaintenanceAt"
                  value={formData.lastMaintenanceAt}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                다음 정비 일자:
                <input
                  type="date"
                  name="nextMaintenanceAt"
                  value={formData.nextMaintenanceAt}
                  onChange={handleFormChange}
                />
              </label>
            </form>
            <div className="modal-actions">
              {/* 더미 데이터 신규 등록 저장 */}
              <button
                onClick={handleSaveAddDummy}
                className="save-button"
                disabled={loading}
              >
                등록
              </button>
              {/* API 연동 신규 등록 저장 */}
              {/* <button onClick={handleSaveAdd} className="save-button" disabled={loading}>
                등록
              </button> */}
              <button onClick={closeAddModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default VehicleManagement;
