// src/admin/components/VehicleManagement.jsx

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import AddModal from "./AddModal";
import DeleteModal from "./DeleteModal";
import "./VehicleManagement.css";
import { MdEdit, MdDelete } from "react-icons/md";
import { FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import LoadingSpinner from "./LoadingSpinner";

const BASE_URL = import.meta.env.VITE_API_URL;

function VehicleManagement() {
  const [vehicles, setVehicles] = useState([]);
  // 확장된(토글) 행의 vehicle_id
  const [expandedVehicleId, setExpandedVehicleId] = useState(null);
  // 선택된 차량(수정/삭제 대상)
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  // 등록 및 수정 폼 데이터
  const [formData, setFormData] = useState({
    vehicle_number: "",
    vin: "",
  });

  // 등록 모달 상태
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  // 삭제 모달 상태
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  // 편집 모드 여부 (인라인 편집)
  const [editingVehicleId, setEditingVehicleId] = useState(null);

  // 필터, 페이지네이션, 로딩, 오류 상태
  const [filters, setFilters] = useState({
    item_status_name: "",
    search: "",
    page: 1,
    pageSize: 10,
  });

  // 클라이언트 페이징 계산
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 각 행의 ref들을 저장할 객체
  const rowRefs = useRef({});

  const detailInfoRef = useRef(null);

  const token = localStorage.getItem("adminToken");

  // 차량 목록 조회 API 호출
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
      } else {
        setError(
          response.data.message || "차량 목록을 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "차량 목록 조회 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 폼 입력 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    // 대문자로 변환 (VIN 같은 경우)
    const newValue = name === "vin" ? value.toUpperCase() : value;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // 토글(확장) 핸들러
  const toggleExpanded = (vehicleId) => {
    setExpandedVehicleId((prev) => (prev === vehicleId ? null : vehicleId));
    // 편집 모드 초기화
    setEditingVehicleId(null);
    setTimeout(() => {
      if (rowRefs.current[vehicleId]) {
        rowRefs.current[vehicleId].scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);
  };

  // 등록 모달 열기 및 닫기
  const openAddModal = () => {
    setFormData({ vehicle_number: "", vin: "" });
    setIsAddModalOpen(true);
  };
  const closeAddModal = () => setIsAddModalOpen(false);

  // 차량번호 형식 검증 함수: 예시로 "PBV-1234" 형식
  const validateVehicleNumber = (vehicle_number) => {
    const vehicleNumberRegex = /^PBV-\d{4}$/;
    return vehicleNumberRegex.test(vehicle_number);
  };

  // VIN 형식 검증 함수: 예시로 15자리의 영문 대문자와 숫자 (예: "ABC123456789XYZ")
  const validateVin = (vin) => {
    const vinRegex = /^[A-Z0-9]{15}$/;
    return vinRegex.test(vin);
  };

  // 신규 등록 API 호출
  const handleSubmitAdd = async () => {
    if (!formData.vehicle_number.trim() || !formData.vin.trim()) {
      alert("VIN과 차량 번호는 필수 항목입니다.");
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
        await fetchVehicles();
        closeAddModal();
      } else {
        setError(response.data.message || "차량 등록 실패");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "차량 등록 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  // 인라인 수정 모드 전환: 상세 정보 영역에서 "수정" 버튼 클릭 시 호출됨
  const startEditing = (vehicle) => {
    setSelectedVehicle(vehicle);
    setFormData({ vehicle_number: vehicle.vehicle_number, vin: vehicle.vin });
    setEditingVehicleId(vehicle.vehicle_id);
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
  const handleSubmitEdit = async (vehicleId) => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        vehicle_number: formData.vehicle_number,
      };
      const response = await axios.patch(
        `${BASE_URL}/admin/vehicles/${vehicleId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchVehicles();
        setEditingVehicleId(null);
      } else {
        setError(response.data.message || "차량 수정 실패");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "차량 수정 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  // 인라인 수정 취소
  const cancelEditing = () => {
    setEditingVehicleId(null);
  };

  // 삭제 모달 열기
  const openDeleteModal = (vehicle) => {
    setSelectedVehicle(vehicle);
    setIsDeleteModalOpen(true);
  };
  const closeDeleteModal = () => setIsDeleteModalOpen(false);

  // 삭제 API 호출
  const handleSubmitDelete = async (vehicleId) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/vehicles/${vehicleId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );
      if (response.data.resultCode === "SUCCESS") {
        await fetchVehicles();
        closeDeleteModal();
      } else {
        setError(response.data.message || "차량 삭제 실패");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "차량 삭제 중 오류 발생");
    } finally {
      setLoading(false);
    }
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  return (
    <div className="vehicle-container">
      <div className="vehicle-header">
        <h1>차량 관리</h1>
        <button className="add-button" onClick={openAddModal}>
          차량 등록
        </button>
      </div>

      {/* 필터 섹션 생략됨 */}

      {error && <p className="error">{error}</p>}
      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="table-wrapper">
          <table className="vehicle-table">
            <thead>
              <tr>
                <th>차량번호</th>
                <th>차대번호 (VIN)</th>
                <th>현재 상태</th>
                <th>주행 거리</th>
                <th>등록 일자</th>
              </tr>
            </thead>
            <tbody>
              {vehicles.length > 0 ? (
                vehicles.map((vehicle) => (
                  <React.Fragment key={vehicle.vehicle_id}>
                    <tr
                      ref={(el) => (rowRefs.current[vehicle.vehicle_id] = el)}
                      className={`main-row ${
                        expandedVehicleId === vehicle.vehicle_id
                          ? "expanded-main-row"
                          : ""
                      }`}
                      onClick={() => toggleExpanded(vehicle.vehicle_id)}
                    >
                      <td>{vehicle.vehicle_number}</td>
                      <td>
                        <span className="cell-text">{vehicle.vin}</span>
                      </td>
                      <td>
                        <span className="cell-text">
                          {vehicle.item_status_name === "active"
                            ? "활성화"
                            : vehicle.item_status_name === "inactive"
                            ? "비활성화"
                            : vehicle.item_status_name === "maintenance"
                            ? "정비 중"
                            : "알 수 없음"}
                        </span>
                      </td>
                      <td>
                        <span className="cell-text">{vehicle.mileage}</span>
                      </td>
                      <td>
                        <span className="cell-text">{vehicle.created_at}</span>
                      </td>
                    </tr>
                    {expandedVehicleId === vehicle.vehicle_id && (
                      <tr className="expanded-row">
                        <td colSpan="12">
                          <div
                            className="detail-info-container"
                            ref={detailInfoRef}
                          >
                            <div className="detail-info">
                              <div className="detail-item">
                                <div className="detail-label">차량 ID</div>
                                <div className="detail-value">
                                  {vehicle.vehicle_id}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">차량번호</div>
                                {editingVehicleId === vehicle.vehicle_id ? (
                                  <input
                                    type="text"
                                    name="vehicle_number"
                                    value={formData.vehicle_number}
                                    onChange={handleFormChange}
                                    className="edit-vehicle-number"
                                  />
                                ) : (
                                  <div className="detail-value">
                                    {vehicle.vehicle_number}
                                  </div>
                                )}
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  차대번호 (VIN)
                                </div>
                                <div className="detail-value">
                                  {vehicle.vin}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">현재 위치</div>
                                <div className="detail-value">
                                  {vehicle.current_location
                                    ? `x: ${vehicle.current_location.x}, y: ${vehicle.current_location.y}`
                                    : "미정"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">상태</div>
                                <div className="detail-value">
                                  {vehicle.item_status_name === "active"
                                    ? "활성화"
                                    : vehicle.item_status_name === "inactive"
                                    ? "비활성화"
                                    : vehicle.item_status_name === "maintenance"
                                    ? "정비 중"
                                    : "알 수 없음"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">주행 거리</div>
                                <div className="detail-value">
                                  {vehicle.mileage}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  최근 정비 일시
                                </div>
                                <div className="detail-value">
                                  {vehicle.last_maintenance_at
                                    ? vehicle.last_maintenance_at
                                    : "미정"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">
                                  다음 정비 일시
                                </div>
                                <div className="detail-value">
                                  {vehicle.next_maintenance_at
                                    ? vehicle.next_maintenance_at
                                    : "미정"}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">등록 일자</div>
                                <div className="detail-value">
                                  {vehicle.created_at}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">등록자 ID</div>
                                <div className="detail-value">
                                  {vehicle.created_by}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">수정 일자</div>
                                <div className="detail-value">
                                  {vehicle.updated_at}
                                </div>
                              </div>
                              <div className="detail-item">
                                <div className="detail-label">수정자 ID</div>
                                <div className="detail-value">
                                  {vehicle.updated_by}
                                </div>
                              </div>
                            </div>
                            <div className="detail-actions">
                              {editingVehicleId === vehicle.vehicle_id ? (
                                <>
                                  <button
                                    className="detail-save-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleSubmitEdit(vehicle.vehicle_id);
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
                                      startEditing(vehicle);
                                    }}
                                  >
                                    <MdEdit />
                                  </button>
                                  <button
                                    className="detail-delete-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      openDeleteModal(vehicle);
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
                  <td colSpan="5">등록된 차량이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

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

      <AddModal
        isOpen={isAddModalOpen}
        onClose={closeAddModal}
        onSubmit={handleSubmitAdd}
        title="신규 차량 등록"
      >
        <div className="form-group">
          <label>차량번호</label>
          <input
            type="text"
            name="vehicle_number"
            placeholder="PBV-0000"
            value={formData.vehicle_number}
            onChange={handleFormChange}
            required
          />
          {/* 차량번호 입력 검증 아이콘 및 설명 */}
          {formData.vehicle_number === "" ? (
            <div className="validation-feedback grey">
              <FaCheckCircle className="icon" />
              <span>PBV-0000 형식</span>
            </div>
          ) : validateVehicleNumber(formData.vehicle_number) ? (
            <div className="validation-feedback green">
              <FaCheckCircle className="icon" />
              <span>PBV-0000 형식</span>
            </div>
          ) : (
            <div className="validation-feedback red">
              <FaTimesCircle className="icon" />
              <span>PBV-0000 형식</span>
            </div>
          )}
        </div>
        <div className="form-group">
          <label>차대번호 (VIN)</label>
          <input
            type="text"
            name="vin"
            placeholder="ABC123456789XYZ"
            value={formData.vin}
            onChange={handleFormChange}
            required
          />
          {/* VIN 입력 검증 아이콘 및 설명 */}
          {formData.vin === "" ? (
            <div className="validation-feedback grey">
              <FaCheckCircle className="icon" />
              <span>15자리의 대문자와 숫자로 구성</span>
            </div>
          ) : validateVin(formData.vin) ? (
            <div className="validation-feedback green">
              <FaCheckCircle className="icon" />
              <span>15자리의 대문자와 숫자로 구성</span>
            </div>
          ) : (
            <div className="validation-feedback red">
              <FaTimesCircle className="icon" />
              <span>15자리의 대문자와 숫자로 구성</span>
            </div>
          )}
        </div>
      </AddModal>

      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onDelete={() => handleSubmitDelete(selectedVehicle.vehicle_id)}
        title="차량 삭제 확인"
        message={
          selectedVehicle
            ? `${selectedVehicle.vehicle_number} 차량을 삭제하시겠습니까?`
            : ""
        }
      />
    </div>
  );
}

export default VehicleManagement;
