import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import "./LoginModal.css"

const LoginModal = ({ onClose }) => {
  const [formData, setFormData] = useState({
    id: "",
    password: "",
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }))
  }
  const navigate = useNavigate()
  const resist = () => {
    navigate("/RegistrationForm")
    onClose()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      const response = await axios.post("https://backend-wandering-river-6835.fly.dev/auth/login", formData)
      alert("로그인 성공!")
      console.log("로그인 성공:", response.data)
      console.log(response.data.data.access_token)
      const token = response.data.data.access_token
      sessionStorage.setItem("token", token)
      onClose()
    } catch (err) {
      setError(err.response?.data?.message || "로그인 중 오류가 발생했습니다. 다시 시도해 주세요.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="lm-overlay">
      <div className="lm-content">
        <button onClick={onClose} className="lm-close-button">
          ✕
        </button>

        <h2 className="lm-title">로그인</h2>

        {error && <div className="lm-error-message">{"계정을 확인해 주세요"}</div>}

        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="id" className="lm-label">아이디</label>
            <input
              id="id"
              name="id"
              type="text"
              placeholder="아이디를 입력하세요"
              value={formData.id}
              onChange={handleChange}
              required
              disabled={isLoading}
              className="lm-input"
            />
          </div>

          <div>
            <label htmlFor="userPassword" className="lm-label">비밀번호</label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={isLoading}
              className="lm-input"
            />
          </div>

          <button type="submit" disabled={isLoading} className="lm-submit-button">
            {isLoading ? "로그인 중..." : "로그인"}
          </button>

          <div className="lm-regist">
            계정이 없으신가요?
            <div>
              <button onClick={resist} className="lm-register-button">회원가입</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginModal
