// src/components/OptionManagement.jsx
import React, { useState } from "react";
import Modal from "./Modal";
import "./OptionManagement.css";

function OptionManagement() {
  const [data, setData] = useState([
    {
      optionId: 1,
      optionTypeName: "GPS Navigation",
      optionTypeSize: "Medium",
      optionTypeCost: 50000,
      status: "active",
      createdAt: "2024-10-10T10:00",
      updatedAt: "2024-11-10T10:00",
    },
    {
      optionId: 2,
      optionTypeName: "Sunroof",
      optionTypeSize: "Large",
      optionTypeCost: 80000,
      status: "inactive",
      createdAt: "2024-09-15T09:00",
      updatedAt: "2024-10-15T09:00",
    },
  ]);

  const [selectedRow, setSelectedRow] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    optionTypeName: "",
    optionTypeSize: "",
    optionTypeCost: "",
    status: "active",
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
      optionTypeName: selectedRow.optionTypeName,
      optionTypeSize: selectedRow.optionTypeSize,
      optionTypeCost: selectedRow.optionTypeCost,
      status: selectedRow.status,
      createdAt: selectedRow.createdAt,
      updatedAt: selectedRow.updatedAt,
    });
    setIsEditModalOpen(true);
  };

  const closeEditModal = () => {
    setFormData({
      optionTypeName: "",
      optionTypeSize: "",
      optionTypeCost: "",
      status: "active",
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
      optionTypeName: "",
      optionTypeSize: "",
      optionTypeCost: "",
      status: "active",
      createdAt: "",
      updatedAt: "",
    });
    setIsAddModalOpen(true);
  };

  const closeAddModal = () => {
    setFormData({
      optionTypeName: "",
      optionTypeSize: "",
      optionTypeCost: "",
      status: "active",
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
        item.optionId === selectedRow.optionId
          ? {
              ...item,
              ...formData,
              optionTypeCost: Number(formData.optionTypeCost),
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
      prevData.filter((item) => item.optionId !== selectedRow.optionId)
    );
    closeDeleteModal();
    closeDetailModal();
  };

  // 신규 등록 저장 시
  const handleSaveAdd = () => {
    const newOption = {
      optionId: data.length + 1,
      ...formData,
      optionTypeCost: Number(formData.optionTypeCost),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setData((prevData) => [...prevData, newOption]);
    closeAddModal();
  };

  return (
    <div className="option-container">
      <div className="option-header">
        <h1>옵션 관리</h1>
        <button className="add-button" onClick={handleAddClick}>
          + 신규 등록
        </button>
      </div>
      <table className="option-table">
        <thead>
          <tr>
            <th>옵션 ID</th>
            <th>옵션 이름</th>
            <th>옵션 크기</th>
            <th>옵션 비용 (원)</th>
            <th>상태</th>
            <th>등록 일자</th>
            <th>수정 일자</th>
            <th>상세 보기</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.optionId}>
              <td>{row.optionId}</td>
              <td>{row.optionTypeName}</td>
              <td>{row.optionTypeSize}</td>
              <td>{row.optionTypeCost.toLocaleString()}원</td>
              <td>{row.status === "active" ? "활성화" : "비활성화"}</td>
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
            <h2>옵션 상세 정보</h2>
            <p>옵션 ID: {selectedRow.optionId}</p>
            <p>옵션 이름: {selectedRow.optionTypeName}</p>
            <p>옵션 크기: {selectedRow.optionTypeSize}</p>
            <p>옵션 비용: {selectedRow.optionTypeCost.toLocaleString()}원</p>
            <p>
              상태: {selectedRow.status === "active" ? "활성화" : "비활성화"}
            </p>
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
          <h2>옵션 수정</h2>
          <form className="edit-form">
            <label>
              옵션 이름:
              <input
                type="text"
                name="optionTypeName"
                value={formData.optionTypeName}
                onChange={handleFormChange}
              />
            </label>
            <label>
              옵션 크기:
              <input
                type="text"
                name="optionTypeSize"
                value={formData.optionTypeSize}
                onChange={handleFormChange}
              />
            </label>
            <label>
              옵션 비용 (원):
              <input
                type="number"
                name="optionTypeCost"
                value={formData.optionTypeCost}
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
              </select>
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
          <h2>옵션 삭제 확인</h2>
          <p>정말로 이 옵션을 삭제하시겠습니까?</p>
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
          <h2>신규 옵션 등록</h2>
          <form className="add-form">
            <label>
              옵션 이름:
              <input
                type="text"
                name="optionTypeName"
                value={formData.optionTypeName}
                onChange={handleFormChange}
              />
            </label>
            <label>
              옵션 크기:
              <input
                type="text"
                name="optionTypeSize"
                value={formData.optionTypeSize}
                onChange={handleFormChange}
              />
            </label>
            <label>
              옵션 비용 (원):
              <input
                type="number"
                name="optionTypeCost"
                value={formData.optionTypeCost}
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
              </select>
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

export default OptionManagement;
