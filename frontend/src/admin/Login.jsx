import React, { useContext, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import moducar_logo from "../assets/moducar_logo.svg";
import { toast } from "react-toastify";
import { AdminAuthContext } from "./context/AdminAuthContext";

const AdminLogin = () => {
  const BASE_URL = import.meta.env.VITE_API_URL;

  const [formData, setFormData] = useState({
    id: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const { loginAdmin } = useContext(AdminAuthContext);
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
        `${BASE_URL}/auth/admin/login`,
        formData,
        {
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
        }
      );
      toast.success("관리자 로그인 성공");
      console.log("관리자 로그인 성공:", response.data);
      const token = response.data.data.access_token;
      const refreshToken = response.data.data.refresh_token;
      // console.log(token);
      const adminData = {
        id: formData.id,
        token: token,
        refreshToken: refreshToken,
      };
      loginAdmin(adminData);
      console.log(adminData);
      navigate("/admin/index");
    } catch (err) {
      // setError(
      //   err.response?.data?.message ||
      //     "로그인 중 오류가 발생했습니다. 다시 시도해 주세요."
      // );
      toast.error("로그인 정보가 잘못되었습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = formData.id && formData.password;

  return (
    <div className="admin-login-overlay">
      <div className="admin-login-content">
        <img src={moducar_logo} alt="Moducar 로고" />
        <h2>
          <span className="highlight-text">관리자</span> 로그인
        </h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="adminId"></label>
            <input
              id="id"
              name="id"
              type="text"
              placeholder=""
              value={formData.id}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
            <span className="floating-label">관리자 아이디</span>
          </div>
          <div className="input-group">
            <label htmlFor="password"></label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder=""
              value={formData.password}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
            <span className="floating-label">관리자 비밀번호</span>
          </div>
          <button type="submit" disabled={!isFormValid || isLoading}>
            {isLoading ? "로그인" : "로그인"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
