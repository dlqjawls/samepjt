// src/components/Modal.jsx

import React from "react";
import "./Modal.css";

function Modal({ isOpen, onClose, children, title }) {
  if (!isOpen) return null;

  return (
    <div className="admin-modal-overlay" onClick={onClose}>
      <div
        className="admin-modal-content"
        onClick={(e) => e.stopPropagation()} // 클릭 이벤트 전파 방지
      >
        <button className="admin-modal-close-button" onClick={onClose}>
          ✕
        </button>
        {title && <div className="admin-modal-header">{title}</div>}
        <div className="admin-modal-body">{children}</div>
      </div>
    </div>
  );
}

export default Modal;
