import React, { useState } from "react";
import "./VehicleManagement.css";

function VehicleManagement() {
  const [data, setData] = useState([
    {
      vehicleNumber: "아3123",
      chassisNumber: "1241241",
      location: "차고지",
      status: "대기 중",
      mileage: "3000km",
      lastMaintenance: "2024.12.21",
      nextMaintenance: "2025.03.01",
    },
    {
      vehicleNumber: "아3123",
      chassisNumber: "1241241",
      location: "차고지",
      status: "대기 중",
      mileage: "3000km",
      lastMaintenance: "2024.12.21",
      nextMaintenance: "2025.03.01",
    },
  ]);

  const [selectedRow, setSelectedRow] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const [formData, setFormData] = useState({
    vehicleNumber: "",
    chassisNumber: "",
    location: "",
    status: "",
    mileage: "",
    lastMaintenance: "",
    nextMaintenance: "",
  });

  const handleDetailClick = (row) => {
    setSelectedRow(row);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedRow(null);
    setIsModalOpen(false);
  };

  const handleAddModalOpen = () => {
    setIsAddModalOpen(true);
  };

  const handleAddModalClose = () => {
    setFormData({
      vehicleNumber: "",
      chassisNumber: "",
      location: "",
      status: "",
      mileage: "",
      lastMaintenance: "",
      nextMaintenance: "",
    });
    setIsAddModalOpen(false);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  const handleSaveNewVehicle = () => {
    setData((prevData) => [...prevData, formData]);
    handleAddModalClose();
  };

  return (
    <div className="table-container">
      <div className="table-header">
        <h1>차량 관리</h1>
        <button className="add-button" onClick={handleAddModalOpen}>
          + 신규 등록
        </button>
      </div>
      <table className="custom-table">
        <thead>
          <tr>
            <th>차량번호</th>
            <th>차대번호</th>
            <th>현재 위치</th>
            <th>현재 상태</th>
            <th>이동 거리</th>
            <th>최근 정비 일자</th>
            <th>다음 정비 일자</th>
            <th>상세 보기</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              <td>{row.vehicleNumber}</td>
              <td>{row.chassisNumber}</td>
              <td>{row.location}</td>
              <td>{row.status}</td>
              <td>{row.mileage}</td>
              <td>{row.lastMaintenance}</td>
              <td>{row.nextMaintenance}</td>
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
      {isModalOpen && selectedRow && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>상세 정보</h2>
            <p>차량번호: {selectedRow.vehicleNumber}</p>
            <p>차대번호: {selectedRow.chassisNumber}</p>
            <p>현재 위치: {selectedRow.location}</p>
            <p>현재 상태: {selectedRow.status}</p>
            <p>이동 거리: {selectedRow.mileage}</p>
            <p>최근 정비 일자: {selectedRow.lastMaintenance}</p>
            <p>다음 정비 일자: {selectedRow.nextMaintenance}</p>
            <button onClick={closeModal} className="close-button">
              닫기
            </button>
          </div>
        </div>
      )}

      {/* 신규 등록 모달 */}
      {isAddModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>신규 차량 등록</h2>
            <form className="add-form">
              <label>
                차량번호:
                <input
                  type="text"
                  name="vehicleNumber"
                  value={formData.vehicleNumber}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                차대번호:
                <input
                  type="text"
                  name="chassisNumber"
                  value={formData.chassisNumber}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                현재 위치:
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                현재 상태:
                <input
                  type="text"
                  name="status"
                  value={formData.status}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                이동 거리:
                <input
                  type="text"
                  name="mileage"
                  value={formData.mileage}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                최근 정비 일자:
                <input
                  type="date"
                  name="lastMaintenance"
                  value={formData.lastMaintenance}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                다음 정비 일자:
                <input
                  type="date"
                  name="nextMaintenance"
                  value={formData.nextMaintenance}
                  onChange={handleFormChange}
                />
              </label>
            </form>
            <div className="modal-actions">
              <button onClick={handleSaveNewVehicle} className="save-button">
                저장
              </button>
              <button onClick={handleAddModalClose} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VehicleManagement;
