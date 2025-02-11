// src/admin/components/VehicleManagement.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import Modal from "./Modal";
import "./VehicleManagement.css";
import { MdSearch } from "react-icons/md";

function VehicleManagement() {
  /**
   * 초기 더미 데이터 설정
   * 디버깅 용으로 사용되며, API 연동 시 제거 예정
   */
  const initialDummyData = [
    {
      vehicle_id: 1,
      vin: "ABC123456789XYZ",
      vehicle_number: "PBV-1234",
      current_location: { x: 12.313, y: 32.3232 },
      status: "active",
      mileage: 12000.5,
      last_maintenance_at: "2025-01-10T12:00:00",
      next_maintenance_at: "2025-06-10T12:00:00",
      created_at: "2024-05-01T08:30:00",
      updated_at: "2025-01-10T12:00:00",
    },
    {
      vehicle_id: 2,
      vin: "DEF987654321ZYX",
      vehicle_number: "PBV-5678",
      current_location: { x: 0, y: 0 },
      status: "inactive",
      mileage: 8000,
      last_maintenance_at: "2024-11-21T10:00:00",
      next_maintenance_at: "2025-04-01T10:00:00",
      created_at: "2024-02-01T10:00:00",
      updated_at: "2024-11-21T10:00:00",
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
    vehicle_number: "",
  });

  // 필터 상태
  const [filters, setFilters] = useState({
    item_status_name: "",
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
   * API 호출 시도 후 실패하면 더미 데이터를 사용
   */
  const fetchVehicles = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/vehicles`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          item_status_name: filters.item_status_name || undefined,
          search: filters.search || undefined,
          page: filters.page,
          pageSize: filters.pageSize,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setVehicles(response.data.data.vehicles);
        setPagination(response.data.data.pagination);
        console.log(response.data);
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
        setError();
        // err.response.data.message ||
        //   "차량 목록을 불러오는 중 오류가 발생했습니다."
      } else {
        // setError("차량 목록을 불러오는 중 오류가 발생했습니다.");
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
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      page: 1,
    }));
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
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
      vehicle_number: selectedVehicle.vehicle_number,
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
      vehicle_number: "",
      vin: "",
    });
    setModalContentType("add");
    setIsModalOpen(true);
  };

  // 신규 등록 모달 닫기 함수
  const closeAddModal = () => {
    setFormData({
      vehicle_number: "",
      vin: "",
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
        item.vehicle_id === selectedVehicle.vehicle_id
          ? {
              ...item,
              vehicle_number: formData.vehicle_number,
              updated_at: new Date().toISOString(),
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
        vehicle_number: formData.vehicle_number,
      };

      const response = await axios.patch(
        `${BASE_URL}/admin/vehicles/${selectedVehicle.vehicle_id}`,
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
      setError(
        err.response?.data?.message ||
          "차량 정보를 수정하는 중 오류가 발생했습니다."
      );
      setVehicles(initialDummyData);
    } finally {
      setLoading(false);
    }
  };

  // 삭제 확인 시 (더미 데이터 사용)
  const handleConfirmDeleteDummy = () => {
    setVehicles((prevVehicles) =>
      prevVehicles.filter(
        (item) => item.vehicle_id !== selectedVehicle.vehicle_id
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
        `${BASE_URL}/admin/vehicles/${selectedVehicle.vehicle_id}`,
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
      setError(
        err.response?.data?.message || "차량을 삭제하는 중 오류가 발생했습니다."
      );
      setVehicles(initialDummyData);
    } finally {
      setLoading(false);
    }
  };

  // 신규 등록 저장 시 (더미 데이터 사용)
  const handleSaveAddDummy = () => {
    const newVehicle = {
      vehicle_id: vehicles.length + 1,
      vin: formData.vin,
      vehicle_number: formData.vehicle_number,
      current_location: { x: 0, y: 0 }, // 등록 시에는 미정으로 처리
      status: "inactive",
      mileage: Number(formData.mileage) || 0,
      last_maintenance_at: formData.last_maintenance_at,
      next_maintenance_at: formData.next_maintenance_at,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setVehicles((prev) => [...prev, newVehicle]);
    closeModal();
  };

  // 신규 등록 저장 시 (API 연동)
  const handleSaveAdd = async () => {
    if (!formData.vin.trim() || !formData.vehicle_number.trim()) {
      setError("VIN과 차량 번호는 필수 항목입니다.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const payload = {
        vin: formData.vin,
        vehicle_number: formData.vehicle_number,
      };

      const response = await axios.post(`${BASE_URL}/admin/vehicles`, payload, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        fetchVehicles();
        closeModal();
      } else {
        setError(response.data.message || "차량을 등록하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      const errorMessages = err.response?.data?.errors
        ? err.response.data.errors
            .map((error) => `${error.field}: ${error.message}`)
            .join(", ")
        : err.response?.data?.message;
      setError(errorMessages || "차량을 등록하는 중 오류가 발생했습니다.");
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
            name="item_status_name"
            value={filters.item_status_name}
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
        <p>로딩 중</p>
      ) : (
        <div className="table-wrapper">
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
                  <tr key={vehicle.vehicle_id}>
                    <td>{vehicle.vehicle_number}</td>
                    <td>{vehicle.vin}</td>
                    <td>
                      {vehicle.current_location
                        ? `x: ${vehicle.current_location.x}, y: ${vehicle.current_location.y}`
                        : "미정"}
                    </td>
                    <td>
                      <span
                        className={`status-badge ${
                          vehicle.item_status_name === "active"
                            ? "status-active"
                            : vehicle.item_status_name === "inactive"
                            ? "status-inactive"
                            : vehicle.item_status_name === "maintenance"
                            ? "status-maintenance"
                            : ""
                        }`}
                      >
                        {vehicle.item_status_name === "active"
                          ? "활성화"
                          : vehicle.item_status_name === "inactive"
                          ? "비활성화"
                          : vehicle.item_status_name === "maintenance"
                          ? "정비 중"
                          : "알 수 없음"}
                      </span>
                    </td>
                    <td>{vehicle.mileage || 0}</td>
                    <td>{vehicle.last_maintenance_at || "없음"}</td>
                    <td>{vehicle.next_maintenance_at || "없음"}</td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => handleDetailClick(vehicle)}
                      >
                        <MdSearch />
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
        </div>
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
            <p>차량번호: {selectedVehicle.vehicle_number}</p>
            <p>차대번호 (VIN): {selectedVehicle.vin}</p>
            <p>
              현재 위치:{" "}
              {selectedVehicle.current_location
                ? `x: ${selectedVehicle.current_location.x}, y: ${selectedVehicle.current_location.y}`
                : "미정"}
            </p>
            <p>
              상태:{" "}
              {selectedVehicle.item_status_name === "active"
                ? "활성화"
                : selectedVehicle.item_status_name === "inactive"
                ? "비활성화"
                : selectedVehicle.item_status_name === "maintenance"
                ? "정비 중"
                : "알 수 없음"}
            </p>
            <p>주행 거리: {selectedVehicle.mileage || 0} km</p>
            <p>
              최근 정비 일자: {selectedVehicle.last_maintenance_at || "없음"}
            </p>
            <p>
              다음 정비 일자: {selectedVehicle.next_maintenance_at || "없음"}
            </p>
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

        {modalContentType === "edit" && selectedVehicle && (
          <div className="edit-content">
            <form className="edit-form">
              <label>
                차량번호:
                <input
                  type="text"
                  name="vehicle_number"
                  value={formData.vehicle_number}
                  onChange={handleFormChange}
                />
              </label>
            </form>
            <div className="modal-actions">
              {/* 더미 데이터 수정 저장 */}
              {/* <button
                onClick={handleSaveEditDummy}
                className="save-button"
                disabled={loading}
              >
                저장
              </button> */}
              {/* API 연동 수정 저장 */}
              <button
                onClick={handleSaveEdit}
                className="save-button"
                disabled={loading}
              >
                저장
              </button>
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
              {/* <button
                onClick={handleConfirmDeleteDummy}
                className="confirm-delete-button"
                disabled={loading}
              >
                삭제
              </button> */}
              {/* API 연동 삭제 */}
              <button
                onClick={handleConfirmDelete}
                className="confirm-delete-button"
                disabled={loading}
              >
                삭제
              </button>
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
            <p>ex) vehicle_number: PBV-1234</p>
            <p>ex) vin: ABC123456789XYZ</p>
            <form className="add-form">
              <label>
                차량번호:
                <input
                  type="text"
                  name="vehicle_number"
                  value={formData.vehicle_number}
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
            </form>
            <div className="modal-actions">
              {/* 더미 데이터 신규 등록 저장 */}
              {/* <button
                onClick={handleSaveAddDummy}
                className="save-button"
                disabled={loading}
              >
                등록
              </button> */}
              {/* API 연동 신규 등록 저장 */}
              <button
                onClick={handleSaveAdd}
                className="save-button"
                disabled={loading}
              >
                등록
              </button>
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
