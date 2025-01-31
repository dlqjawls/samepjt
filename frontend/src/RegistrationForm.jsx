import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./RegistrationForm.css";
const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    id: "",
    password: "",
    email: "",
    name: "",
    phoneNum: "",
    address: "",
  });

  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const home = () => {
    navigate("/");
  };

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validatePhoneNum = (phoneNum) => {
    return /^\d{3}-\d{3,4}-\d{4}$/.test(phoneNum);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setApiError(null);
    setSuccessMessage("");

    // 클라이언트 측 유효성 검사
    const newErrors = {};
    if (!formData.id) newErrors.id = "아이디를 입력해주세요";
    if (!formData.password) newErrors.password = "비밀번호를 입력해주세요";
    if (!formData.email) newErrors.email = "이메일을 입력해주세요";
    else if (!validateEmail(formData.email))
      newErrors.email = "올바른 이메일 형식이 아닙니다";
    if (!formData.name) newErrors.name = "이름을 입력해주세요";
    if (!formData.phoneNum) newErrors.phoneNum = "전화번호를 입력해주세요";
    else if (!validatePhoneNum(formData.phoneNum))
      newErrors.phoneNum =
        "전화번호 형식이 올바르지 않습니다 (예: 010-1234-5678)";
    if (!formData.address) newErrors.address = "주소를 입력해주세요";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      const response = await axios.post(
        "https://backend-wandering-river-6835.fly.dev/auth/register",
        formData
      );

      if (response.data.resultCode === "SUCCESS") {
        setSuccessMessage("회원가입이 완료되었습니다.");
        setTimeout(() => {
          navigate("/login");
        }, 2000);
      }
    } catch (error) {
      if (error.response) {
        const { status, data } = error.response;
        switch (status) {
          case 400:
            setApiError(data.message || "이미 존재하는 아이디입니다.");
            break;
          case 422:
            setApiError("입력하신 정보를 다시 확인해주세요.");
            break;
          case 500:
            setApiError("서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
            break;
          default:
            setApiError("회원가입 중 오류가 발생했습니다.");
        }
      } else {
        setApiError("네트워크 연결을 확인해주세요.");
      }
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h2 className="mb-6 text-center text-2xl font-bold">회원가입</h2>
        {successMessage && (
          <div className="mb-4 rounded bg-green-100 p-3 text-green-700">
            {successMessage}
          </div>
        )}
        {apiError && (
          <div className="mb-4 rounded bg-red-100 p-3 text-red-700">
            {apiError}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="mb-2 block">아이디</label>
            <input
              type="text"
              name="id"
              value={formData.id}
              onChange={handleChange}
              className={`w-full rounded border p-2 ${
                errors.id ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.id && (
              <p className="mt-1 text-sm text-red-500">{errors.id}</p>
            )}
          </div>

          <div className="mb-4">
            <label className="mb-2 block">비밀번호</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`w-full rounded border p-2 ${
                errors.password ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-500">{errors.password}</p>
            )}
          </div>

          <div className="mb-4">
            <label className="mb-2 block">이메일</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full rounded border p-2 ${
                errors.email ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-500">{errors.email}</p>
            )}
          </div>

          <div className="mb-4">
            <label className="mb-2 block">이름</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={`w-full rounded border p-2 ${
                errors.name ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-500">{errors.name}</p>
            )}
          </div>

          <div className="mb-4">
            <label className="mb-2 block">전화번호</label>
            <input
              type="tel"
              name="phoneNum"
              value={formData.phoneNum}
              onChange={handleChange}
              placeholder="010-0000-0000"
              className={`w-full rounded border p-2 ${
                errors.phoneNum ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.phoneNum && (
              <p className="mt-1 text-sm text-red-500">{errors.phoneNum}</p>
            )}
          </div>

          <div className="mb-6">
            <label className="mb-2 block">주소</label>
            <input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleChange}
              className={`w-full rounded border p-2 ${
                errors.address ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.address && (
              <p className="mt-1 text-sm text-red-500">{errors.address}</p>
            )}
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              className="w-full rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
            >
              회원가입
            </button>
            <button
              type="button"
              onClick={home}
              className="w-full rounded bg-gray-500 px-4 py-2 text-white hover:bg-gray-600"
            >
              취소
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegistrationForm;
