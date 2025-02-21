import React from "react";
import "./SettingsModal.css";

const SettingsModal = ({ onClose }) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-button" onClick={onClose}>
          ✕
        </button>
        <h2>설정</h2>
        {/* 설정 내용 추가 */}
        <div className="settings-options">
          <p>설정 내용</p>
          {/* 예: 계정 정보와 설정 변경 */}
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
