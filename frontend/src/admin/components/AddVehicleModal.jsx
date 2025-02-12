// src/admin/components/AddVehicleModal.jsx

import React from "react";
import "./AddVehicleModal.css";

const AddVehicleModal = ({ isOpen, onClose, onSubmit, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="add-vehicle-modal-overlay" onClick={onClose}>
      <div
        className="add-vehicle-modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="add-vehicle-modal-header">
          <h2>{title || "신규 차량 등록"}</h2>
        </div>
        <div className="add-vehicle-modal-body">{children}</div>
        <div className="add-vehicle-modal-actions">
          <button onClick={onSubmit} className="add-vehicle-save-button">
            등록
          </button>
          <button onClick={onClose} className="add-vehicle-cancel-button">
            취소
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddVehicleModal;
