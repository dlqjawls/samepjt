import React from "react";
import { Link } from "react-router-dom";

function LoginModal({ onClose }) {
  return (
    <div style={modalStyle}>
      <div style={modalContentStyle}>
        <h2>로그인</h2>
        <input type="text" placeholder="아이디" style={inputStyle} />
        <input type="password" placeholder="비밀번호" style={inputStyle} />
        <button style={buttonStyle}>로그인</button>
        <p>
          계정이 없으신가요? <Link to="/signup" onClick={onClose}>회원가입</Link>
        </p>
        <button onClick={onClose} style={closeButtonStyle}>닫기</button>
      </div>
    </div>
  );
}

const modalStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  backgroundColor: "rgba(0, 0, 0, 0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
};

const modalContentStyle = {
  backgroundColor: "white",
  padding: "20px",
  borderRadius: "10px",
  textAlign: "center",
};

const inputStyle = {
  display: "block",
  width: "80%",
  margin: "10px auto",
  padding: "10px",
  borderRadius: "5px",
  border: "1px solid #ccc",
};

const buttonStyle = {
  padding: "10px 20px",
  margin: "10px",
  borderRadius: "5px",
  backgroundColor: "#007BFF",
  color: "white",
  border: "none",
  cursor: "pointer",
};

const closeButtonStyle = {
  padding: "5px 10px",
  backgroundColor: "red",
  color: "white",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
};

export default LoginModal;
