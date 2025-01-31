// src/components/Modal.jsx

import React from "react";
import "./Modal.css";

function Modal({ isOpen, onClose, children }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()} // 클릭 이벤트 전파 방지
      >
        <button className="modal-close-button" onClick={onClose}>
          ✕
        </button>
        {children}
      </div>
    </div>
  );
}

export default Modal;
