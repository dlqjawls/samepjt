// src/admin/components/AddVehicleModal.jsx

import React from "react";
import "./AddModal.css";

const AddModal = ({ isOpen, onClose, onSubmit, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="add-modal-overlay" onClick={onClose}>
      <div className="add-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="add-modal-header">
          <h2>{title || "신규 차량 등록"}</h2>
        </div>
        <div className="add-modal-body">{children}</div>
        <div className="add-modal-actions">
          <button onClick={onSubmit} className="add-save-button">
            등록
          </button>
          <button onClick={onClose} className="add-cancel-button">
            취소
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddModal;
