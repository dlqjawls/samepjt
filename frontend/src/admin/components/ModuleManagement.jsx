// src/components/ModuleManagement.jsx
import React, { useState } from "react";
import Modal from "./Modal";
import "./ModuleManagement.css";

function ModuleManagement() {
  const [data, setData] = useState([
    {
      moduleId: 1,
      moduleNfcTagId: "NFC123456",
      moduleType: "센서",
      moduleSize: "Small",
      moduleCost: 30000,
      status: "active",
      lastMaintenanceAt: "2024-11-15",
      nextMaintenanceAt: "2025-02-15",
      currentLocation: "창고",
      createdAt: "2024-10-01T08:00",
      updatedAt: "2024-11-01T08:00",
    },
    {
      moduleId: 2,
      moduleNfcTagId: "NFC654321",
      moduleType: "카메라",
      moduleSize: "Large",
      moduleCost: 70000,
      status: "maintenance",
      lastMaintenanceAt: "2024-10-10",
      nextMaintenanceAt: "2025-01-10",
      currentLocation: "정비소",
      createdAt: "2024-09-20T09:00",
      updatedAt: "2024-11-05T09:00",
    },
  ]);

  const [selectedRow, setSelectedRow] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    moduleNfcTagId: "",
    moduleType: "",
    moduleSize: "",
    moduleCost: "",
    status: "active",
    lastMaintenanceAt: "",
    nextMaintenanceAt: "",
    currentLocation: "",
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
      moduleNfcTagId: selectedRow.moduleNfcTagId,
      moduleType: selectedRow.moduleType,
      moduleSize: selectedRow.moduleSize,
      moduleCost: selectedRow.moduleCost,
      status: selectedRow.status,
      lastMaintenanceAt: selectedRow.lastMaintenanceAt,
      nextMaintenanceAt: selectedRow.nextMaintenanceAt,
      currentLocation: selectedRow.currentLocation,
      createdAt: selectedRow.createdAt,
      updatedAt: selectedRow.updatedAt,
    });
    setIsEditModalOpen(true);
  };

  const closeEditModal = () => {
    setFormData({
      moduleNfcTagId: "",
      moduleType: "",
      moduleSize: "",
      moduleCost: "",
      status: "active",
      lastMaintenanceAt: "",
      nextMaintenanceAt: "",
      currentLocation: "",
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
      moduleNfcTagId: "",
      moduleType: "",
      moduleSize: "",
      moduleCost: "",
      status: "active",
      lastMaintenanceAt: "",
      nextMaintenanceAt: "",
      currentLocation: "",
      createdAt: "",
      updatedAt: "",
    });
    setIsAddModalOpen(true);
  };

  const closeAddModal = () => {
    setFormData({
      moduleNfcTagId: "",
      moduleType: "",
      moduleSize: "",
      moduleCost: "",
      status: "active",
      lastMaintenanceAt: "",
      nextMaintenanceAt: "",
      currentLocation: "",
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
        item.moduleId === selectedRow.moduleId
          ? {
              ...item,
              ...formData,
              moduleCost: Number(formData.moduleCost),
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
      prevData.filter((item) => item.moduleId !== selectedRow.moduleId)
    );
    closeDeleteModal();
    closeDetailModal();
  };

  // 신규 등록 저장 시
  const handleSaveAdd = () => {
    const newModule = {
      moduleId: data.length + 1,
      ...formData,
      moduleCost: Number(formData.moduleCost),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setData((prevData) => [...prevData, newModule]);
    closeAddModal();
  };

  return (
    <div className="module-container">
      <div className="module-header">
        <h1>모듈 관리</h1>
        <button className="add-button" onClick={handleAddClick}>
          + 신규 등록
        </button>
      </div>
      <table className="module-table">
        <thead>
          <tr>
            <th>모듈 ID</th>
            <th>NFC 태그 ID</th>
            <th>모듈 타입</th>
            <th>모듈 크기</th>
            <th>모듈 비용 (원)</th>
            <th>상태</th>
            <th>현재 위치</th>
            <th>등록 일자</th>
            <th>수정 일자</th>
            <th>상세 보기</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.moduleId}>
              <td>{row.moduleId}</td>
              <td>{row.moduleNfcTagId}</td>
              <td>{row.moduleType}</td>
              <td>{row.moduleSize}</td>
              <td>{row.moduleCost.toLocaleString()}원</td>
              <td>
                {row.status === "active"
                  ? "활성화"
                  : row.status === "inactive"
                  ? "비활성화"
                  : "정비 중"}
              </td>
              <td>{row.currentLocation}</td>
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
            <h2>모듈 상세 정보</h2>
            <p>모듈 ID: {selectedRow.moduleId}</p>
            <p>NFC 태그 ID: {selectedRow.moduleNfcTagId}</p>
            <p>모듈 타입: {selectedRow.moduleType}</p>
            <p>모듈 크기: {selectedRow.moduleSize}</p>
            <p>모듈 비용: {selectedRow.moduleCost.toLocaleString()}원</p>
            <p>
              상태:{" "}
              {selectedRow.status === "active"
                ? "활성화"
                : selectedRow.status === "inactive"
                ? "비활성화"
                : "정비 중"}
            </p>
            <p>현재 위치: {selectedRow.currentLocation}</p>
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
          <h2>모듈 수정</h2>
          <form className="edit-form">
            <label>
              NFC 태그 ID:
              <input
                type="text"
                name="moduleNfcTagId"
                value={formData.moduleNfcTagId}
                onChange={handleFormChange}
              />
            </label>
            <label>
              모듈 타입:
              <input
                type="text"
                name="moduleType"
                value={formData.moduleType}
                onChange={handleFormChange}
              />
            </label>
            <label>
              모듈 크기:
              <input
                type="text"
                name="moduleSize"
                value={formData.moduleSize}
                onChange={handleFormChange}
              />
            </label>
            <label>
              모듈 비용 (원):
              <input
                type="number"
                name="moduleCost"
                value={formData.moduleCost}
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
          <h2>모듈 삭제 확인</h2>
          <p>정말로 이 모듈을 삭제하시겠습니까?</p>
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
          <h2>신규 모듈 등록</h2>
          <form className="add-form">
            <label>
              NFC 태그 ID:
              <input
                type="text"
                name="moduleNfcTagId"
                value={formData.moduleNfcTagId}
                onChange={handleFormChange}
              />
            </label>
            <label>
              모듈 타입:
              <input
                type="text"
                name="moduleType"
                value={formData.moduleType}
                onChange={handleFormChange}
              />
            </label>
            <label>
              모듈 크기:
              <input
                type="text"
                name="moduleSize"
                value={formData.moduleSize}
                onChange={handleFormChange}
              />
            </label>
            <label>
              모듈 비용 (원):
              <input
                type="number"
                name="moduleCost"
                value={formData.moduleCost}
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

export default ModuleManagement;
