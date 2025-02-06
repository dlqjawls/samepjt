import "./Modal.css"

const Modal = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h2>{title}</h2>
                    <button onClick={onClose}>닫기</button>
                </div>
                <div className="modal-body">
                    {children}
                </div>
            </div>
        </div>
    )
}

export default Modal;