import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import moducar_logo from "../assets/moducar_logo.svg";

const AdminLogin = () => {
  const [formData, setFormData] = useState({
    adminId: "",
    adminPassword: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await axios.post(
        "https://backend-wandering-river-6835.fly.dev/admin/login",
        formData
      );
      alert("관리자 로그인 성공!");
      console.log("관리자 로그인 성공:", response.data);
      console.log(response.data.token);
      const token = response.data.accessToken;
      localStorage.setItem("adminToken", token);
      navigate("/admin/index");
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "로그인 중 오류가 발생했습니다. 다시 시도해 주세요."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="admin-login-overlay">
      <div className="admin-login-content">
        <img src={moducar_logo} alt="" />
        <h2>
          <span className="highlight-text">관리자</span> 로그인
        </h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="adminId">아이디</label>
            <input
              id="adminId"
              name="adminId"
              type="text"
              placeholder="관리자 아이디"
              value={formData.adminId}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
          </div>
          <div>
            <label htmlFor="adminPassword">비밀번호</label>
            <input
              id="adminPassword"
              name="adminPassword"
              type="password"
              placeholder="관리자 비밀번호"
              value={formData.adminPassword}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "로그인 중..." : "로그인"}
          </button>
          <button
            type="button"
            onClick={() => (window.location.href = "/admin")}
          >
            디버깅: 관리자 페이지로 이동
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
