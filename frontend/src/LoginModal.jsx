import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import "./LoginModal.css"

const LoginModal = ({ onClose }) => {
  const [formData, setFormData] = useState({
    userId: "",
    userPassword: "",
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
  const navigate= useNavigate();
  const resist = ()=>{
    navigate("/RegistrationForm")
    onClose()
    
  };
  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      const response = await axios.post("https://backend-wandering-river-6835.fly.dev/user/login", formData)
      alert("로그인 성공!")
      console.log("로그인 성공:", response.data)
      console.log(response.data.token)
      const token = response.data.accessToken
      localStorage.setItem("token",token)
      onClose()
    } catch (err) {
      setError(err.response?.data?.message || "로그인 중 오류가 발생했습니다. 다시 시도해 주세요.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button onClick={onClose} className="close-button">
          ✕
        </button>

        <h2>로그인</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="userId">아이디</label>
            <input id="userId" name="userId" type="text" placeholder="아이디를 입력하세요" value={formData.userId} onChange={handleChange} required disabled={isLoading} />
          </div>

          <div>
            <label htmlFor="userPassword">비밀번호</label>
            <input id="userPassword" name="userPassword" type="password" placeholder="비밀번호를 입력하세요" value={formData.userPassword} onChange={handleChange} required disabled={isLoading} />
          </div>

          <button type="submit" disabled={isLoading}>
            {isLoading ? "로그인 중..." : "로그인"}
          </button>

          <div className="modal-regist">
            계정이 없으신가요?
            <div>
              <button onClick={resist} >회원가입 </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginModal