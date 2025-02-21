// src/admin/components/DeleteModal.jsx

import React from "react";
import "./DeleteModal.css";

const DeleteModal = ({ isOpen, onClose, onDelete, message, title }) => {
  if (!isOpen) return null;

  return (
    <div className="delete-modal-overlay" onClick={onClose}>
      <div
        className="delete-modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        {title && <div className="delete-modal-header">{title}</div>}
        <div className="delete-modal-body">
          <p>{message || "정말 삭제하시겠습니까?"}</p>
        </div>
        <div className="delete-modal-actions">
          <button onClick={onDelete} className="delete-delete-button">
            삭제
          </button>
          <button onClick={onClose} className="delete-cancel-button">
            취소
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteModal;
