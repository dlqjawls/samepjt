import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import "./RegistrationForm.css"
import { encryptData } from "../utils/crypto"
const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    id: "",
    password: "",
    confirmPassword: "",
    email: "",
    name: "",
    phoneNum: "",
    address: "",
  })

  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState(null)
  const [successMessage, setSuccessMessage] = useState("")
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({ ...formData, [name]: value })
  }

  const home = () => {
    navigate("/")
  }

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }

  const validatePhoneNum = (phoneNum) => {
    return /^\d{3}-\d{3,4}-\d{4}$/.test(phoneNum)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const encryptedData = {
      id: encryptData(formData.id),
      password: encryptData(formData.password),
      name: encryptData(formData.name),
      email: encryptData(formData.email),
      phone: encryptData(formData.phone),
    }
    setErrors({})
    setApiError(null)
    setSuccessMessage("")

    // 클라이언트 측 유효성 검사
    const newErrors = {}
    if (!formData.id) newErrors.id = "아이디를 입력해주세요"
    if (!formData.password) newErrors.password = "비밀번호를 입력해주세요"
    if (!formData.confirmPassword) newErrors.confirmPassword = "비밀번호 확인을 입력해주세요"
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "비밀번호가 일치하지 않습니다"
    if (!formData.email) newErrors.email = "이메일을 입력해주세요"
    else if (!validateEmail(formData.email)) newErrors.email = "올바른 이메일 형식이 아닙니다"
    if (!formData.name) newErrors.name = "이름을 입력해주세요"
    if (!formData.phoneNum) newErrors.phoneNum = "전화번호를 입력해주세요"
    else if (!validatePhoneNum(formData.phoneNum)) newErrors.phoneNum = "전화번호 형식이 올바르지 않습니다 (예: 010-1234-5678)"
    if (!formData.address) newErrors.address = "주소를 입력해주세요"

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/auth/register`,
        formData
        // encryptedData
      )

      if (response.data.resultCode === "SUCCESS") {
        setSuccessMessage("회원가입이 완료되었습니다.")
        setTimeout(() => {
          navigate("/login")
        }, 2000)
      }
    } catch (error) {
      if (error.response) {
        const { status, data } = error.response
        switch (status) {
          case 400:
            setApiError(data.message || "이미 존재하는 아이디입니다.")
            break
          case 422:
            setApiError("입력하신 정보를 다시 확인해주세요.")
            break
          case 500:
            setApiError("서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
            break
          default:
            setApiError("회원가입 중 오류가 발생했습니다.")
        }
      } else {
        setApiError("네트워크 연결을 확인해주세요.")
      }
    }
  }

  return (
    <div className="registration-container">
      <div className="registration-form">
        <h2 className="form-title">회원가입</h2>
        {successMessage && <div className="success-message">{successMessage}</div>}
        {apiError && <div className="error-message">{apiError}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>아이디</label>
            <input type="text" name="id" value={formData.id} onChange={handleChange} className={errors.id ? "input-error" : ""} />
            {errors.id && <p className="error">{errors.id}</p>}
          </div>

          <div className="form-group">
            <label>이메일</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} className={errors.email ? "input-error" : ""} />
            {errors.email && <p className="error">{errors.email}</p>}
          </div>

          <div className="form-group">
            <label>이름</label>
            <input type="text" name="name" value={formData.name} onChange={handleChange} className={errors.name ? "input-error" : ""} />
            {errors.name && <p className="error">{errors.name}</p>}
          </div>

          <div className="form-group">
            <label>전화번호</label>
            <input type="tel" name="phoneNum" value={formData.phoneNum} onChange={handleChange} className={errors.phoneNum ? "input-error" : ""} />
            {errors.phoneNum && <p className="error">{errors.phoneNum}</p>}
          </div>

          <div className="form-group">
            <label>비밀번호</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} className={errors.password ? "input-error" : ""} />
            {errors.password && <p className="error">{errors.password}</p>}
          </div>

          <div className="form-group">
            <label>비밀번호 확인</label>
            <input type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} className={errors.confirmPassword ? "input-error" : ""} />
            {errors.confirmPassword && <p className="error">{errors.confirmPassword}</p>}
          </div>

          <div className="form-group">
            <label>주소</label>
            <input type="text" name="address" value={formData.address} onChange={handleChange} className={errors.address ? "input-error" : ""} />
            {errors.address && <p className="error">{errors.address}</p>}
          </div>

          <div className="button-group">
            <button type="submit" className="rf-submit-button">
              회원가입
            </button>
            <button type="button" onClick={home} className="rf-cancel-button">
              취소
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RegistrationForm
