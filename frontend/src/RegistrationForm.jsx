// src/components/RegistrationForm.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './RegistrationForm.css';
import { useNavigate } from 'react-router-dom';
function RegistrationForm() {
  // 폼 필드 상태 관리
  const [formData, setFormData] = useState({
    userId: '',
    userPassword: '',
    userEmail: '',
    userName: '',
    userPhoneNum: '',
    userAddress: '',
  });

  // 에러 상태 관리
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // 입력 변화 핸들러
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  // 홈 네비게이터 
  const navigate = useNavigate() ;
  const home = ()=>{
    navigate("/")
  }

  
  // 폼 제출 핸들러
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setApiError(null);
    setSuccessMessage('');

    // 클라이언트 측 유효성 검사 (간단히 예시)
    const newErrors = {};
    if (!formData.userId) newErrors.userId = 'User ID is required';
    if (!formData.userPassword) newErrors.userPassword = 'Password is required';
    if (!formData.userEmail) newErrors.userEmail = 'Email is required';
    if (!formData.userName) newErrors.userName = 'Name is required';
    if (!formData.userPhoneNum) newErrors.userPhoneNum = 'Phone number is required';
    if (!formData.userAddress) newErrors.userAddress = 'Address is required';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      // API 요청
      const response = await axios.post('https://backend-wandering-river-6835.fly.dev/user/register', formData);

      if (response.data.resultCode === 'SUCCESS') {
        setSuccessMessage(response.data.message);
        setFormData({
          userId: '',
          userPassword: '',
          userEmail: '',
          userName: '',
          userPhoneNum: '',
          userAddress: '',
        });
        alert("회원가입 성공")
        navigate("/")
      } else {
        setApiError(response.data.message);
        if (response.data.errors) {
          const apiErrors = {};
          response.data.errors.forEach((error) => {
            apiErrors[error.field] = error.message;
          });
          setErrors(apiErrors);
        }
      }
    } catch (error) {
      setApiError('An unexpected error occurred. Please try again later.');
      console.error(error);
    }
  };

  return (
    <div className="registration-form">
      <h2>User Registration</h2>
      {successMessage && <div className="success-message">{successMessage}</div>}
      {apiError && <div className="error-message">{apiError}</div>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>User ID:</label>
          <input
            type="text"
            name="userId"
            value={formData.userId}
            onChange={handleChange}
          />
          {errors.userId && <span className="error">{errors.userId}</span>}
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            name="userPassword"
            value={formData.userPassword}
            onChange={handleChange}
          />
          {errors.userPassword && <span className="error">{errors.userPassword}</span>}
        </div>
        <div>
          <label>Email:</label>
          <input
            type="email"
            name="userEmail"
            value={formData.userEmail}
            onChange={handleChange}
          />
          {errors.userEmail && <span className="error">{errors.userEmail}</span>}
        </div>
        <div>
          <label>Name:</label>
          <input
            type="text"
            name="userName"
            value={formData.userName}
            onChange={handleChange}
          />
          {errors.userName && <span className="error">{errors.userName}</span>}
        </div>
        <div>
          <label>Phone Number:</label>
          <input
            type="text"
            name="userPhoneNum"
            value={formData.userPhoneNum}
            onChange={handleChange}
          />
          {errors.userPhoneNum && <span className="error">{errors.userPhoneNum}</span>}
        </div>
        <div>
          <label>Address:</label>
          <input
            type="text"
            name="userAddress"
            value={formData.userAddress}
            onChange={handleChange}
          />
          {errors.userAddress && <span className="error">{errors.userAddress}</span>}
        </div>
        <button type="submit"  >Register</button>
        <button type="button" onClick={home}>메인페이지로</button>
      </form>
    </div>
  );
}

export default RegistrationForm;
