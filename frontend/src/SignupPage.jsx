import React from "react";

function SignupPage() {
  return (
    <div style={signupStyle}>
      <h1>회원가입 페이지</h1>
      <form>
        <input type="text" placeholder="아이디" style={inputStyle} />
        <input type="email" placeholder="이메일" style={inputStyle} />
        <input type="password" placeholder="비밀번호" style={inputStyle} />
        <input type="password" placeholder="비밀번호 확인" style={inputStyle} />
        <button type="submit" style={buttonStyle}>회원가입</button>
      </form>
    </div>
  );
}

const signupStyle = {
  textAlign: "center",
  marginTop: "50px",
};

const inputStyle = {
  display: "block",
  width: "50%",
  margin: "10px auto",
  padding: "10px",
  borderRadius: "5px",
  border: "1px solid #ccc",
};

const buttonStyle = {
  padding: "10px 20px",
  backgroundColor: "#28a745",
  color: "white",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
};

export default SignupPage;
