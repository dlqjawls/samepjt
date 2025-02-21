import React from "react"
import { createRoot } from "react-dom/client"
import "./ConfirmModal.css"

const ConfirmModal = ({ onConfirm, onCancel, isOpen }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <p>결제를 진행하시겠습니까?</p>
        <div className="modal-buttons">
          <button onClick={onConfirm}>확인</button>
          <button className="cancel" onClick={onCancel}>취소</button>
        </div>
      </div>
    </div>
  )
}

export const showConfirmModal = () => {
  return new Promise((resolve) => {
    const modalRoot = document.createElement('div');
    modalRoot.id = 'modal-root';
    document.body.appendChild(modalRoot);

    const handleConfirm = () => {
      resolve(true);
      root.unmount();
      document.body.removeChild(modalRoot);
    };

    const handleCancel = () => {
      resolve(false);
      root.unmount();
      document.body.removeChild(modalRoot);
    };

    const root = createRoot(modalRoot);
    root.render(
      <ConfirmModal
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        isOpen={true}
      />
    );
  });
}

export default ConfirmModal