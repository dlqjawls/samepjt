// src/components/RentalRecords.jsx
import React, { useState } from "react";
import Modal from "./Modal";
import "./RentalRecords.css";

function RentalRecords() {
  const [data, setData] = useState([
    {
      rentId: 1,
      userId: "user123",
      departureLocation: "서울",
      arrivalLocation: "부산",
      rentStatus: "in_progress",
      startTime: "2024-12-01T10:00",
      endTime: "2024-11-20T16:00",
      baseCost: 100000,
      additionalCost: 20000,
      totalDistance: 400,
      statusUpdatedAt: "2024-12-01T12:00",
      createdAt: "2024-11-25T09:00",
      updatedAt: "2024-12-01T12:00",
    },
    {
      rentId: 2,
      userId: "user456",
      departureLocation: "인천",
      arrivalLocation: "대구",
      rentStatus: "completed",
      startTime: "2024-11-20T08:00",
      endTime: "2024-11-20T16:00",
      baseCost: 90000,
      additionalCost: 15000,
      totalDistance: 350,
      statusUpdatedAt: "2024-11-20T16:00",
      createdAt: "2024-11-15T10:00",
      updatedAt: "2024-11-20T16:00",
    },
  ]);

  const [selectedRow, setSelectedRow] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    userId: "",
    departureLocation: "",
    arrivalLocation: "",
    rentStatus: "reserved",
    startTime: "",
    endTime: "",
    baseCost: "",
    additionalCost: "",
    totalDistance: "",
    statusUpdatedAt: "",
    createdAt: "",
  });

  // 상세보기 클릭 시
  const handleDetailClick = (row) => {
    setSelectedRow(row);
    setIsDetailModalOpen(true);
  };

  const closeDetailModal = () => {
    setSelectedRow(null);
    setIsDetailModalOpen(false);
  };

  // 수정 클릭 시
  const handleEditClick = () => {
    setFormData({
      userId: selectedRow.userId,
      departureLocation: selectedRow.departureLocation,
      arrivalLocation: selectedRow.arrivalLocation,
      rentStatus: selectedRow.rentStatus,
      startTime: selectedRow.startTime,
      endTime: selectedRow.endTime || "",
      baseCost: selectedRow.baseCost,
      additionalCost: selectedRow.additionalCost,
      totalDistance: selectedRow.totalDistance,
      statusUpdatedAt: selectedRow.statusUpdatedAt,
      createdAt: selectedRow.createdAt,
    });
    setIsEditModalOpen(true);
  };

  const closeEditModal = () => {
    setFormData({
      userId: "",
      departureLocation: "",
      arrivalLocation: "",
      rentStatus: "reserved",
      startTime: "",
      endTime: "",
      baseCost: "",
      additionalCost: "",
      totalDistance: "",
      statusUpdatedAt: "",
      createdAt: "",
    });
    setIsEditModalOpen(false);
  };

  // 삭제 클릭 시
  const handleDeleteClick = () => {
    setIsDeleteModalOpen(true);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalOpen(false);
  };

  // 신규 등록 클릭 시
  const handleAddClick = () => {
    setFormData({
      userId: "",
      departureLocation: "",
      arrivalLocation: "",
      rentStatus: "reserved",
      startTime: "",
      endTime: "",
      baseCost: "",
      additionalCost: "",
      totalDistance: "",
      statusUpdatedAt: "",
      createdAt: "",
    });
    setIsAddModalOpen(true);
  };

  const closeAddModal = () => {
    setFormData({
      userId: "",
      departureLocation: "",
      arrivalLocation: "",
      rentStatus: "reserved",
      startTime: "",
      endTime: "",
      baseCost: "",
      additionalCost: "",
      totalDistance: "",
      statusUpdatedAt: "",
      createdAt: "",
    });
    setIsAddModalOpen(false);
  };

  // 폼 변경 시
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  // 수정 저장 시
  const handleSaveEdit = () => {
    setData((prevData) =>
      prevData.map((item) =>
        item.rentId === selectedRow.rentId
          ? {
              ...item,
              ...formData,
              baseCost: Number(formData.baseCost),
              additionalCost: Number(formData.additionalCost),
              totalDistance: Number(formData.totalDistance),
              endTime: formData.endTime || null,
              updatedAt: new Date().toISOString(),
            }
          : item
      )
    );
    closeEditModal();
    closeDetailModal();
  };

  // 삭제 확인 시
  const handleConfirmDelete = () => {
    setData((prevData) =>
      prevData.filter((item) => item.rentId !== selectedRow.rentId)
    );
    closeDeleteModal();
    closeDetailModal();
  };

  // 신규 등록 저장 시
  const handleSaveAdd = () => {
    const newRent = {
      rentId: data.length + 1,
      ...formData,
      baseCost: Number(formData.baseCost),
      additionalCost: Number(formData.additionalCost),
      totalDistance: Number(formData.totalDistance),
      endTime: formData.endTime || null,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setData((prevData) => [...prevData, newRent]);
    closeAddModal();
  };

  return (
    <div className="rental-container">
      <div className="rental-header">
        <h1>대여 기록</h1>
        <button className="add-button" onClick={handleAddClick}>
          + 신규 등록
        </button>
      </div>
      <table className="rental-table">
        <thead>
          <tr>
            {/* <th>대여 ID</th> */}
            <th>사용자 ID</th>
            <th>출발지</th>
            <th>도착지</th>
            <th>상태</th>
            <th>시작 시간</th>
            <th>종료 시간</th>
            {/* <th>기본 비용</th>
            <th>추가 비용</th>
            <th>총 거리</th> */}
            <th>상태 업데이트</th>
            <th>등록 일자</th>
            <th>상세 보기</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.rentId}>
              {/* <td>{row.rentId}</td> */}
              <td>{row.userId}</td>
              <td>{row.departureLocation}</td>
              <td>{row.arrivalLocation}</td>
              <td>
                {row.rentStatus === "reserved"
                  ? "예약됨"
                  : row.rentStatus === "in_progress"
                  ? "진행 중"
                  : row.rentStatus === "completed"
                  ? "완료됨"
                  : "취소됨"}
              </td>
              <td>{new Date(row.startTime).toLocaleString()}</td>
              <td>
                {row.endTime
                  ? new Date(row.endTime).toLocaleString()
                  : "진행 중"}
              </td>
              {/* <td>{row.baseCost.toLocaleString()}원</td>
              <td>{row.additionalCost.toLocaleString()}원</td>
              <td>{row.totalDistance} km</td> */}
              <td>{new Date(row.statusUpdatedAt).toLocaleString()}</td>
              <td>{new Date(row.createdAt).toLocaleString()}</td>
              <td>
                <button
                  className="detail-button"
                  onClick={() => handleDetailClick(row)}
                >
                  🔍 상세보기
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* 상세 정보 모달 */}
      <Modal isOpen={isDetailModalOpen} onClose={closeDetailModal}>
        {selectedRow && (
          <div className="detail-content">
            <h2>대여 상세 정보</h2>
            <p>대여 ID: {selectedRow.rentId}</p>
            <p>사용자 ID: {selectedRow.userId}</p>
            <p>출발지: {selectedRow.departureLocation}</p>
            <p>도착지: {selectedRow.arrivalLocation}</p>
            <p>
              상태:{" "}
              {selectedRow.rentStatus === "reserved"
                ? "예약됨"
                : selectedRow.rentStatus === "in_progress"
                ? "진행 중"
                : selectedRow.rentStatus === "completed"
                ? "완료됨"
                : "취소됨"}
            </p>
            <p>시작 시간: {new Date(selectedRow.startTime).toLocaleString()}</p>
            <p>
              종료 시간:{" "}
              {selectedRow.endTime
                ? new Date(selectedRow.endTime).toLocaleString()
                : "진행 중"}
            </p>
            <p>기본 비용: {selectedRow.baseCost.toLocaleString()}원</p>
            <p>추가 비용: {selectedRow.additionalCost.toLocaleString()}원</p>
            <p>총 거리: {selectedRow.totalDistance} km</p>
            <p>
              상태 업데이트:{" "}
              {new Date(selectedRow.statusUpdatedAt).toLocaleString()}
            </p>
            <p>등록 일자: {new Date(selectedRow.createdAt).toLocaleString()}</p>
            <div className="modal-actions">
              <button onClick={handleEditClick} className="edit-button">
                수정
              </button>
              <button onClick={handleDeleteClick} className="delete-button">
                삭제
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* 수정 모달 */}
      <Modal isOpen={isEditModalOpen} onClose={closeEditModal}>
        <div className="edit-content">
          <h2>대여 기록 수정</h2>
          <form className="edit-form">
            <label>
              사용자 ID:
              <input
                type="text"
                name="userId"
                value={formData.userId}
                onChange={handleFormChange}
              />
            </label>
            <label>
              출발지:
              <input
                type="text"
                name="departureLocation"
                value={formData.departureLocation}
                onChange={handleFormChange}
              />
            </label>
            <label>
              도착지:
              <input
                type="text"
                name="arrivalLocation"
                value={formData.arrivalLocation}
                onChange={handleFormChange}
              />
            </label>
            <label>
              상태:
              <select
                name="rentStatus"
                value={formData.rentStatus}
                onChange={handleFormChange}
              >
                <option value="reserved">예약됨</option>
                <option value="in_progress">진행 중</option>
                <option value="completed">완료됨</option>
                <option value="canceled">취소됨</option>
              </select>
            </label>
            <label>
              시작 시간:
              <input
                type="datetime-local"
                name="startTime"
                value={formData.startTime}
                onChange={handleFormChange}
              />
            </label>
            <label>
              종료 시간:
              <input
                type="datetime-local"
                name="endTime"
                value={formData.endTime}
                onChange={handleFormChange}
              />
            </label>
            <label>
              기본 비용 (원):
              <input
                type="number"
                name="baseCost"
                value={formData.baseCost}
                onChange={handleFormChange}
              />
            </label>
            <label>
              추가 비용 (원):
              <input
                type="number"
                name="additionalCost"
                value={formData.additionalCost}
                onChange={handleFormChange}
              />
            </label>
            <label>
              총 거리 (km):
              <input
                type="number"
                name="totalDistance"
                value={formData.totalDistance}
                onChange={handleFormChange}
              />
            </label>
            <label>
              상태 업데이트 시간:
              <input
                type="datetime-local"
                name="statusUpdatedAt"
                value={formData.statusUpdatedAt}
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
              />
            </label>
          </form>
          <div className="modal-actions">
            <button onClick={handleSaveEdit} className="save-button">
              저장
            </button>
            <button onClick={closeEditModal} className="cancel-button">
              취소
            </button>
          </div>
        </div>
      </Modal>

      {/* 삭제 확인 모달 */}
      <Modal isOpen={isDeleteModalOpen} onClose={closeDeleteModal}>
        <div className="delete-content">
          <h2>대여 기록 삭제 확인</h2>
          <p>정말로 이 대여 기록을 삭제하시겠습니까?</p>
          <div className="modal-actions">
            <button
              onClick={handleConfirmDelete}
              className="confirm-delete-button"
            >
              삭제
            </button>
            <button onClick={closeDeleteModal} className="cancel-button">
              취소
            </button>
          </div>
        </div>
      </Modal>

      {/* 신규 등록 모달 */}
      <Modal isOpen={isAddModalOpen} onClose={closeAddModal}>
        <div className="add-content">
          <h2>신규 대여 기록 등록</h2>
          <form className="add-form">
            <label>
              사용자 ID:
              <input
                type="text"
                name="userId"
                value={formData.userId}
                onChange={handleFormChange}
              />
            </label>
            <label>
              출발지:
              <input
                type="text"
                name="departureLocation"
                value={formData.departureLocation}
                onChange={handleFormChange}
              />
            </label>
            <label>
              도착지:
              <input
                type="text"
                name="arrivalLocation"
                value={formData.arrivalLocation}
                onChange={handleFormChange}
              />
            </label>
            <label>
              상태:
              <select
                name="rentStatus"
                value={formData.rentStatus}
                onChange={handleFormChange}
              >
                <option value="reserved">예약됨</option>
                <option value="in_progress">진행 중</option>
                <option value="completed">완료됨</option>
                <option value="canceled">취소됨</option>
              </select>
            </label>
            <label>
              시작 시간:
              <input
                type="datetime-local"
                name="startTime"
                value={formData.startTime}
                onChange={handleFormChange}
              />
            </label>
            <label>
              종료 시간:
              <input
                type="datetime-local"
                name="endTime"
                value={formData.endTime}
                onChange={handleFormChange}
              />
            </label>
            <label>
              기본 비용 (원):
              <input
                type="number"
                name="baseCost"
                value={formData.baseCost}
                onChange={handleFormChange}
              />
            </label>
            <label>
              추가 비용 (원):
              <input
                type="number"
                name="additionalCost"
                value={formData.additionalCost}
                onChange={handleFormChange}
              />
            </label>
            <label>
              총 거리 (km):
              <input
                type="number"
                name="totalDistance"
                value={formData.totalDistance}
                onChange={handleFormChange}
              />
            </label>
            <label>
              상태 업데이트 시간:
              <input
                type="datetime-local"
                name="statusUpdatedAt"
                value={formData.statusUpdatedAt}
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
              />
            </label>
          </form>
          <div className="modal-actions">
            <button onClick={handleSaveAdd} className="save-button">
              등록
            </button>
            <button onClick={closeAddModal} className="cancel-button">
              취소
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default RentalRecords;
