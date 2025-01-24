// src/components/MaintenanceRecords.jsx
import React, { useState } from "react";
import Modal from "./Modal";
import "./MaintenanceRecords.css";

function MaintenanceRecords() {
  const [data, setData] = useState([
    {
      maintenanceId: 1,
      adminId: "adminMaster",
      vehicleId: 1,
      issue: "타이어 교체",
      maintenanceDate: "2024-12-10",
      cost: 50000,
      status: "completed",
      completedAt: "2024-12-15",
      notes: "모든 타이어 교체 완료",
      createdAt: "2024-12-01T09:00",
      updatedAt: "2024-12-15T10:00",
    },
    {
      maintenanceId: 2,
      adminId: "adminSemi",
      vehicleId: 2,
      issue: "엔진 오일 교환",
      maintenanceDate: "2024-11-20",
      cost: 30000,
      status: "in_progress",
      completedAt: null,
      notes: "엔진 오일 교환 중",
      createdAt: "2024-11-10T08:00",
      updatedAt: "2024-11-20T12:00",
    },
  ]);

  const [selectedRow, setSelectedRow] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    adminId: "",
    vehicleId: "",
    issue: "",
    maintenanceDate: "",
    cost: "",
    status: "pending",
    completedAt: "",
    notes: "",
    createdAt: "",
    updatedAt: "",
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
      adminId: selectedRow.adminId,
      vehicleId: selectedRow.vehicleId,
      issue: selectedRow.issue,
      maintenanceDate: selectedRow.maintenanceDate,
      cost: selectedRow.cost,
      status: selectedRow.status,
      completedAt: selectedRow.completedAt || "",
      notes: selectedRow.notes,
      createdAt: selectedRow.createdAt,
      updatedAt: selectedRow.updatedAt,
    });
    setIsEditModalOpen(true);
  };

  const closeEditModal = () => {
    setFormData({
      adminId: "",
      vehicleId: "",
      issue: "",
      maintenanceDate: "",
      cost: "",
      status: "pending",
      completedAt: "",
      notes: "",
      createdAt: "",
      updatedAt: "",
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
      adminId: "",
      vehicleId: "",
      issue: "",
      maintenanceDate: "",
      cost: "",
      status: "pending",
      completedAt: "",
      notes: "",
      createdAt: "",
      updatedAt: "",
    });
    setIsAddModalOpen(true);
  };

  const closeAddModal = () => {
    setFormData({
      adminId: "",
      vehicleId: "",
      issue: "",
      maintenanceDate: "",
      cost: "",
      status: "pending",
      completedAt: "",
      notes: "",
      createdAt: "",
      updatedAt: "",
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
        item.maintenanceId === selectedRow.maintenanceId
          ? {
              ...item,
              ...formData,
              cost: Number(formData.cost),
              completedAt: formData.completedAt || null,
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
      prevData.filter(
        (item) => item.maintenanceId !== selectedRow.maintenanceId
      )
    );
    closeDeleteModal();
    closeDetailModal();
  };

  // 신규 등록 저장 시
  const handleSaveAdd = () => {
    const newMaintenance = {
      maintenanceId: data.length + 1,
      ...formData,
      cost: Number(formData.cost),
      completedAt: formData.completedAt || null,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setData((prevData) => [...prevData, newMaintenance]);
    closeAddModal();
  };

  return (
    <div className="maintenance-container">
      <div className="maintenance-header">
        <h1>정비 기록</h1>
        <button className="add-button" onClick={handleAddClick}>
          + 신규 등록
        </button>
      </div>
      <table className="maintenance-table">
        <thead>
          <tr>
            <th>정비 ID</th>
            <th>관리자 ID</th>
            <th>차량 ID</th>
            <th>문제</th>
            <th>정비 일자</th>
            <th>비용 (원)</th>
            <th>상태</th>
            <th>완료 일자</th>
            <th>노트</th>
            <th>등록 일자</th>
            <th>수정 일자</th>
            <th>상세 보기</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.maintenanceId}>
              <td>{row.maintenanceId}</td>
              <td>{row.adminId}</td>
              <td>{row.vehicleId}</td>
              <td>{row.issue}</td>
              <td>{row.maintenanceDate}</td>
              <td>{row.cost.toLocaleString()}원</td>
              <td>
                {row.status === "pending"
                  ? "대기 중"
                  : row.status === "in_progress"
                  ? "진행 중"
                  : "완료됨"}
              </td>
              <td>{row.completedAt ? row.completedAt : "진행 중"}</td>
              <td>{row.notes}</td>
              <td>{new Date(row.createdAt).toLocaleString()}</td>
              <td>{new Date(row.updatedAt).toLocaleString()}</td>
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
            <h2>정비 상세 정보</h2>
            <p>정비 ID: {selectedRow.maintenanceId}</p>
            <p>관리자 ID: {selectedRow.adminId}</p>
            <p>차량 ID: {selectedRow.vehicleId}</p>
            <p>문제: {selectedRow.issue}</p>
            <p>정비 일자: {selectedRow.maintenanceDate}</p>
            <p>비용: {selectedRow.cost.toLocaleString()}원</p>
            <p>
              상태:{" "}
              {selectedRow.status === "pending"
                ? "대기 중"
                : selectedRow.status === "in_progress"
                ? "진행 중"
                : "완료됨"}
            </p>
            <p>완료 일자: {selectedRow.completedAt || "진행 중"}</p>
            <p>노트: {selectedRow.notes}</p>
            <p>등록 일자: {new Date(selectedRow.createdAt).toLocaleString()}</p>
            <p>수정 일자: {new Date(selectedRow.updatedAt).toLocaleString()}</p>
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
          <h2>정비 기록 수정</h2>
          <form className="edit-form">
            <label>
              관리자 ID:
              <input
                type="text"
                name="adminId"
                value={formData.adminId}
                onChange={handleFormChange}
              />
            </label>
            <label>
              차량 ID:
              <input
                type="number"
                name="vehicleId"
                value={formData.vehicleId}
                onChange={handleFormChange}
              />
            </label>
            <label>
              문제:
              <input
                type="text"
                name="issue"
                value={formData.issue}
                onChange={handleFormChange}
              />
            </label>
            <label>
              정비 일자:
              <input
                type="date"
                name="maintenanceDate"
                value={formData.maintenanceDate}
                onChange={handleFormChange}
              />
            </label>
            <label>
              비용 (원):
              <input
                type="number"
                name="cost"
                value={formData.cost}
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
                <option value="pending">대기 중</option>
                <option value="in_progress">진행 중</option>
                <option value="completed">완료됨</option>
              </select>
            </label>
            <label>
              완료 일자:
              <input
                type="date"
                name="completedAt"
                value={formData.completedAt}
                onChange={handleFormChange}
              />
            </label>
            <label>
              노트:
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleFormChange}
              ></textarea>
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
            <label>
              수정 일자:
              <input
                type="datetime-local"
                name="updatedAt"
                value={formData.updatedAt}
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
          <h2>정비 기록 삭제 확인</h2>
          <p>정말로 이 정비 기록을 삭제하시겠습니까?</p>
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
          <h2>신규 정비 기록 등록</h2>
          <form className="add-form">
            <label>
              관리자 ID:
              <input
                type="text"
                name="adminId"
                value={formData.adminId}
                onChange={handleFormChange}
              />
            </label>
            <label>
              차량 ID:
              <input
                type="number"
                name="vehicleId"
                value={formData.vehicleId}
                onChange={handleFormChange}
              />
            </label>
            <label>
              문제:
              <input
                type="text"
                name="issue"
                value={formData.issue}
                onChange={handleFormChange}
              />
            </label>
            <label>
              정비 일자:
              <input
                type="date"
                name="maintenanceDate"
                value={formData.maintenanceDate}
                onChange={handleFormChange}
              />
            </label>
            <label>
              비용 (원):
              <input
                type="number"
                name="cost"
                value={formData.cost}
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
                <option value="pending">대기 중</option>
                <option value="in_progress">진행 중</option>
                <option value="completed">완료됨</option>
              </select>
            </label>
            <label>
              완료 일자:
              <input
                type="date"
                name="completedAt"
                value={formData.completedAt}
                onChange={handleFormChange}
              />
            </label>
            <label>
              노트:
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleFormChange}
              ></textarea>
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
            <label>
              수정 일자:
              <input
                type="datetime-local"
                name="updatedAt"
                value={formData.updatedAt}
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

export default MaintenanceRecords;
